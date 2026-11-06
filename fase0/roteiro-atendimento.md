# Fase 0 — Roteiro de atendimento manual (14 dias, custo zero)

Objetivo: provar demanda e juntar 50 mensagens rotuladas, **sem automação e sem gastar**.
Automação (n8n) fica **desligada** até a decisão do dia 14 (aba *Resumo* da planilha).

## Regras de privacidade (valem para a planilha toda)
- **Nunca** registre nome, telefone, CNPJ, print ou a mensagem original.
- Use `id` sequencial (C001...). O vínculo id ↔ contato fica **só no seu WhatsApp**.
- `resumo_anonimo`: reescreva a 1ª mensagem com suas palavras, sem nomes, números ou marcas pessoais.
  Ex.: "Oi Kauan, sou a Ana da Padaria Sol, minha maquininha cobra 4%" → *"Tem padaria, acha a taxa da máquina atual alta."*
- Se a pessoa pedir para sair: pare na hora, não insista, marque `intencao = OPOSICAO`.
- Planilha só sua (Google com verificação em 2 etapas). Apague a planilha se encerrar o projeto.

## Roteiro (5 passos, até 4 linhas por mensagem)

**1. Abertura (responda em até 15 min)**
> Fala, tudo certo? Aqui é o Kauan, vi que você veio pelo vídeo. Me conta rapidinho: qual é o seu negócio?

**2. Diagnóstico (no máximo 2 perguntas)**
> Hoje você recebe como: máquina, Pix, link? Qual o que mais te incomoda: taxa, prazo para cair o dinheiro ou aluguel da máquina?

(Se ele quiser contar: faixa de faturamento mensal. Não insista.)

**3. Recomendação (uma oferta só, sem prometer taxa)**
> Pelo que você falou, o que faz mais sentido é [produto]. As condições aparecem na hora do cadastro, pelo meu link. Quer que eu te mande?

**4. Link + próximo passo**
> Segue o link: [link de indicação]. Qualquer dúvida no cadastro, me chama aqui que eu te ajudo.

**5. Acompanhamento (uma vez só, em até 24h, só se ele não respondeu)**
> Conseguiu dar uma olhada? Se não fizer sentido agora, sem problema.

Depois disso, **não mande mais nada** se ele não responder (marque `Sem resposta`).

## Respostas prontas
| Situação | Resposta |
|---|---|
| "Qual a taxa?" | "Depende do plano e do tipo de venda; aparece certinho no cadastro antes de você confirmar qualquer coisa. Te mando o link?" |
| "Já tenho máquina" | "Tranquilo! Quanto você paga hoje? Se a sua já está boa, não vale trocar." |
| "Não tenho CNPJ" | "Algumas opções funcionam com CPF; outras pedem CNPJ (MEI). Quer que eu veja qual serve pra você?" |
| Pediu para sair | "Certo, não te mando mais nada. Obrigado!" → `OPOSICAO` |

## O que NÃO falar
- Taxa ou valor que você não viu no regulamento ou no app do parceiro.
- "Aprovação garantida" de crédito ou conta.
- Que você é funcionário do banco ou da fintech. Você é **consultor parceiro / indicador**.

## Rotina diária (10 min)
1. Para cada conversa nova: uma linha na planilha (id, data, vídeo, segmento, necessidade, intenção, resumo anônimo, minutos até responder).
2. Atualize a `etapa` das conversas antigas.
3. Quando o app do programa mostrar comissão: preencha `comissao_prevista` / `comissao_recebida`.

## Dia 14 — decisão (aba Resumo)
3 ou mais respostas **SIM** → avaliar servidor e automação (com as 50 mensagens para testar a IA).
Menos que isso → ajustar vídeos e oferta. **Não gastar.**
