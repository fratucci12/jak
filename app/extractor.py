import json
import os
import time
from contextlib import suppress
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import undetected_chromedriver as uc

from .logger import info, error


load_dotenv()


BASE_COMPRAS = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras"
API_PROPOSTAS = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras/{compra}/itens/{item}/propostas"
MODALIDADES = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "12",
    "20",
    "22",
    "33",
    "44",
    "57",
]


def _parse_compra_info(url: str):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    compra_raw = query.get("compra", [None])[0]
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    item = None
    if "item" in parts:
        idx = parts.index("item")
        if idx + 1 < len(parts):
            item = parts[idx + 1]
    # Para a API, precisamos usar o número completo da compra exatamente como na URL
    unidade = None  # mantido por compatibilidade, caso volte a usar no futuro
    return compra_raw, item, unidade

def _generate_captcha_token(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hcaptcha-widget-id]"))
    )
    wait.until(lambda d: d.execute_script("return typeof hcaptcha !== 'undefined'"))
    script = """
const done = arguments[0];
try {
  const el = document.querySelector('[data-hcaptcha-widget-id]');
  const widgetId = el.getAttribute('data-hcaptcha-widget-id');
  (async () => {
    try {
      const { response } = await hcaptcha.execute(widgetId, { async: true });
      done(response);
    } catch (err) {
      done(null);
    }
  })();
} catch (err) {
  done(null);
}
"""
    token = driver.execute_async_script(script)
    if not token:
        raise RuntimeError("Falha ao gerar token hCaptcha")
    info("Token capturado", token_preview=token[:40])
    return token


def _fetch_propostas(compra_id, item_id, token, cookies, timeout=30):
    if not compra_id or not item_id:
        raise ValueError("URL não contém parâmetros de compra/item válidos.")
    api_url = API_PROPOSTAS.format(compra=compra_id, item=item_id)
    session = requests.Session()
    session.cookies.update(cookies)
    headers = {
        "Origin": "https://cnetmobile.estaleiro.serpro.gov.br",
        "Referer": BASE_COMPRAS,
        "Accept": "application/json, text/plain, */*",
    }
    params = {"captcha": token}
    resp = session.get(api_url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def scrape_propostas(url: str, timeout=60):
    info("Iniciando SeleniumBase", url=url)
    driver = None

    try:
        headless = os.getenv("SCRAPER_HEADLESS", "").lower() in {"1", "true", "yes"}

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument(
            "--unsafely-treat-insecure-origin-as-secure=https://cnetmobile.estaleiro.serpro.gov.br"
        )
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            info("Rodando navegador em modo headless")
        else:
            options.add_argument("--start-maximized")

        driver = uc.Chrome(
            headless=headless,
            options=options,
            seleniumwire_options={
                "disable_encoding": False,
                "verify_ssl": False,
            },
        )

        compra_id, item_id, _ = _parse_compra_info(url)
        if not compra_id or not item_id:
            error("URL inválida para extração", url=url)
            return None

        driver.get(BASE_COMPRAS)
        try:
            token = _generate_captcha_token(driver, timeout=timeout)
            info("Token hCaptcha gerado sem preencher formulário")
        except Exception as e:
            error("Não foi possível gerar o token hCaptcha", exception=str(e))
            return None

        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        data = _fetch_propostas(compra_id, item_id, token, cookies, timeout=timeout)

        return data

    except Exception as e:
        error("Erro durante scraping", exception=str(e))
        return None
    finally:
        if driver:
            with suppress(Exception):
                driver.quit()
