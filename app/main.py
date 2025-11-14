from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid, os
from fastapi.concurrency import run_in_threadpool
from .extractor import scrape_propostas
from .excel import gerar_excel
from .logger import info, error


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/processar")
async def processar(request: Request, url: str = Form(...)):
    info("Recebido request para processar", url=url)

    # 👉 roda o scraper síncrono SEGURO dentro do FastAPI
    data = await run_in_threadpool(scrape_propostas, url)

    if not data:
        error("Falha na extração", url=url)
        return {"error": "Falha ao extrair dados."}

    filename = f"propostas_{uuid.uuid4().hex}.xlsx"
    caminho = gerar_excel(data, filename)

    info("Excel gerado", file=caminho)
    return FileResponse(
        caminho,
        filename="resultado.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
