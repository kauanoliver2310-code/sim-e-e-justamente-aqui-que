# 02 — Pesquisa técnica com fontes

Pesquisa feita em 06/11/2026. Legenda de status:
**OFICIAL** = conferido em fonte do próprio fornecedor/órgão ·
**TERCEIROS** = só fontes secundárias · **NÃO CONFIRMADO** = não achei evidência ·
**HIPÓTESE** = número estimado.

| Componente | O que foi verificado | Status | Fonte |
|---|---|---|---|
| **WhatsApp Business Platform (Meta)** | Cobrança por mensagem entregue desde jul/2025. Mensagens de serviço respondendo cliente dentro da janela de 24h: **grátis**. Marketing no Brasil: ~US$ 0,0625/msg (terceiros). Meta anunciou cobrança em BRL para empresas brasileiras em 2026 (datas divergem entre fontes). | TERCEIROS (preço) | [Meta — Pricing](https://developers.facebook.com/docs/whatsapp/pricing) · [Message Central — Brasil](https://www.messagecentral.com/blog/whatsapp-business-api-pricing-in-brazil) · [Kommo](https://support.kommo.com/docs/updated-pricing-rules-for-whatsapp-business.md) |
| **Evolution API** | Não oficial (automatiza o WhatsApp Web). Risco de banimento e violação dos termos. | Análise | — |
| **BrasilAPI CNPJ** | `GET https://brasilapi.com.br/api/cnpj/v1/{cnpj}`, sem chave, consulta 1 CNPJ por vez. Projeto comunitário: **sem SLA**, e limites de uso não documentados nas fontes achadas. | TERCEIROS | [docs.rs brasilapi](https://docs.rs/crate/brasilapi/latest/source/src/cnpj/mod.rs) · [Apify actor](https://apify.com/automation-lab/brasilapi-cnpj-company-scraper) |
| **CNPJ alfanumérico** | Em vigor desde jul/2026. DV com valor ASCII−48 e mesmos pesos. Validador implementado e conferido contra o exemplo oficial `12.ABC.345/01DE-35`. | OFICIAL + TESTADO | IN RFB 2.229/2024 · `tests/test_cnpj.py` |
| **IBAMA — embargos** (ATUALIZADO) | API oficial **SICAFI-AIE** no catálogo Conecta gov.br (v1.0, 20/10/2026), por CPF/CNPJ, sem autenticação, 10 req/s — achada pelo ChatGPT. Tentativa de acesso daqui bloqueada pela rede do ambiente: **testar o Swagger antes de integrar**. | OFICIAL (catálogo), NÃO TESTADO | [Catálogo](https://www.gov.br/conecta/catalogo/apis/sicafi-conecta-consulta-embargos-vigente-e-lavrados-ibama) · [Swagger](https://sicafi-conecta.ibama.gov.br/swagger-ui/index.html) |
| ~~IBAMA (versão anterior)~~ | Portal público de consulta e certidão por CPF/CNPJ, com atualização diária informada. **Não achei API REST oficial documentada.** Infosimples e BigData Corp vendem APIs pagas por cima do portal. | NÃO CONFIRMADO (API) | [Manual IBAMA](https://www.gov.br/ibama/pt-br/servicos/consultas/autuacoes-e-embargos/areas-embargadas/manual_consulta_embargos.pdf/@@download/file) · [Infosimples](https://infosimples.com/consultas/ibama-certidao-embargos/) · [BigData Corp](https://docs.bigdatacorp.com.br/plataforma/reference/ondemand_ibama_embargados_company) |
| **MTE — Lista Suja** | Atualização **semestral** (últimas: 06/04/2026 e 06/10/2026; +82 empregadores, −151 removidos). Base: Portaria Interministerial MTE/MDHC/MIR nº 18/2024. Estar na lista não é, por si só, sanção. | OFICIAL (Agência Gov) | [Agência Gov](https://agenciagov.ebc.com.br/noticias/202610/201clista-suja201d-do-trabalho-analogo-a-escravidao-e-atualizada-com-82-novos-empregadores) · [CBIC](https://cbic.org.br/?p=109264) |
| **Resend (e-mail)** | Grátis: 3.000/mês **e** 100/dia, 1 domínio. Plano pago de entrada: fontes divergem (US$ 20 para 50 mil é o mais citado). | OFICIAL (grátis) / TERCEIROS (pago) | [resend.com/pricing](https://resend.com/pricing.md) · [Blog Resend](https://resend.com/blog/new-free-tier) |
| **Claude (Anthropic)** | Haiku 5.5: US$ 0,10 de entrada / US$ 0,50 de saída por milhão de tokens (prompts de até 100K). Sonnet 5.5: US$ 2 / US$ 10. Batch API: 50% de desconto. | OFICIAL | Tabela de modelos da Anthropic (cache de 06/10/2026) |
| **Gemini (Google)** | Agregadores com preços **conflitantes** para as versões Flash 3.x. | NÃO CONFIRMADO | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) (conferir) · [anotherwrapper](https://anotherwrapper.com/llm-pricing/gemini-3.6-flash) |
| **OpenAI** | Preço citado pelo ChatGPT ("GPT-6 Luna" US$ 0,10/0,60) não verificado por mim. | NÃO CONFIRMADO | ChatGPT deve anexar a página oficial |
| **n8n** | Community Edition auto-hospedada sem licença paga (Sustainable Use License, uso interno OK). Cloud é pago, preço não cotado aqui. Tem nós nativos para Anthropic, Google Sheets, Postgres, HTTP e WhatsApp Business Cloud. | HIPÓTESE (preço) | n8n.io/pricing (conferir) |
| **VPS** | R$ 30/mês do PDF **não cotado**. Para n8n + Postgres, considerar no mínimo 2 GB de RAM. | HIPÓTESE | Cotar 2–3 fornecedores |
| **Google Calendar API** | Uso padrão sem custo, sujeito a cotas (informação do ChatGPT, compatível com a documentação conhecida). | TERCEIROS | developers.google.com/calendar |
| **LGPD / ANPD** | O legítimo interesse exige teste de finalidade, necessidade, balanceamento e salvaguardas (Guia ANPD). | OFICIAL (citado pelo ChatGPT) | Guia orientativo de Legítimo Interesse da ANPD |

## Dependência de terceiros (riscos)

| Dependência | Risco | Mitigação |
|---|---|---|
| BrasilAPI | Sem SLA, pode cair ou limitar | Cache local no Postgres + fallback para Dados Abertos CNPJ carregados localmente |
| Meta / WhatsApp | Mudança de preço/política, banimento | Só API oficial, só opt-in, número dedicado, monitorar a nota de qualidade |
| LLM | Preço e modelo mudam | Prompts versionados, saída validada (`classificacao.py`), troca de fornecedor = trocar 1 nó |
| Portais governamentais | Sem API, mudança de layout | Lista Suja por arquivo (semestral); IBAMA manual/certidão na fase 2 |

## O que ficou pendente de verificação (para o ChatGPT auditar)

1. Rate card oficial da Meta para o Brasil (BRL, categorias marketing/utility/authentication).
2. Existência e acesso à "API IBAMA de embargos" citada pelo ChatGPT (link exato e quem pode usar).
3. Preços oficiais de OpenAI e Gemini nos modelos econômicos atuais.
4. Preço do VPS (2 GB de RAM) em 2–3 fornecedores nacionais.
5. **Regulamento do programa de indicação** de cada parceiro (Mercado Pago e outros): valor da comissão, regras de divulgação, proibição de spam e uso de marca na camisa e nos vídeos.
