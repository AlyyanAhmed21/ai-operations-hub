# backend/services/automation_client.py
import os
import httpx
import asyncio
from utils.logger import logger

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

async def trigger_automation_workflow(payload: dict):
    """
    Sends structured data to Make.com asynchronously.
    """
    logger.info("⚙️ [Automation Client] Sending data to Make.com...")
    
    async def send_request():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(MAKE_WEBHOOK_URL, json=payload, timeout=10.0)
                response.raise_for_status()
                logger.info(f"✅ [Automation Client] Successfully triggered workflow. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ [Automation Client] Failed to trigger Make.com: {str(e)}")

    # Run the request in the background
    asyncio.create_task(send_request())