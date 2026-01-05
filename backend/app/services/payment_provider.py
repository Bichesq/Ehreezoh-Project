import uuid
import asyncio
import random

class PaymentProviderService:
    async def initiate_payment(self, phone_number: str, amount: float, provider: str) -> str:
        """
        Simulates initiating a payment request to MOMO or OM API.
        Returns a transaction ID.
        """
        # Simulate network delay
        await asyncio.sleep(1)
        
        # Determine success/failure randomly or via specific phone numbers for testing
        if phone_number.endswith("00"):
            raise Exception("Payment Failed: Insufficient Funds")
            
        transaction_id = f"TX-{provider.upper()}-{uuid.uuid4().hex[:8]}"
        return transaction_id

    async def check_status(self, transaction_id: str) -> str:
        """
        Simulates checking transaction status.
        """
        # For simulation, always return success
        return "success"

payment_provider = PaymentProviderService()
