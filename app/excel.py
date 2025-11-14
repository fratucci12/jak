from openpyxl import Workbook
from typing import List, Dict
from .logger import info, error
import os

def gerar_excel(data: List[Dict], filename: str) -> str:
    '''
    Recebe lista de propostas (list of dicts) e gera um xlsx com colunas:
    fornecedor, valor_unitario, marca, modelo
    '''
    wb = Workbook()
    ws = wb.active
    ws.title = "Propostas"
    ws.append(["fornecedor", "valor_unitario", "marca", "modelo"])

    def lookup(d, keys):
        for k in keys:
            if k in d:
                return d.get(k)
        return None

    for p in data if isinstance(data, list) else [data]:
        fornecedor = lookup(p, ["fornecedor", "razaoSocial", "proponente", "nome"])
        valor = lookup(p, ["valorUnitario", "valor_unitario", "valor", "valorUnitario"])
        marca = lookup(p, ["marca", "brand", "Marca"])
        modelo = lookup(p, ["modelo", "model", "modeloDoItem", "Model"])

        ws.append([fornecedor, valor, marca, modelo])

    caminho = os.path.join(os.getcwd(), filename)
    wb.save(caminho)
    info("Excel salvo", path=caminho, rows= len(ws['A'])-1)
    return caminho
