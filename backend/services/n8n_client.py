# backend/services/n8n_client.py
import httpx
import asyncio
from utils.logger import logger

# This will be your n8n webhook URL. We will get this from n8n in Step 4.
# Notice we removed "-test" from the URL
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/ai-ops-hub"

async def trigger_n8n_workflow(payload: dict):
    """
    Sends structured data to n8n asynchronously so it doesn't block the user's API response.
    """
    logger.info("⚙️ [n8n Client] Sending data to automation workflow...")
    
    async def send_request():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(N8N_WEBHOOK_URL, json=payload, timeout=10.0)
                response.raise_for_status()
                logger.info(f"✅ [n8n Client] Successfully triggered workflow. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ [n8n Client] Failed to trigger n8n: {str(e)}")

    # Run the request in the background
    asyncio.create_task(send_request())