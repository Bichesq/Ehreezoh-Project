"""
Ehreezoh - Payments API
Endpoints for initiating and managing payments
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.websocket import notify_driver, broadcast_ride_update, EventType
from app.models.user import User
from app.models.ride import Ride
from app.models.payment import Payment
from app.services.payment_service import payment_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

class PaymentInitiateRequest(BaseModel):
    ride_id: str
    payment_method: str = Field(..., description="'mtn_momo' or 'orange_money'")
    phone_number: str = Field(..., description="Payer's phone number")
    amount: Optional[float] = None  # Optional, can verify against ride fare

class PaymentResponse(BaseModel):
    id: str
    status: str
    transaction_id: Optional[str]
    message: str

@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    request: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate a payment for a ride
    """
    # 1. Validate ride
    ride = db.query(Ride).filter(Ride.id == request.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
        
    if ride.passenger_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this ride payment")
    
    # Check if already paid
    existing_payment = db.query(Payment).filter(
        Payment.ride_id == ride.id, 
        Payment.status == "completed"
    ).first()
    
    if existing_payment:
        return {
            "id": existing_payment.id,
            "status": "completed",
            "transaction_id": existing_payment.transaction_id,
            "message": "Payment already completed"
        }

    # 2. Determine amount
    amount_to_pay = request.amount or ride.final_fare or ride.estimated_fare
    if not amount_to_pay:
        raise HTTPException(status_code=400, detail="Ride fare not determined yet")

    # 3. Create Payment record
    payment = Payment(
        ride_id=ride.id,
        amount=amount_to_pay,
        currency="XAF",
        payment_method=request.payment_method,
        phone_number=request.phone_number,
        status="pending",
        platform_commission=float(amount_to_pay) * 0.15, # 15% commission
        driver_payout=float(amount_to_pay) * 0.85
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # 4. Call Payment Service
    result = await payment_service.initiate_payment(
        amount=float(amount_to_pay),
        currency="XAF",
        phone_number=request.phone_number,
        provider=request.payment_method,
        external_id=str(payment.id),
        description=f"Ride {ride.id}"
    )

    if result.get("success"):
        payment.transaction_id = result.get("transaction_id")
        payment.status = result.get("status", "pending")
        db.commit()
    else:
        payment.status = "failed"
        payment.failure_reason = result.get("message")
        db.commit()
        raise HTTPException(status_code=400, detail="Payment initiation failed")

    return {
        "id": payment.id,
        "status": payment.status,
        "transaction_id": payment.transaction_id,
        "message": "Payment initiated"
    }

@router.post("/verify/{payment_id}")
async def verify_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Manually check payment status (Polling)
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    if payment.status == "completed":
        return payment.to_dict()

    # Call service to verify
    if payment.transaction_id:
        new_status = await payment_service.verify_payment_status(payment.transaction_id)
        
        if new_status != payment.status:
            payment.status = new_status
            if new_status == "completed":
                payment.completed_at = datetime.utcnow()
                # Update ride payment status too
                if payment.ride:
                    payment.ride.payment_status = "paid"
                    
                    # Notify driver
                    if payment.ride.driver:
                        await notify_driver(
                            driver_user_id=payment.ride.driver.user_id,
                            event_type=EventType.PAYMENT_RECEIVED,
                            data={
                                "ride_id": payment.ride_id,
                                "amount": float(payment.amount),
                                "transaction_id": payment.transaction_id,
                                "timestamp": payment.completed_at.isoformat()
                            }
                        )
                    
                    # Broadcast to ride room
                    await broadcast_ride_update(
                        ride_id=payment.ride_id,
                        event_type=EventType.PAYMENT_RECEIVED,
                        ride_data={
                            "id": payment.ride_id,
                            "payment_status": "paid",
                            "amount": float(payment.amount)
                        }
                    )
            
            db.commit()
            
    return payment.to_dict()


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook for async payment notifications (Mock/Placeholder)
    """
    # In real world, verify signature here
    payload = await request.json()
    logger.info(f"Webhook received: {payload}")
    
    # Process logic would go here
    # 1. Verify signature (skipped for mock)
    # 2. Extract external_id and status
    # 3. Find payment
    # 4. Update status & notify
    
    # Mock Example Logic:
    external_id = payload.get("id")
    status = payload.get("status")
    
    if external_id and status:
         payment = db.query(Payment).filter(Payment.transaction_id == external_id).first()
         if payment and payment.status != "completed" and status == "successful":
             payment.status = "completed"
             payment.completed_at = datetime.utcnow()
             if payment.ride:
                 payment.ride.payment_status = "paid"
                 
                 # Notify driver
                 if payment.ride.driver:
                     await notify_driver(
                         driver_user_id=payment.ride.driver.user_id,
                         event_type=EventType.PAYMENT_RECEIVED,
                         data={
                             "ride_id": payment.ride_id,
                             "amount": float(payment.amount),
                             "transaction_id": payment.transaction_id,
                             "timestamp": payment.completed_at.isoformat()
                         }
                     )
                 
                 # Broadcast to ride room
                 await broadcast_ride_update(
                     ride_id=payment.ride_id,
                     event_type=EventType.PAYMENT_RECEIVED,
                     ride_data={
                         "id": payment.ride_id,
                         "payment_status": "paid",
                         "amount": float(payment.amount)
                     }
                 )
             db.commit()

    return {"status": "received"}
