#!/usr/bin/env python3
"""Gera n8n/workflows/*.json a partir do código em n8n/src/*.js.

Uso: python3 n8n/build.py
Os .js são a fonte da verdade (testados em n8n/tests). Não edite o JSON à mão.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SRC = AQUI / "src"
OUT = AQUI / "workflows"


def js(nome: str, prefixo: str = "") -> str:
    return prefixo + (SRC / f"{nome}.js").read_text(encoding="utf-8")


class WF:
    def __init__(self, nome: str):
        self.nome = nome
        self.nodes: list[dict] = []
        self.conn: dict[str, dict] = {}
        self.x = 0

    def node(self, nome, tipo, versao, params, y=0, **extra):
        self.x += 220
        n = {"id": str(uuid.uuid5(uuid.NAMESPACE_DNS, self.nome + nome)), "name": nome,
             "type": tipo, "typeVersion": versao, "position": [self.x, y], "parameters": params}
        n.update(extra)
        self.nodes.append(n)
        return nome

    def code(self, nome, arquivo, y=0, prefixo="", **extra):
        return self.node(nome, "n8n-nodes-base.code", 2, {"jsCode": js(arquivo, prefixo)}, y, **extra)

    def liga(self, de, para, saida=0):
        main = self.conn.setdefault(de, {"main": []})["main"]
        while len(main) <= saida:
            main.append([])
        main[saida].append({"node": para, "type": "main", "index": 0})

    def cadeia(self, *nomes):
        for a, b in zip(nomes, nomes[1:]):
            self.liga(a, b)

    def salvar(self, arquivo):
        OUT.mkdir(exist_ok=True)
        dados = {"name": self.nome, "nodes": self.nodes, "connections": self.conn,
                 "settings": {"executionOrder": "v1"}, "active": False}
        (OUT / arquivo).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


SHEET_ID = {"__rl": True, "mode": "id", "value": "={{ $('Config').first().json.sheet_id }}"}


def aba(nome):
    return {"__rl": True, "mode": "name", "value": nome}


def sheets_ler(wf, nome, aba_nome, y=0):
    return wf.node(nome, "n8n-nodes-base.googleSheets", 4.5,
                   {"operation": "read", "documentId": SHEET_ID, "sheetName": aba(aba_nome), "options": {}},
                   y, executeOnce=True, alwaysOutputData=True)


def sheets_add(wf, nome, aba_nome, y=0):
    return wf.node(nome, "n8n-nodes-base.googleSheets", 4.5,
                   {"operation": "append", "documentId": SHEET_ID, "sheetName": aba(aba_nome),
                    "columns": {"mappingMode": "autoMapInputData", "value": {}},
                    "options": {"cellFormat": "RAW"}}, y)


def sheets_atualizar(wf, nome, aba_nome, y=0):
    return wf.node(nome, "n8n-nodes-base.googleSheets", 4.5,
                   {"operation": "update", "documentId": SHEET_ID, "sheetName": aba(aba_nome),
                    "columns": {"mappingMode": "autoMapInputData", "value": {},
                                "matchingColumns": ["chave"]},
                    "options": {"cellFormat": "RAW"}}, y)


def hash_tel(wf, y=0):
    return wf.node("Hash telefone", "n8n-nodes-base.crypto", 1,
                   {"action": "hash", "type": "SHA256", "value": "={{ String($json.telefone) }}",
                    "dataPropertyName": "telefone_hash"}, y)


def http_claude(wf, nome, y=0):
    return wf.node(nome, "n8n-nodes-base.httpRequest", 4.2, {
        "method": "POST", "url": "https://api.anthropic.com/v1/messages",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [{"name": "anthropic-version", "value": "2023-06-01"}]},
        "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.req) }}",
        "options": {"timeout": 60000}},
        y, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueRegularOutput")


def switch(wf, nome, expr, saidas, y=0):
    return wf.node(nome, "n8n-nodes-base.switch", 3,
                   {"mode": "expression", "numberOutputs": saidas, "output": expr}, y)


def entrada():
    wf = WF("KAUAN 01 - WhatsApp entrada (classificar e rascunhar)")
    # Verificação GET da Meta
    wf.node("Webhook GET", "n8n-nodes-base.webhook", 2,
            {"httpMethod": "GET", "path": "whatsapp", "responseMode": "responseNode", "options": {}},
            -300, webhookId=str(uuid.uuid5(uuid.NAMESPACE_DNS, "kauan-wa-get")))
    wf.code("Verificar token Meta", "verificar_meta", -300)
    wf.node("Responder verificação", "n8n-nodes-base.respondToWebhook", 1.1,
            {"respondWith": "text", "responseBody": "={{ $json.challenge }}",
             "options": {"responseCode": "={{ $json.ok ? 200 : 403 }}"}}, -300)
    wf.cadeia("Webhook GET", "Verificar token Meta", "Responder verificação")

    # Mensagens POST
    wf.x = 0
    wf.node("Webhook POST", "n8n-nodes-base.webhook", 2,
            {"httpMethod": "POST", "path": "whatsapp", "responseMode": "responseNode", "options": {}},
            webhookId=str(uuid.uuid5(uuid.NAMESPACE_DNS, "kauan-wa-post")))
    wf.node("Responder 200", "n8n-nodes-base.respondToWebhook", 1.1,
            {"respondWith": "noData", "options": {"responseCode": 200}})
    wf.code("Config", "config_entrada")
    wf.code("Extrair mensagens", "extrair")
    hash_tel(wf)
    sheets_ler(wf, "Ler Supressao", "Supressao")
    wf.code("Rotear entrada", "rotear_entrada")
    switch(wf, "Rota entrada", "={{ {ignorar:0, oposicao:1, classificar:2, humano:3}[$json.rota] }}", 4)
    wf.cadeia("Webhook POST", "Responder 200", "Config", "Extrair mensagens", "Hash telefone",
              "Ler Supressao", "Rotear entrada", "Rota entrada")

    wf.node("Ignorar (suprimido)", "n8n-nodes-base.noOp", 1, {}, -200)
    wf.liga("Rota entrada", "Ignorar (suprimido)", 0)

    x_ramo = wf.x
    wf.code("Linha supressao", "linha_supressao", -100)
    sheets_add(wf, "Gravar Supressao", "Supressao", -100)
    wf.liga("Rota entrada", "Linha supressao", 1)
    wf.liga("Linha supressao", "Gravar Supressao")

    wf.x = x_ramo
    wf.code("Montar P1", "montar_p1", 100)
    http_claude(wf, "Claude P1 classificar", 100)
    wf.code("Validar P1", "validar_p1", 100)
    switch(wf, "Rota P1", "={{ {oposicao:0, rascunho:1, humano:2}[$json.rota] }}", 3, 100)
    wf.liga("Rota entrada", "Montar P1", 2)
    wf.cadeia("Montar P1", "Claude P1 classificar", "Validar P1", "Rota P1")
    wf.liga("Rota P1", "Linha supressao", 0)

    wf.code("Montar P2", "montar_p2", 100)
    http_claude(wf, "Claude P2 rascunho", 100)
    wf.code("Linha rascunho", "linha_aprovacao", 100, prefixo="const MODO = 'p2';\n")
    wf.liga("Rota P1", "Montar P2", 1)
    wf.cadeia("Montar P2", "Claude P2 rascunho", "Linha rascunho")

    wf.code("Linha humano", "linha_aprovacao", 300, prefixo="const MODO = 'humano';\n")
    wf.liga("Rota P1", "Linha humano", 2)
    wf.liga("Rota entrada", "Linha humano", 3)

    sheets_add(wf, "Gravar Aprovacao", "Aprovacao", 200)
    wf.liga("Linha rascunho", "Gravar Aprovacao")
    wf.liga("Linha humano", "Gravar Aprovacao")
    wf.salvar("01-whatsapp-entrada.json")


def envio():
    wf = WF("KAUAN 02 - Enviar mensagens aprovadas")
    wf.node("A cada 2 min", "n8n-nodes-base.scheduleTrigger", 1.2,
            {"rule": {"interval": [{"field": "minutes", "minutesInterval": 2}]}})
    wf.code("Config", "config_envio")
    sheets_ler(wf, "Ler Aprovacao", "Aprovacao")
    hash_tel(wf)
    sheets_ler(wf, "Ler Supressao", "Supressao")
    wf.code("Selecionar envios", "selecionar_envios")
    switch(wf, "Rota envio", "={{ $json.acao === 'enviar' ? 0 : 1 }}", 2)
    wf.cadeia("A cada 2 min", "Config", "Ler Aprovacao", "Hash telefone", "Ler Supressao",
              "Selecionar envios", "Rota envio")
    wf.node("WhatsApp enviar", "n8n-nodes-base.httpRequest", 4.2, {
        "method": "POST",
        "url": "=https://graph.facebook.com/{{ $('Config').first().json.graph_versao }}/"
               "{{ $('Config').first().json.phone_number_id }}/messages",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.req) }}",
        "options": {"timeout": 30000}}, -100, onError="continueRegularOutput")
    wf.code("Resultado envio", "resultado_envio", -100)
    wf.liga("Rota envio", "WhatsApp enviar", 0)
    wf.liga("WhatsApp enviar", "Resultado envio")
    wf.node("Limpar campos", "n8n-nodes-base.code", 2,
            {"jsCode": "return $input.all().map(i => { const j = { ...i.json }; delete j.acao; "
                       "delete j.req; return { json: j }; });"}, 100)
    wf.liga("Rota envio", "Limpar campos", 1)
    sheets_atualizar(wf, "Atualizar Aprovacao", "Aprovacao")
    wf.liga("Resultado envio", "Atualizar Aprovacao")
    wf.liga("Limpar campos", "Atualizar Aprovacao")
    wf.salvar("02-enviar-aprovadas.json")


if __name__ == "__main__":
    entrada()
    envio()
    print("ok:", ", ".join(p.name for p in sorted(OUT.glob("*.json"))))
