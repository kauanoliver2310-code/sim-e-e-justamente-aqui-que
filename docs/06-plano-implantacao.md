# 06 — Plano de implantação por etapas

Cada fase só começa quando a anterior tem **evidência** (não só documento).

## Fase 0 — Validar sem gastar (semana 1) · custo: R$ 0
- [ ] Ler o **regulamento** de cada programa de indicação (comissão, regras de divulgação, uso de marca na roupa e nos vídeos, proibição de spam).
- [ ] Preencher a `comissao_por_venda_brl` real e rodar `ponto_de_equilibrio` (ver `README.md`).
- [ ] Publicar vídeos e atender o WhatsApp **manualmente** com os prompts P1/P2 colados no Claude.
- [ ] Anotar numa planilha: lead, origem, tempo de resposta, resultado.
- **Critério para avançar:** 20 conversas inbound/semana **ou** o atendimento manual passando de 1h/dia.

## Fase 1 — MVP inbound (semanas 2–4) · custo estimado: R$ 40–65/mês
- [ ] Cotar o VPS (2 GB de RAM) e instalar o n8n Community. *Autorização do Kauan para contratar.*
- [ ] Criar a conta no WhatsApp Business Platform (Cloud API) com número dedicado. *Autorização do Kauan.*
- [ ] Fluxo n8n: webhook → BrasilAPI → P1 → validação → P2 → Sheets "Aprovação" → envio após aprovação.
- [ ] Portar as regras de `cnpj.py`, `classificacao.py` e a supressão para nós Code (JS) **ou** subir o serviço Python.
- [ ] Testes do n8n (ver `07-contrato-especialistas.md`): os 11 cenários com evidência (print/execução).
- **Critério para avançar:** 2 semanas sem mensagem duplicada, 100% das oposições atendidas, custo real ≤ previsto.

## Fase 2 — Canal ativo controlado (mês 2) · custo estimado: + R$ 0–20/mês
- [ ] Redigir e guardar a LIA (legítimo interesse).
- [ ] Baixar os Dados Abertos CNPJ, filtrar CNAE + município de atuação, até 100 empresas por semana.
- [ ] Lista Suja: baixar o arquivo e comparar por CNPJ; registrar a data da base.
- [ ] E-mail via Resend (domínio próprio, SPF/DKIM), P3, no máximo 100/dia.
- [ ] Migrar Sheets → PostgreSQL (`sql/schema.sql`).

## Fase 3 — Escala (mês 3+)
Só com custo por venda medido e positivo. Avaliar: mais regiões, follow-up automático aprovado em lote, Batch API para classificação.

## Monitoramento mensal (todo dia 5)
| Item | Onde conferir | Responsável |
|---|---|---|
| Rate card WhatsApp Brasil | developers.facebook.com/docs/whatsapp/pricing | ChatGPT |
| Preço dos LLMs | páginas oficiais Anthropic / OpenAI / Google | Claude + ChatGPT |
| Plano grátis do Resend | resend.com/pricing | ChatGPT |
| BrasilAPI no ar e com o mesmo formato | teste automatizado de contrato | GitHub (CI) |
| Lista Suja (abr/out) | gov.br/trabalho | Kauan |
| Regulamento dos programas de indicação | site de cada parceiro | Kauan |
| Atualizar `config/premissas.json` e rodar a simulação | este repositório | Claude |

## O que NÃO será feito sem autorização expressa do Kauan
Contratar VPS/serviço · comprar créditos · enviar mensagens reais · criar conta na Meta · alterar contas existentes.
