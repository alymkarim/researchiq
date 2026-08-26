from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .auth import get_current_user
from ..services.llm_service import get_available_providers

router = APIRouter(prefix="/api/llm", tags=["llm"])


class ProviderInfo(BaseModel):
    name: str
    base_url: str
    models: list[str]


class ProvidersResponse(BaseModel):
    providers: list[ProviderInfo]


@router.get("/providers", response_model=ProvidersResponse)
def list_providers(
    user=Depends(get_current_user),
):
    providers = get_available_providers()
    return ProvidersResponse(
        providers=[ProviderInfo(**p) for p in providers]
    )
