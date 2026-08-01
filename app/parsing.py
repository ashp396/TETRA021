import httpx
import asyncio
from app.config import settings

LLAMAPARSE_UPLOAD_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
LLAMAPARSE_RESULT_URL = "https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/text"


async def parse_document(file_path: str, filename: str) -> str:
    """
    Sends a document to LlamaParse (free tier: 1000 pages per month) and
    returns the extracted plain text. Works for PDF, PPTX, and XLSX.
    """
    if not settings.llamaparse_api_key:
        raise RuntimeError("LLAMAPARSE_API_KEY is not set. Add it to your .env file.")

    headers = {"Authorization": f"Bearer {settings.llamaparse_api_key}"}

    async with httpx.AsyncClient(timeout=120) as client:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            upload_response = await client.post(LLAMAPARSE_UPLOAD_URL, headers=headers, files=files)
        upload_response.raise_for_status()
        job_id = upload_response.json()["id"]

        for _ in range(30):
            result_response = await client.get(
                LLAMAPARSE_RESULT_URL.format(job_id=job_id), headers=headers
            )
            if result_response.status_code == 200:
                return result_response.json().get("text", "")
            await asyncio.sleep(2)

    raise TimeoutError(f"LlamaParse job {job_id} did not complete in time.")
