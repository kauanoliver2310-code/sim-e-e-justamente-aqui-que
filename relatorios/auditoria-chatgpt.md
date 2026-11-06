# Auditoria independente — ChatGPT
**Projeto:** KAUAN AI BUSINESS  
**Data da auditoria:** 06/11/2026  
**Escopo:** seção 03 de `docs/07-contrato-especialistas.md`  
**Branch auditada:** `claude/prospeccao-ia-auditoria-j84sgl`

## 1. Resumo executivo

A base de código e os documentos foram lidos pela integração GitHub. A auditoria confirma a direção inbound do projeto, identifica correções importantes nas premissas de custo e corrige a afirmação sobre a API do IBAMA.

**Não considero o sistema pronto para produção.** Os 57 testes são declarados pelo documento do projeto como executados em 06/11/2026, mas não foram reexecutados de forma independente nesta auditoria. Também não há evidência de execução real de n8n, Meta WhatsApp Cloud API, BrasilAPI ou Calendar.

## 2. Conferência de preços e fontes

### WhatsApp Business Platform — Brasil

Fonte oficial a consultar: https://developers.facebook.com/docs/whatsapp/pricing

A página oficial da Meta retornou HTTP 429 durante esta verificação, então não foi possível conferir diretamente a planilha de tarifas da Meta nesta sessão. Fontes secundárias recentes que dizem reproduzir o rate card da Meta, vigente desde 01/10/2026, apontam:

- Marketing: **R$ 0,3217 por mensagem entregue**.
- Utilidade, autenticação e serviço: **R$ 0,035 por mensagem entregue**.
- Serviço: primeiras **1.000 mensagens por número/mês gratuitas**; excedente cobrado a R$ 0,035.
- Mensagens enviadas pelo cliente não são cobradas.

Referências secundárias de conferência:
- https://blog.cenvia.com.br/whatsapp-business-api-preco/
- https://vectalk.com.br/blog/en/whatsapp-api-pricing-brazil/
- https://contactship.ai/en/blog/whatsapp-business-api-pricing-latin-america-2026

**Impacto:** a afirmação “responder dentro de 24h é sempre grátis” está desatualizada para o rate card citado por essas fontes: há franquia mensal de 1.000 mensagens de serviço por número; depois, R$ 0,035 por mensagem. Mensagem de marketing não se torna gratuita só por estar dentro da janela de 24h. A categoria depende do conteúdo e das regras da Meta.

100 mensagens de marketing entregues custariam aproximadamente **R$ 32,17**, antes de eventuais tributos ou tarifas adicionais de um provedor. O orçamento de R$ 40 é uma provisão conservadora, não o preço exato.

### Hostinger KVM 2 — fonte oficial

Página oficial: https://www.hostinger.com/br/hospedagem-n8n

Na página consultada, o KVM 2 aparece com:
- 2 vCPU, 8 GB RAM, 100 GB NVMe e 8 TB de largura de banda.
- Oferta: **R$ 42,99/mês equivalente**, com pagamento integral de **R$ 1.031,76 por 24 meses**.
- Renovação automática: **R$ 77,99/mês**, pelo mesmo período de renovação.
- O n8n auto-hospedado está incluído no modelo VPS; o n8n em si é gratuito na Community Edition.

**Correção:** os R$ 35–39/mês e o desembolso adiantado de R$ 840–940 registrados no orçamento não correspondem à oferta oficial exibida na página consultada em 06/11/2026. O valor promocional atual exibido é R$ 42,99/mês equivalente e R$ 1.031,76 adiantados por 24 meses. Preço pode mudar conforme campanha, checkout e região.

### n8n Cloud — fonte oficial

Página oficial: https://n8n.io/pricing/

A página oficial exibe:
- Starter: **€ 20/mês, faturado anualmente**, com 2.500 execuções mensais.
- Pro: **€ 50/mês, faturado anualmente**, com 10.000 execuções mensais.
- A Community Edition auto-hospedada está disponível sem licença paga.

**Correção:** “R$ 150+/mês” não é um preço oficial em reais; é uma conversão estimada. A referência oficial é € 20/mês com faturamento anual. A conversão depende do câmbio, impostos e meio de pagamento.

### Mercado Pago — programa de indicação

Artigo oficial: https://www.mercadopago.com.br/blog/ganhar-dinheiro-renda-extra-indicando-solucoes-mercado-pago

O artigo oficial, publicado em 24/07/2026, anuncia incentivos de **até R$ 250**, condicionados ao produto, campanha ativa e transações elegíveis realizadas pela pessoa indicada. O próprio Mercado Pago orienta consultar as condições vigentes no aplicativo.

**Conclusão:** R$ 250 é um teto promocional divulgado, não uma comissão garantida por venda nem receita mensal previsível. Não use esse valor como receita-base nem como garantia de ponto de equilíbrio. O regulamento e o valor efetivamente oferecido na conta do participante precisam ser confirmados antes de qualquer projeção.

### PagBank

O valor de até R$ 155 consta no orçamento como informação de terceiros. Não foi encontrada evidência oficial suficiente nesta auditoria para confirmar o valor, os requisitos ou a disponibilidade da campanha. Manter como **NÃO VERIFICADO**.

## 3. Auditoria do modelo financeiro

Arquivos lidos:
- `config/premissas.json`
- `src/kauan_ai/custos.py`
- `scripts/simular_custos.py`
- `relatorios/simulacao_custos.md`

### Correção da linha de 5.000 leads

A reprodução aritmética das premissas antigas do ChatGPT confirma:

`R$ 30,00 + R$ 13,75 + R$ 1.608,50 = R$ 1.652,25`

Portanto, **R$ 1.652,25** é o total correto. O valor de R$ 1.762,25 estava R$ 110,00 acima.

Observação de escopo: esta é uma conferência aritmética independente das fórmulas e dos valores registrados. O script `scripts/simular_custos.py` não foi executado neste ambiente, então não declaro uma reexecução independente do programa.

### Orçamento fase 1 — soma atualizada

Usando os itens listados no documento de orçamento e a oferta oficial atual da Hostinger:

| Item | Promoção VPS | Renovação VPS |
|---|---:|---:|
| Hostinger KVM 2 | R$ 42,99 | R$ 77,99 |
| Domínio (estimativa rateada) | R$ 3,50 | R$ 3,50 |
| WhatsApp (provisão do orçamento) | R$ 40,00 | R$ 40,00 |
| Chip (hipótese) | R$ 20,00 | R$ 20,00 |
| IA (hipótese) | R$ 20,00 | R$ 20,00 |
| Reserva | R$ 20,00 | R$ 20,00 |
| **Total** | **R$ 146,49** | **R$ 181,49** |

Se o item WhatsApp for exatamente 100 mensagens de marketing a R$ 0,3217, em vez da provisão de R$ 40, os totais ficam aproximadamente **R$ 138,66** na promoção e **R$ 173,66** na renovação.

O pagamento inicial do VPS, na página consultada, é **R$ 1.031,76 por 24 meses**, não R$ 840–940. Os totais mensais acima são equivalentes mensais; não representam o dinheiro exigido no checkout.

### Pontos que impedem validar R$ 20 de IA

A Anthropic confirma oficialmente Haiku 5.5 a US$ 0,10 por milhão de tokens de entrada e US$ 0,50 por milhão de tokens de saída para prompts de até 100K tokens:
https://www.anthropic.com/claude/haiku

Entretanto, a premissa “1.000 conversas × 5 chamadas” não está modelada explicitamente em `config/premissas.json` ou em `custos.py`. O modelo recebe tokens de entrada e saída por lead, sem um campo separado para chamadas por conversa.

Com as premissas intermediárias do arquivo (2.500 tokens de entrada e 700 de saída por lead, câmbio R$ 5,50), o custo calculado para 1.000 leads é cerca de **R$ 3,30** se esses tokens forem o total por lead. Se forem por chamada e houver cinco chamadas, fica perto de **R$ 16,50**. Portanto, R$ 20 pode ser uma reserva plausível, mas só após documentar se os tokens são por chamada ou por conversa e medir o consumo real.

### Problema de arquitetura no cálculo do WhatsApp

O código calcula o WhatsApp como:
`qualificados × fração_whatsapp × mensagens_por_lead × preço_whatsapp_marketing`.

Isso mistura o custo de marketing com o fluxo inbound. A arquitetura aprovada é inbound-first; respostas a mensagens recebidas devem ser contabilizadas como mensagens de serviço, separadas de templates de marketing e de follow-ups promocionais.

**Correção necessária:** criar premissas separadas para:
1. mensagens de serviço (franquia de 1.000 por número/mês e excedente);
2. templates de utilidade;
3. templates de marketing;
4. tarifas próprias de BSP/provedor, se houver.

Não classificar follow-up como serviço apenas por ocorrer dentro da janela de 24 horas.

## 4. API IBAMA — correção da afirmação anterior

A afirmação anterior de que não havia API REST oficial documentada deve ser **retratada e corrigida**.

Catálogo oficial do governo:
https://www.gov.br/conecta/catalogo/apis/sicafi-conecta-consulta-embargos-vigente-e-lavrados-ibama

O catálogo apresenta a API **SICAFI-AIE — Consulta Embargos Vigentes e Lavrados**, versão 1.0, datada de 20/10/2026. Ela permite consulta de Termos de Embargo, inclusive por CPF/CNPJ, e informa:
- Swagger de produção: https://sicafi-conecta.ibama.gov.br/swagger-ui/index.html
- OpenAPI JSON: https://sicafi-conecta.ibama.gov.br/v3/api-docs
- Sem autenticação do provedor, segundo o catálogo.
- Limite informado: 10 requisições por segundo, com tolerância a até 20 simultâneas.
- Tamanho máximo de página: 500 registros.

A API existe e está documentada no catálogo oficial. Antes de integração, deve-se conferir o Swagger, validar o contrato real do endpoint e testar limites e respostas. A consulta não deve gerar automaticamente uma conclusão de irregularidade; preservar status, data, fonte e revisão humana.

## 5. P1 — avaliação com 50 mensagens

Prompt analisado: `docs/05-prompts-agentes.md`, seção P1. Validador analisado: `src/kauan_ai/classificacao.py`.

Não foi localizado no repositório um conjunto de 50 mensagens reais e anonimizadas com rótulos de referência. Os testes disponíveis cobrem JSON válido/inválido, domínios permitidos, baixa confiança e oposição, mas não medem acurácia de intenção em mensagens reais.

Assim, **não é possível informar honestamente**:
- percentual de JSON válido em 50 mensagens reais;
- percentual de acerto da intenção;
- matriz de confusão ou precisão por classe.

Para concluir a avaliação, criar um conjunto de 50 mensagens anonimizadas, rotuladas manualmente por uma pessoa, cobrindo as seis intenções e os três estados de ICP. Rodar P1 em temperatura/configuração fixada, registrar versão do modelo e prompt, e comparar saída com os rótulos humanos.

Risco adicional do prompt: a mensagem do cliente é delimitada por tags XML-like `<mensagem>...`. Uma mensagem maliciosa pode conter texto de fechamento de tag e tentar escapar do delimitador. Preferir serialização JSON/escaping do conteúdo e reforçar que o texto do cliente é dado não confiável, nunca instrução.

O validador confere estrutura e domínios, mas não mede verdade semântica. A lógica de roteamento do n8n deve bloquear explicitamente `OPOSICAO`, `SEM_INTERESSE` e `INDEFINIDO` conforme política; não basta status estrutural `OK`.

## 6. Discordâncias e correções recomendadas

1. **Preço do VPS:** atualizar o orçamento para a oferta oficial consultada, incluindo o desembolso de 24 meses e a renovação.
2. **WhatsApp:** separar mensagens de serviço, utilidade e marketing; revisar a afirmação de gratuidade ilimitada dentro da janela de 24h.
3. **Receita de indicação:** retirar “1 venda paga a operação” como premissa garantida. Usar comissão efetiva e conversão comprovada.
4. **IBAMA:** substituir “API não encontrada” pela integração SICAFI-AIE oficial, após teste do Swagger.
5. **IA:** explicitar número de chamadas e tokens por chamada; medir tokens reais antes de fixar custo mensal.
6. **P1:** não declarar precisão sem conjunto de 50 mensagens reais anonimizadas e rotuladas.
7. **Testes:** o repositório declara 57 testes aprovados, mas a auditoria não os reexecutou. A evidência independente pendente é execução local/CI com log vinculado ao commit da branch.
8. **Inbound vs outbound:** revisar a simulação para que o custo de WhatsApp reflita o canal inbound pretendido, e mantenha prospecção ativa em cenário separado.

## 7. Estado da auditoria

| Requisito | Estado |
|---|---|
| Ler contrato, orçamento, premissas, script, módulo de custos e relatório | **ANALISADO** |
| Conferir preços oficiais disponíveis | **PARCIALMENTE VERIFICADO** |
| Rate card Meta diretamente | **PENDENTE** — página oficial retornou 429 |
| Hostinger KVM 2 | **VERIFICADO EM FONTE OFICIAL** |
| n8n Cloud | **VERIFICADO EM FONTE OFICIAL** |
| Mercado Pago | **VALOR MÁXIMO CONDICIONAL; REGULAMENTO DA CAMPANHA PENDENTE** |
| PagBank | **NÃO VERIFICADO** |
| API IBAMA | **CORRIGIDO COM CATÁLOGO OFICIAL** |
| Aritmética da linha 5.000 | **CONFERIDA** |
| Reexecução do script e dos 57 testes | **PENDENTE** |
| P1 com 50 mensagens reais anonimizadas | **PENDENTE — dataset ausente** |
| Integrações reais | **NÃO TESTADAS** |

**Conclusão:** a arquitetura inbound é uma direção mais segura e econômica do que disparos frios em massa, mas o orçamento ainda precisa de revisão e as integrações não estão validadas. Próximo passo técnico: corrigir o modelo de custo do WhatsApp e o orçamento, montar o dataset de avaliação do P1 e executar a suíte de testes no CI antes de qualquer contratação ou ativação.
