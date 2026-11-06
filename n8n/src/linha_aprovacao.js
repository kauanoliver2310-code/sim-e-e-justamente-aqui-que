// Monta a linha da aba Aprovacao. MODO ('p2' | 'humano') é injetado pelo build.py.
const PASSOS = ['ENVIAR_LINK', 'AGENDAR', 'TIRAR_DUVIDA'];
const deP2 = MODO === 'p2';
const base = deP2 ? $('Montar P2').all() : null;
return $input.all().map((r, k) => {
  const j = deP2 ? { ...base[k].json } : { ...r.json };
  delete j.req;
  let rascunho = '', passo = '', status = 'FILA_HUMANA', motivo = j.motivo || '';
  if (deP2) {
    const b = r.json.error ? null : (r.json.content || []).find(c => c.type === 'text');
    try {
      const d = JSON.parse(b ? b.text : 'null');
      if (d && typeof d.texto === 'string' && d.texto.trim() && PASSOS.includes(d.proximo_passo)) {
        rascunho = d.texto.trim(); passo = d.proximo_passo; status = 'RASCUNHO';
      } else motivo = 'rascunho inválido da IA';
    } catch (e) { motivo = 'rascunho inválido da IA'; }
  }
  return { json: {
    chave: 'r_' + j.wamid, telefone: j.telefone, mensagem_cliente: String(j.texto || '').slice(0, 500),
    recebido_em: j.recebido_em, intencao: j.intencao || '', confianca: j.confianca ?? '',
    rascunho, proximo_passo: passo, status, motivo,
    aprovado_por: '', enviado_em: '', ref_envio: '', criado_em: new Date().toISOString(),
  } };
});
