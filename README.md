# JAK - Extrator de Propostas (FastAPI + Selenium)

## Como rodar localmente

1. Crie um ambiente virtual e ative:
```
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate # Unix
```

2. Instale dependências:
```
pip install -r requirements.txt
```

3. Rode o app (por padrão o scraper sobe em headless):
```
SCRAPER_HEADLESS=1 uvicorn app.main:app --reload
```

### Executar em headless/Xvfb

Alguns endpoints exigem interação com o navegador para liberar o captcha, então mantemos o Chrome em modo "headfull". Para rodar em ambientes sem display (ex.: servidor ou container), instale o `xvfb` e use o script auxiliar:

```
sudo apt install xvfb  # ou equivalente
chmod +x run_with_xvfb.sh
./run_with_xvfb.sh
```

O script inicia o `uvicorn` dentro de um servidor X virtual (`xvfb-run -screen 0 1920x1080x24`). Use a variável `PORT` para ajustar a porta exposta. Se desejar forçar o modo totalmente headless (sem Xvfb), defina `SCRAPER_HEADLESS=1` antes de rodar o servidor, sabendo que o site pode bloquear o acesso sem captcha.

## Rodando com Docker

O Dockerfile já instala o Google Chrome e todas as dependências necessárias para o Selenium rodar em modo headless. Para gerar a imagem e rodar o serviço:

```
docker build -t jak .
docker run --rm -p 8000:8000 -e SCRAPER_HEADLESS=1 jak
```

Após subir, acesse `http://localhost:8000` para usar a interface.

## Deploy no Render

- Suba este repositório no GitHub.
- Crie um novo Web Service no Render apontando para o repositório.
- Escolha `Docker` como environment.
- Após o deploy, você pode acessar a URL do serviço.
