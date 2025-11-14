def gerar_excel(propostas, filename):
    from loguru import logger as log
    import os
    import openpyxl

    log.info(f"Início da geração do Excel. Recebido tipo: {type(propostas)}, quantidade: {len(propostas)}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Propostas"

    ws.append(["Fornecedor", "Valor", "Marca", "Modelo"])

    for idx, p in enumerate(propostas, 1):
        try:
            fornecedor = p.get("participante", {}).get("nome") if isinstance(p, dict) else None

            valores = p.get("valores", {}) if isinstance(p, dict) else {}
            vpil = valores.get("valorPropostaInicialOuLances", {}) if isinstance(valores, dict) else {}

            valor_informado = None
            if isinstance(vpil, dict):
                valor_informado = vpil.get("valorInformado")
            else:
                # vpil pode ser float ou outro tipo
                valor_informado = vpil

            valor_unitario = None
            if isinstance(valor_informado, dict):
                valor_unitario = valor_informado.get("valorUnitario")
            else:
                valor_unitario = valor_informado

            # Agora valor_unitario pode ser dict ou float
            valor_total = None
            if isinstance(valor_unitario, dict):
                valor_total = valor_unitario.get("valorTotal")
            else:
                valor_total = valor_unitario

            marca = p.get("marcaFabricante") if isinstance(p, dict) else None
            modelo = p.get("modeloVersao") if isinstance(p, dict) else None

            log.info(f"Item {idx}: fornecedor={fornecedor}, valor={valor_total}, marca={marca}, modelo={modelo}")

            ws.append([fornecedor, valor_total, marca, modelo])
        except Exception as e:
            log.error(f"Erro no processamento da proposta {idx}: {e}")

    caminho = os.path.abspath(f"{filename}.xlsx")
    wb.save(caminho)
    log.info(f"Excel salvo em {caminho}")
    return caminho
