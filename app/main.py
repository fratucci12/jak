from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid, os
from extractor import scrape_propostas
from excel import gerar_excel
from logger import info, error

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/processar")
async def processar(request: Request, url: str = Form(...)):
    info("Recebido request para processar", url=url)
    data = await scrape_propostas(url)
    if not data:
        error("Falha na extração", url=url)
        return {"error": "Falha ao extrair dados. Veja logs."}

    # gerar excel
    filename = f"propostas_{uuid.uuid4().hex}.xlsx"
    caminho = gerar_excel(data, filename)
    info("Excel gerado", file=caminho)
    return FileResponse(caminho, filename="resultado.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
