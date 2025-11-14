import asyncio, json
from playwright.async_api import async_playwright
from logger import info, error

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => false});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt']});
window.chrome = { runtime: {} };
"""

async def scrape_propostas(url: str):
    info("Iniciando Playwright", url=url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117', locale='pt-BR')
        page = await context.new_page()
        await page.add_init_script(STEALTH_JS)

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        async def on_response(response):
            try:
                if '/propostas' in response.url and response.status == 200:
                    if not future.done():
                        future.set_result(response)
                        info("API /propostas detectada", url=response.url)
            except Exception as e:
                error("Erro no on_response", exception=str(e))

        page.on('response', on_response)

        await page.goto(url, wait_until='domcontentloaded')
        info("Página carregada (domcontentloaded), aguardando /propostas...")

        try:
            response = await asyncio.wait_for(future, timeout=60)
        except asyncio.TimeoutError:
            error("Timeout esperando /propostas")
            await browser.close()
            return None

        # garante corpo completo e lê como texto
        try:
            body = await response.text()
        except Exception as e:
            error("Erro ao ler body", exception=str(e))
            body = None

        await browser.close()

        if not body:
            error("Body vazio")
            return None

        try:
            data = json.loads(body)
            info("JSON decodificado", items=len(data) if isinstance(data, list) else 1)
            return data
        except Exception as e:
            error("Falha ao parsear JSON", exception=str(e))
            return None
