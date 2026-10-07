from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_gemma_service import gemma_service


router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str


@router.post("/chat_gemma")
def chat(request: ChatRequest):

    result = gemma_service.generate_response(
        request.prompt
    )

    return {
        "content": result
    }