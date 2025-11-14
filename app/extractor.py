import json
import time
import uuid
from seleniumbase import Driver


def log(level, message, **extra):
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": level,
        "message": message,
        "event_id": str(uuid.uuid4()),
    }
    event.update(extra)
    print(json.dumps(event, ensure_ascii=False))


def extrair_dados(url: str):
    log("INFO", "Iniciando Chrome + CDP", url=url)

    # === INICIAR CHROME COM CDP ATIVADO ===
    driver = Driver(
        browser="chrome",
        headless=True,
        undetected=True,
        agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )

    driver.open(url)

    # ATIVAR LISTEN DE REDE ANTES DE CARREGAR
    driver.execute_cdp_cmd("Network.enable", {})

    captured = []

    def capturar(request):
        try:
            req_url = request.get("request", {}).get("url", "")
            if "comprasnet-web" in req_url:
                captured.append(request)
        except Exception:
            pass

    driver.add_cdp_listener("Network.requestWillBeSent", capturar)

    log("INFO", "Aguardando chamadas de API")

    # Esperar requisições aparecerem
    time.sleep(7)

    if not captured:
        log("ERROR", "Nenhuma requisição capturada! Verifique se a página carregou totalmente")
        driver.quit()
        return None

    # === TENTAR IDENTIFICAR O ENDPOINT CERTO ===
    candidatos = [
        "propostas",
        "melhor-proposta",
        "lances",
        "melhorLance",
        "melhorOferta",
        "cotacoes",
    ]

    alvo = None
    for req in captured:
        url_req = req.get("request", {}).get("url", "")
        if any(c in url_req.lower() for c in candidatos):
            alvo = req
            break

    if not alvo:
        # DEBUG: Exibir todas as URLs encontradas
        for req in captured:
            log("INFO", "REQ DEBUG", url=req.get("request", {}).get("url", ""))

        log("ERROR", "Nenhuma rota de propostas foi encontrada")
        driver.quit()
        return None

    log("INFO", "Rota encontrada", rota=alvo["request"]["url"])

    # === OBTER RESPONSE PELO ID ===
    req_id = alvo["requestId"]

    try:
        resp = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})
        body = resp.get("body", "")
        data = json.loads(body)

    except Exception as e:
        log("ERROR", "Falha ao ler o corpo da resposta", error=str(e))
        driver.quit()
        return None

    driver.quit()
    return data
