# Simulação de custos — gerada por código

Premissas: `config/premissas.json` (data de referência 2026-11-06). Orçamento de caixa: R$ 250,00/mês.

> ESTIMATIVA, não cotação. Ver status de cada premissa no JSON. 'Caixa' = dinheiro que sai; 'Econômico' = caixa + horas de manutenção.

## Cenário conservador

| Leads/mês | IA | E-mail | WhatsApp | Fixo | **Caixa** | Econômico | Reuniões | R$/lead | R$/reunião | ≤ orçamento |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 100 | R$ 8,40 | R$ 0,00 | R$ 20,00 | R$ 63,50 | **R$ 91,90** | R$ 331,90 | 0.4 | R$ 0,92 | R$ 204,22 | sim |
| 500 | R$ 42,00 | R$ 0,00 | R$ 100,00 | R$ 63,50 | **R$ 205,50** | R$ 445,50 | 2.2 | R$ 0,41 | R$ 91,33 | sim |
| 1000 | R$ 84,00 | R$ 0,00 | R$ 200,00 | R$ 63,50 | **R$ 347,50** | R$ 587,50 | 4.5 | R$ 0,35 | R$ 77,22 | NÃO |
| 3000 | R$ 252,00 | R$ 120,00 | R$ 600,00 | R$ 63,50 | **R$ 1.035,50** | R$ 1.275,50 | 13.5 | R$ 0,35 | R$ 76,70 | NÃO |
| 5000 | R$ 420,00 | R$ 120,00 | R$ 1.000,00 | R$ 63,50 | **R$ 1.603,50** | R$ 1.843,50 | 22.5 | R$ 0,32 | R$ 71,27 | NÃO |

Alertas:
- 100 leads: Menos de 1 reunião esperada no mês: volume baixo demais para medir
- 1000 leads: Custo de caixa R$ 347.50 acima do orçamento R$ 250.00
- 1000 leads: WhatsApp marketing é mais da metade do custo
- 3000 leads: E-mail excede faixa grátis (diário): plano pago necessário
- 3000 leads: Custo de caixa R$ 1035.50 acima do orçamento R$ 250.00
- 3000 leads: WhatsApp marketing é mais da metade do custo
- 5000 leads: E-mail excede faixa grátis (mensal): plano pago necessário
- 5000 leads: Custo de caixa R$ 1603.50 acima do orçamento R$ 250.00
- 5000 leads: WhatsApp marketing é mais da metade do custo

## Cenário intermediario

| Leads/mês | IA | E-mail | WhatsApp | Fixo | **Caixa** | Econômico | Reuniões | R$/lead | R$/reunião | ≤ orçamento |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 100 | R$ 0,33 | R$ 0,00 | R$ 5,79 | R$ 43,50 | **R$ 49,62** | R$ 229,62 | 1.2 | R$ 0,50 | R$ 41,35 | sim |
| 500 | R$ 1,65 | R$ 0,00 | R$ 28,95 | R$ 43,50 | **R$ 74,10** | R$ 254,10 | 6.0 | R$ 0,15 | R$ 12,35 | sim |
| 1000 | R$ 3,30 | R$ 0,00 | R$ 57,91 | R$ 43,50 | **R$ 104,71** | R$ 284,71 | 12.0 | R$ 0,10 | R$ 8,73 | sim |
| 3000 | R$ 9,90 | R$ 110,00 | R$ 173,72 | R$ 43,50 | **R$ 337,12** | R$ 517,12 | 36.0 | R$ 0,11 | R$ 9,36 | NÃO |
| 5000 | R$ 16,50 | R$ 110,00 | R$ 289,53 | R$ 43,50 | **R$ 459,53** | R$ 639,53 | 60.0 | R$ 0,09 | R$ 7,66 | NÃO |

Alertas:
- 1000 leads: WhatsApp marketing é mais da metade do custo
- 3000 leads: E-mail excede faixa grátis (mensal): plano pago necessário
- 3000 leads: Custo de caixa R$ 337.12 acima do orçamento R$ 250.00
- 3000 leads: WhatsApp marketing é mais da metade do custo
- 5000 leads: E-mail excede faixa grátis (mensal): plano pago necessário
- 5000 leads: Custo de caixa R$ 459.53 acima do orçamento R$ 250.00
- 5000 leads: WhatsApp marketing é mais da metade do custo

## Cenário otimista

| Leads/mês | IA | E-mail | WhatsApp | Fixo | **Caixa** | Econômico | Reuniões | R$/lead | R$/reunião | ≤ orçamento |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 100 | R$ 0,12 | R$ 0,00 | R$ 2,10 | R$ 33,50 | **R$ 35,72** | R$ 155,72 | 2.8 | R$ 0,36 | R$ 12,76 | sim |
| 500 | R$ 0,59 | R$ 0,00 | R$ 10,50 | R$ 33,50 | **R$ 44,59** | R$ 164,59 | 14.0 | R$ 0,09 | R$ 3,18 | sim |
| 1000 | R$ 1,17 | R$ 0,00 | R$ 21,00 | R$ 33,50 | **R$ 55,67** | R$ 175,67 | 28.0 | R$ 0,06 | R$ 1,99 | sim |
| 3000 | R$ 3,51 | R$ 104,00 | R$ 63,00 | R$ 33,50 | **R$ 204,01** | R$ 324,01 | 84.0 | R$ 0,07 | R$ 2,43 | sim |
| 5000 | R$ 5,85 | R$ 104,00 | R$ 105,00 | R$ 33,50 | **R$ 248,35** | R$ 368,35 | 140.0 | R$ 0,05 | R$ 1,77 | sim |

Alertas:
- 3000 leads: E-mail excede faixa grátis (mensal): plano pago necessário
- 5000 leads: E-mail excede faixa grátis (mensal): plano pago necessário

## Conferência da tabela do ChatGPT (mesmas premissas dele)

| Leads | IA | WhatsApp | Total |
|---:|---:|---:|---:|
| 100 | R$ 0,28 | R$ 32,17 | R$ 62,45 |
| 500 | R$ 1,38 | R$ 160,85 | R$ 192,22 |
| 1000 | R$ 2,75 | R$ 321,70 | R$ 354,45 |
| 3000 | R$ 8,25 | R$ 965,10 | R$ 1.003,35 |
| 5000 | R$ 13,75 | R$ 1.608,50 | R$ 1.652,25 |

Resultado: 4 de 5 linhas conferem. **A linha de 5.000 leads do ChatGPT está errada**: ele publicou R$ 1.762,25; o correto é 30 + 13,75 + 1.608,50 = R$ 1.652,25 (erro de soma de R$ 110). Fora isso, o problema não é a conta, são as premissas: WhatsApp de marketing para 100% dos leads, hospedagem de R$ 30 não cotada, preço do WhatsApp não confirmado no rate card oficial, nenhum custo de manutenção e nenhum custo por reunião.
