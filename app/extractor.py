import json
import os
import time
from seleniumbase import Driver
from .logger import info, error


def scrape_propostas(url: str, timeout=60):
    info("Iniciando SeleniumBase", url=url)

    try:
        driver = Driver(
            browser="chrome",
            uc=True,          # undetected-chromedriver
            headless=False,    # rode headless se quiser
        )

        driver.get(url)
        time.sleep(3)

        end_time = time.time() + timeout
        while time.time() < end_time:
            html = driver.page_source
            if "/propostas" in html:
                info("/propostas detectado no HTML")
                break
            time.sleep(1)
        else:
            error("Timeout esperando /propostas")
            driver.quit()
            return None

        body = driver.find_element("tag name", "body").text

        driver.quit()

        try:
            data = json.loads(body)
        except Exception as e:
            error("Falha ao parsear JSON", exception=str(e))
            return None

        filename = "propostas_extraidas.json"
        caminho = os.path.join(os.getcwd(), filename)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        info("JSON salvo", path=caminho)
        return data

    except Exception as e:
        error("Erro durante scraping", exception=str(e))
        return None
