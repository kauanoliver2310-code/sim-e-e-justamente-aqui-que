// Junta lista de supressão + palavra-chave de descadastro. Decide: ignorar | oposicao | classificar.
const sup = new Set($input.all().map(r => String(r.json.chave || '')));
const RX = /^\s*(sair|parar|pare|stop|descadastrar|remover)\s*[.!]*\s*$|n[aã]o\s+(me\s+)?(mande|envie)\s+mais|n[aã]o\s+quero\s+mais\s+receber|me\s+tir[ae]\s+da\s+lista/i;
return $('Hash telefone').all().map(i => {
  const j = { ...i.json };
  j.suprimido = sup.has('telefone:' + j.telefone_hash);
  j.oposicao_palavra = RX.test(j.texto || '');
  j.rota = j.suprimido ? 'ignorar' : (j.oposicao_palavra ? 'oposicao' : (j.texto ? 'classificar' : 'humano'));
  if (j.rota === 'humano') j.motivo = 'mensagem sem texto (' + j.tipo + ')';
  return { json: j };
});
