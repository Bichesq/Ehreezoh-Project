import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

EXPO_PUSH_API_URL = "https://exp.host/--/api/v2/push/send"

class NotificationService:
    @staticmethod
    async def send_push_notification(
        to: str | List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        sound: str = "default"
    ):
        """
        Send push notification using Expo Push API.
        'to' can be a single token string or a list of token strings.
        """
        if not to:
            logger.warning("No device tokens provided for push notification")
            return

        # Prepare messages
        # If 'to' is a list, we can bundle them or send individually. 
        # Expo supports batching.
        
        messages = []
        if isinstance(to, str):
            messages.append({
                "to": to,
                "title": title,
                "body": body,
                "data": data or {},
                "sound": sound
            })
        else:
            # If list, create message for each or grouping logic
            # Simplest for now: create one message object per user or use 'to' array if content is same
            if len(to) > 100:
                 # TODO: batching logic for > 100
                 logger.warning("Sending to > 100 users, explicit batching recommended but not implemented.")
            
            messages.append({
                "to": to, # Expo accepts array of tokens
                "title": title,
                "body": body,
                "data": data or {},
                "sound": sound
            })

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    EXPO_PUSH_API_URL, 
                    json=messages, 
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"Push notification sent: {response.json()}")
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to send push notification: {e}")
                if hasattr(e, 'response'): 
                     logger.error(f"Response: {e.response.text}")
                return None

notification_service = NotificationService()
