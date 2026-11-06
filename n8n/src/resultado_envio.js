const st = $getWorkflowStaticData('global');
st.enviados = st.enviados || [];
const base = $('Selecionar envios').all().filter(i => i.json.acao === 'enviar');
return $input.all().map((r, k) => {
  const chave = base[k].json.chave;
  const id = r.json.messages && r.json.messages[0] && r.json.messages[0].id;
  if (id) {
    st.enviados.push(chave);
    if (st.enviados.length > 5000) st.enviados = st.enviados.slice(-2500);
    return { json: { chave, status: 'ENVIADA', ref_envio: id, enviado_em: new Date().toISOString(), motivo: '' } };
  }
  const erro = r.json.error ? JSON.stringify(r.json.error).slice(0, 300) : 'sem id na resposta';
  return { json: { chave, status: 'FALHA', motivo: erro } };
});
