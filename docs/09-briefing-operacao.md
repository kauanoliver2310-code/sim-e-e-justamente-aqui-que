# 09 — Briefing da operação comercial (aprovado em 06/11/2026)

Planilha oficial: KAUAN AI BUSINESS – Controle Central (Planilha Google, aba **Leads**).
Regras gerais: **nenhum contato externo automático**, nenhuma compra (nem estoque de maquininhas), nenhum disparo. Kauan aprova e faz todo contato.

## Classificação (todas as frentes)
| Classe | Significado |
|---|---|
| A | Oportunidade concreta: abertura, expansão ou mudança operacional **próxima**, com momento comercial relevante. Não é necessidade comprovada. |
| B | Perfil compatível: empresa real, em operação, com pagamento presencial, sem sinal específico de contratação ou troca. |
| C | Baixa prioridade: informação insuficiente, empresa grande demais ou oportunidade pouco clara. |

Campo obrigatório: **Necessidade de pagamento confirmada?** = Sim / Não / Desconhecida (coluna AM).
Fato e hipótese sempre separados. Fonte com link e data. Lote com no máximo 5 leads; entregar menos se não houver qualidade.

## Frente 1 — Varredura semanal de inaugurações · Claude
- Bairros: Copacabana, Ipanema, Leme (depois Leblon e Botafogo).
- Fontes: notícias locais (Diário do Rio, Time Out, Veja Rio, Informa Rio), páginas oficiais dos negócios.
- Prioridade: aberturas previstas para os próximos 30–60 dias; novas unidades de pequenos negócios.
- **Conferir a data da publicação na própria página** (o piloto pegou uma matéria de 2021 que a busca deu como recente).
- Dedup: nome comercial + endereço contra toda a aba Leads.
- Entrega: linhas novas na aba Leads (lote "Semanal Claude dd/mm") + resumo para revisão.
- Status: **teste manual primeiro**; o agendamento só acontece após a aprovação do Kauan.

## Frente 2 — CNPJs novos, mensal · Claude (código/GitHub)
- Fonte: Dados Abertos CNPJ da Receita Federal.
- Filtros: abertura nos últimos 60 dias, situação ATIVA, CEPs dos bairros, CNAE de venda presencial (alimentação, beleza, varejo, serviços).
- Saída: lista para investigação, **nunca classe A automática** (abrir CNPJ não prova que já vende).
- Status: **teste manual de 1 mês** antes de automatizar no GitHub Actions (verificar tamanho da base e limites gratuitos).
- LGPD: MEI e empresário individual = pessoa física; registrar só dados comerciais.

## Frente 3 — Campanha de Réveillon · Kauan + Zapia (conteúdo), ChatGPT (validação)
- Ângulo: "Vai receber clientes no Réveillon? Prepare sua operação de pagamentos antes da alta temporada."
- Público, por prioridade: (1) quiosques e bares da orla; (2) pequenos negócios de alimentação formalizados; (3) ambulantes **credenciados** (condicionado à verificação).
- Fora de escopo: abordagem indiscriminada de ambulantes; promessa de condição sazonal não confirmada.
- Regras 2026/27 **ainda não publicadas**: não reaproveitar prazos de 2025/26.
- Programa: Convide e Ganhe (sem estoque). Revendedores = exige compra: não usar.
- Conteúdos: (a) preparar os recebimentos para dias de grande movimento; (b) o que avaliar antes de escolher uma maquininha; (c) não depender só de dinheiro ou Pix.

## Responsáveis
| Quem | Faz |
|---|---|
| Claude | Frentes 1 e 2, gravação na aba Leads, código no GitHub |
| Zapia | Verificações rápidas (negócio aberto? regra publicada?), WhatsApp Business, roteiros dos vídeos de Réveillon |
| ChatGPT | Auditoria dos lotes, validação das regras e condições, revisão da campanha |
| Kauan | Aprovação, visitas, conversas, fechamento |
