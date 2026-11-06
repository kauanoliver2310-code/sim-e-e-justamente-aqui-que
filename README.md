# KAUAN AI BUSINESS — Sistema de Prospecção, Qualificação e Compliance com IA

Auditoria técnica e financeira do SOP original, mais o núcleo de regras testado.
Entrega da parte **01 · Claude** (pesquisa, arquitetura, especificação). Ver `docs/07-contrato-especialistas.md`.

## Conclusão principal
**Inverter o modelo.** O SOP original foi escrito para disparo frio em massa (minerar CNPJ → WhatsApp).
Isso é o mais caro, viola a regra de opt-in do WhatsApp, e a Evolution API arrisca banir o número
que fecha as vendas. A automação deve servir o **inbound dos vídeos** (resposta rápida, qualificação,
link certo, acompanhamento) e a prospecção ativa vira canal secundário por e-mail, com LGPD.

## O que foi pesquisado, calculado e testado

| Tipo | Item | Onde |
|---|---|---|
| Pesquisado | Preços e limites (WhatsApp, Resend, LLMs, BrasilAPI, IBAMA, MTE), com status de verificação | `docs/02-pesquisa-fontes.md` |
| Auditado | SOP original (13 problemas) e material do ChatGPT (1 erro de soma, 1 afirmação não confirmada) | `docs/01-diagnostico.md` |
| Calculado | Custos em 3 cenários × 5 volumes, R$/lead, R$/reunião, ponto de equilíbrio | `relatorios/simulacao_custos.md` |
| Implementado | Validação de CNPJ (incluindo alfanumérico), motor de compliance, cadastro com LGPD, outbox idempotente, agenda, validação da saída da IA | `src/kauan_ai/` |
| Testado | **57 testes automatizados passando** | `tests/` |
| **Não** testado | Integrações reais (n8n, Meta, BrasilAPI ao vivo, Calendar): nenhuma chamada externa foi feita | Fase 1 do plano |

## Como rodar
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v   # testes
python3 scripts/simular_custos.py                          # gera relatorios/simulacao_custos.{md,csv}
```
Para mudar uma premissa (preço, câmbio, taxa de resposta): edite `config/premissas.json` e rode de novo.

Ponto de equilíbrio com a comissão real do programa de indicação:
```bash
PYTHONPATH=src python3 -c "
from kauan_ai.custos import *
d = carregar_premissas('config/premissas.json')
r = calcular(500, d['cenarios']['intermediario'], orcamento_brl=250)
print(ponto_de_equilibrio(r, comissao_por_venda_brl=COLOQUE_AQUI, taxa_fechamento_reuniao=0.3))"
```

## Estrutura
```
config/premissas.json      premissas com status (OFICIAL / TERCEIROS / HIPÓTESE)
src/kauan_ai/              regras determinísticas (sem dependências externas)
tests/                     unittest (stdlib)
scripts/simular_custos.py  gera o relatório financeiro
sql/schema.sql             banco da fase 2
docs/01..07                diagnóstico, pesquisa, arquitetura, SOP v2, prompts, plano, contrato
```

## Garantias de segurança no código
- Nenhum envio real: o `EnviadorSimulado` é o padrão.
- Mensagem sem aprovação humana não sai (`PermissionError`).
- Fonte fora do ar ou desatualizada ⇒ `PENDENTE`, nunca `APTO`.
- Homônimo nunca vira restrição.
- Oposição elimina os dados e bloqueia contato futuro.
