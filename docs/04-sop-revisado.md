# 04 — SOP revisado: Prospecção, Qualificação e Vendas com IA

Versão 2.0 · 06/11/2026 · substitui o SOP v1 (PDF).

## 1. Princípios

1. **Inbound primeiro.** O vídeo gera a conversa; a automação acelera a resposta e o acompanhamento.
2. **Código decide, IA redige.** Regras, cálculos e consultas são feitos por código. A IA interpreta texto e escreve rascunhos.
3. **Nada sai sem o Kauan aprovar.** Toda mensagem começa como rascunho.
4. **Na dúvida, PENDENTE.** Fonte fora do ar, desatualizada ou com dado incompleto nunca vira aprovação.
5. **Evidência ou nada.** Todo parecer registra fonte, data da consulta, data da base e referência.
6. **LGPD desde o primeiro lead.** Base legal, oposição, retenção e registro.
7. **Simulação por padrão.** Disparos reais, contratação de serviço e compra de créditos só com autorização expressa do Kauan.

## 2. Fluxo operacional

### Etapa A — Entrada do lead
- **A1 (inbound):** cliente manda mensagem no WhatsApp (vindo do vídeo). Base legal: `PROCEDIMENTOS_PRELIMINARES`, porque o titular pediu informação.
- **A2 (lista, fase 2):** Dados Abertos CNPJ filtrados por CNAE + município. Base legal: `LEGITIMO_INTERESSE`, **só com o teste de legítimo interesse (LIA) preenchido** (ver §5). O sistema bloqueia o cadastro sem LIA.
- Todo CNPJ é validado (numérico e alfanumérico) e deduplicado pela forma normalizada.

### Etapa B — Qualificação
1. Consulta cadastral (BrasilAPI, com cache de 30 dias): situação, CNAE, porte, MEI.
2. Situação ≠ ATIVA ⇒ `INAPTO_CADASTRAL`; o lead é encerrado com mensagem educada, se for inbound.
3. A IA classifica a intenção da mensagem → JSON validado. JSON inválido ⇒ `FALHA_CLASSIFICACAO` ⇒ o Kauan lê.
4. Intenção `OPOSICAO` ("não quero", "pare", "sair") ⇒ **registrar oposição imediatamente** e não responder com oferta.

### Etapa C — Compliance (fase 2, canal A2)
| Fonte | Como | Validade da base |
|---|---|---|
| Receita (BrasilAPI) | Automático | 45 dias |
| MTE Lista Suja | Arquivo semestral baixado e comparado por CNPJ | 200 dias |
| IBAMA embargos | Certidão manual quando houver indício (fase 2) | 7 dias |
| Falência/RJ | Fora do MVP (sem fonte gratuita estruturada confirmada) | — |

Pareceres possíveis: `APTO`, `PENDENTE`, `REVISAO_HUMANA` (homônimo), `RESTRICAO_A_CONFIRMAR`
(CNPJ exato, o Kauan decide), `INAPTO_CADASTRAL`. **Só `APTO` segue automaticamente.**

### Etapa D — Abordagem
1. A IA gera um rascunho curto, com o nome da empresa, o segmento e **uma** oferta adequada (maquininha, conta PJ...).
2. O Kauan aprova, edita ou descarta (rascunho e versão final ficam guardados para melhorar o prompt).
3. Envio:
   - WhatsApp: **somente** resposta dentro da janela de 24h do cliente ou com opt-in registrado.
   - E-mail (fase 2): no máximo 100/dia (limite grátis do Resend), com remetente identificado e **link de descadastro**.
4. A chave de idempotência impede mensagem duplicada; reprocessar não reenvia.

### Etapa E — Fechamento / agenda
- Venda simples (maquininha): mandar o **link de indicação** certo no WhatsApp. Sem reunião.
- Venda consultiva (conta PJ, várias soluções): link do Cal.com ou proposta de 3 horários. O evento é criado por código, com idempotência; após 3 falhas, escala para o Kauan.

### Etapa F — CRM e métricas (toda semana)
Leads por origem · tempo de primeira resposta · % qualificados · reuniões · vendas · **custo por venda** · oposições recebidas.

## 3. Tratamento de exceções
| Situação | Ação |
|---|---|
| API fora do ar | `PENDENTE` + fila de reprocessamento a cada 6h; máximo de 5 tentativas, depois o Kauan é avisado |
| Base desatualizada | `PENDENTE` até a base ser atualizada |
| JSON da IA inválido | `FALHA_CLASSIFICACAO`, sem resposta automática |
| Falha de envio | Status `FALHA`; reprocessamento reenvia uma única vez |
| Falha na agenda | Retentativa; na 3ª, `ESCALADO_HUMANO` |
| Limite diário de e-mail | Para e continua no dia seguinte |

## 4. Papéis
| Papel | Responsável |
|---|---|
| Aprovar mensagens, confirmar restrições, fechar vendas | Kauan |
| Executar fluxos | n8n |
| Regras e validações | Código (este repositório) |
| Auditoria mensal de preços, APIs e regras | ChatGPT + Claude (checklist em `06-plano-implantacao.md`) |

## 5. LGPD — regras mínimas

1. **Finalidade:** oferecer soluções de pagamento e contas PJ a empresas. Nada além disso.
2. **Necessidade:** guardar só CNPJ, razão social, CNAE, município, contato comercial e histórico da conversa.
3. **Base legal por lead**, gravada no cadastro:
   - inbound ⇒ procedimentos preliminares a pedido do titular;
   - lista ⇒ legítimo interesse **com LIA documentada** (finalidade legítima, necessidade, balanceamento com as expectativas do titular, salvaguardas: opt-out fácil, volume baixo, contexto B2B).
4. **MEI e empresário individual = dados de pessoa física.** Cuidado redobrado: nada de enriquecer com redes sociais pessoais.
5. **Transparência:** a primeira mensagem diz quem é o Kauan, como conseguiu o contato e como pedir para sair.
6. **Oposição/descadastro:** atendida na hora, em qualquer canal. O contato vai para a lista de supressão (hash) e os dados do lead são eliminados. Testado em `tests/test_leads_mensagens.py`.
7. **Retenção:** lead sem interação por 180 dias é descartado automaticamente, com registro.
8. **Acesso:** só o Kauan acessa planilha/banco; credenciais nos *credentials* do n8n, nunca no código ou na planilha.
9. **Registro:** cada consulta guarda fonte, data e hash do retorno; cada evento LGPD vai para `eventos_lgpd`.
10. **Revisão humana:** nenhuma empresa é marcada como irregular sem o Kauan ver a evidência.

## 6. O que está proibido
- Evolution API ou qualquer automação não oficial de WhatsApp.
- Mensagem de marketing no WhatsApp para quem não deu opt-in.
- Raspagem de sites ou do Google Maps contra os termos de uso.
- Comprar listas de contatos.
- IA declarando "aprovado/reprovado" sem o motor de regras.
- Envio sem aprovação humana.
