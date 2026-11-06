# 07 — Contrato entre os 4 especialistas

Fonte única de verdade: **este repositório**. Requisitos, estados e nomes abaixo valem para todos.
Ninguém declara nada "concluído" sem a evidência pedida.

## Vocabulário comum (não traduzir nem renomear)
- Pareceres: `APTO`, `PENDENTE`, `REVISAO_HUMANA`, `RESTRICAO_A_CONFIRMAR`, `INAPTO_CADASTRAL`
- Mensagem: `RASCUNHO`, `APROVADA`, `ENVIADA`, `BLOQUEADA`, `FALHA`
- Classificação: `OK`, `REVISAO_HUMANA`, `REGISTRAR_OPOSICAO`, `FALHA_CLASSIFICACAO`
- Agenda: `SOLICITADO`, `CONFIRMADO`, `FALHA`, `ESCALADO_HUMANO`
- Chave de idempotência: `sha256(cnpj|canal|campanha|etapa)[:32]`

## 01 · Claude — pesquisa, arquitetura, especificação ✅ entregue nesta rodada
| Entrega | Evidência |
|---|---|
| Diagnóstico, pesquisa, arquitetura, SOP, prompts, plano | `docs/01..07` |
| Modelo de custos | `src/kauan_ai/custos.py`, `relatorios/simulacao_custos.md` |
| Regras determinísticas | `src/kauan_ai/*.py` |
| Testes | `python3 -m unittest` → 57 testes OK (rodado em 06/11/2026) |

## 02 · n8n — fluxos e testes
**Deve entregar:** export JSON de cada workflow em `n8n/` e o print/log de execução de cada cenário:

| # | Cenário | Resultado esperado |
|---|---|---|
| 1 | CNPJ inválido | Não cria lead; registra erro |
| 2 | CNPJ duplicado (máscara diferente) | Atualiza; não duplica |
| 3 | Empresa BAIXADA | `INAPTO_CADASTRAL` |
| 4 | BrasilAPI fora do ar (simular URL errada) | `PENDENTE` + fila de reprocessamento |
| 5 | Dados incompletos | `PENDENTE` |
| 6 | Base desatualizada | `PENDENTE` |
| 7 | IA devolve texto não-JSON | `FALHA_CLASSIFICACAO`, sem resposta automática |
| 8 | Mesmo webhook recebido 2× | 1 rascunho só |
| 9 | Falha ao criar evento | Retentativa → `ESCALADO_HUMANO` |
| 10 | Reprocessar fila | Nada é reenviado em duplicidade |
| 11 | Cliente escreve "SAIR" | Oposição registrada; nenhuma mensagem de oferta depois |

Todos com **envio simulado** (nó de envio desativado ou apontando para um webhook de teste).

## 03 · ChatGPT — auditoria independente
**Deve entregar:** `relatorios/auditoria-chatgpt.md` com:
1. Conferência de `config/premissas.json` com link oficial de cada preço (itens pendentes em `docs/02`).
2. Reexecução de `scripts/simular_custos.py` e comparação com o próprio cálculo dele (**incluindo a correção da linha de 5.000 leads**).
3. Link exato da "API IBAMA de embargos" citada, ou a retratação.
4. Teste de qualidade do P1 em 50 mensagens reais/anonimizadas: % de JSON válido e % de acerto da intenção.
5. Lista de discordâncias com a arquitetura, com justificativa.

## 04 · GitHub — código, versão, testes
**Já ativo:** CI em `.github/workflows/testes.yml` roda os testes em todo push.
**Próximo:** proteção de branch `main` (PR obrigatório + CI verde), `n8n/` versionado, segredos só em *GitHub Secrets* e nas credentials do n8n, nunca em arquivo.

## Relatório Mestre de Validação
Montado depois que os 4 entregarem: `relatorios/RELATORIO-MESTRE.md`, com uma linha por requisito:
**Pesquisado / Calculado / Implementado / Testado / Evidência / Status**.
