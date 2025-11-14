import anyio
from fastapi import APIRouter
from app.extractor import extrair_dados

router = APIRouter()


@router.get("/extrair")
async def extrair(url: str):
    # Roda o Selenium EM OUTRA THREAD
    data = await anyio.to_thread.run_sync(extrair_dados, url)

    if data is None:
        return {"erro": "Falha ao extrair dados"}

    return data
