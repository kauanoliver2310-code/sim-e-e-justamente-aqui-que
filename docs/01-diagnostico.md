# 01 — Diagnóstico do SOP original

Documento auditado: *SOP — Agente Autônomo de Prospecção, Compliance e Vendas* (PDF, 5 seções).
Data da auditoria: 06/11/2026. Responsável: Claude (pesquisa, arquitetura, especificação).

## Resumo em uma frase

O SOP tem uma boa estrutura (minerar → checar → abordar → agendar → CRM), mas foi escrito para
**prospecção fria em massa**, e esse é justamente o modelo mais caro, mais arriscado e menos aderente
ao negócio do Kauan (vídeo curto → WhatsApp → link de indicação).

## Problemas encontrados

| # | Trecho do SOP | Problema | Gravidade | Correção |
|---|---|---|---|---|
| 1 | "Disparo automatizado" via **Evolution API (WhatsApp)** | API não oficial. Viola os termos do WhatsApp e arrisca banimento do número que é a principal ferramenta de fechamento do Kauan. | **Crítica** | Só WhatsApp Business Platform oficial (Cloud API). |
| 2 | WhatsApp para leads minerados | Mensagem iniciada pela empresa exige **opt-in** do destinatário pela política do WhatsApp. Número de cadastro de CNPJ não é opt-in. | **Crítica** | WhatsApp só para quem chamou primeiro (inbound) ou deu opt-in. Frio → e-mail, com regras LGPD. |
| 3 | "APIs corporativas para **raspagem**" de leads | BrasilAPI consulta **um CNPJ por vez**; não busca por CNAE/cidade. Raspagem de sites tem risco legal e de termos de uso. | Alta | Lista vem do **Dados Abertos CNPJ** da Receita (download mensal, grátis) ou de inbound. |
| 4 | "Filtrar contatos diretos (e-mails e telefones)" | Telefone/e-mail do cadastro CNPJ muitas vezes é do **contador**, não do dono. Em MEI, é dado de **pessoa física** (LGPD plena). | Alta | Marcar origem do contato; não presumir que é do decisor; base legal registrada por lead. |
| 5 | IA "atribui nota de risco" e Status "Aprovado / Reprovado" | IA não pode reprovar empresa por coincidência de nome ou dado não confirmado. | Alta | Motor **determinístico** (`src/kauan_ai/compliance.py`): evidência + confiança; restrição só com CNPJ exato e confirmação humana. |
| 6 | "[PENDENTE: API X INDISPONÍVEL]" | Boa ideia, mas o SOP não proíbe aprovar com fonte faltando, nem trata **base desatualizada**. | Média | Fonte ausente/erro/desatualizada ⇒ `PENDENTE`, nunca `APTO`. Testado. |
| 7 | Tabela de custos "Gratuito" | Confunde **ter API** com **ser grátis**. Resend grátis tem teto de 100/dia; WhatsApp marketing é pago por mensagem; VPS não cotado. | Média | Modelo de custos em código com status de cada premissa (`config/premissas.json`). |
| 8 | Prompt 2 manda a IA "fazer o cruzamento nas bases" | LLM não consulta base nenhuma: ela inventa se não receber os dados. | Alta | Consultas feitas por código/n8n; a IA só **redige** a partir dos resultados já obtidos. |
| 9 | Prompt 3: IA "verifica horários" e "cria o evento" | Mesma falha: ação externa precisa ser nó/código, com idempotência. | Média | `src/kauan_ai/agenda.py`: idempotente, retentativa, escala para humano. |
| 10 | "Banco vetorial" para aprender com correções | Complexidade sem retorno no estágio atual. | Baixa | Guardar rascunho vs. versão aprovada numa tabela; revisar mensalmente e ajustar o prompt. |
| 11 | Sem LGPD | Nenhuma menção a base legal, oposição, retenção, registro. | **Crítica** | Ver `04-sop-revisado.md` §LGPD e `src/kauan_ai/leads.py`. |
| 12 | Sem métrica de negócio | Não mede custo por reunião nem por venda. | Média | `custos.py` calcula R$/reunião e ponto de equilíbrio por comissão. |
| 13 | Compliance com IBAMA/MTE/falência para todo lead | Para padaria, salão e loja de bairro comprando maquininha, o risco é baixo; custo de integração é alto. | Média | Fase 1: só Receita (ativa, CNAE, porte). IBAMA/MTE na fase 2, para proteger a marca pessoal. |

## Auditoria do material do ChatGPT

| Afirmação | Verificação | Resultado |
|---|---|---|
| Tabela de custos (100 a 5.000 leads) | Reproduzida em código (`tests/test_custos.py`) | 4 linhas conferem. **A linha de 5.000 está errada**: publicou R$ 1.762,25; o correto é **R$ 1.652,25** (erro de soma de R$ 110). |
| Resend grátis: 3.000/mês, 100/dia | Página oficial do Resend | **Confirmado.** |
| Lista Suja semestral | Agência Gov / imprensa (atualizações em 06/04/2026 e 06/10/2026) | **Confirmado.** |
| "IBAMA possui API governamental específica de embargos" | Não encontrei documentação pública dessa API. Achei o portal de consulta/certidão e serviços **pagos de terceiros** que automatizam o portal. | **Não confirmado.** APIs do catálogo Conecta gov.br costumam ser restritas a órgãos públicos. Pedir ao ChatGPT o link exato. |
| WhatsApp marketing R$ 0,3217/msg | Terceiros citam ~US$ 0,0625/msg para o Brasil (≈ R$ 0,34 com câmbio de R$ 5,50). Não consegui abrir o rate card oficial. | **Plausível, não confirmado.** |
| Preço "GPT-6 Luna" US$ 0,10/0,60 | Não verificado por mim. | **Pendente.** O ChatGPT deve anexar a página oficial. |
| Simulação manda WhatsApp de marketing para 100% dos leads | — | **Premissa errada** para leads frios: viola a regra de opt-in (item 2). |

## Conclusão

O sistema é viável **se for invertido**: a automação serve o **inbound** gerado pelos vídeos
(qualificar, responder rápido, acompanhar, registrar, mandar o link certo) e a prospecção ativa vira
um canal **secundário e controlado** (e-mail com LGPD e lista pequena e regional), não disparo em massa.
