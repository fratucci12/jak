# JAK - Extrator de Propostas (FastAPI + Playwright)

Estrutura mínima para rodar no Render (Docker).

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
playwright install
```

3. Rode o app:
```
uvicorn app.main:app --reload
```

## Deploy no Render

- Suba este repositório no GitHub.
- Crie um novo Web Service no Render apontando para o repositório.
- Escolha `Docker` como environment.
- Após o deploy, você pode acessar a URL do serviço.

