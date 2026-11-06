// Extrai mensagens do webhook da Meta. Ignora status de entrega e IDs já vistos (Meta reenvia).
const st = $getWorkflowStaticData('global');
st.vistos = st.vistos || [];
const out = [];
for (const item of $('Webhook POST').all()) {
  const body = item.json.body || {};
  for (const entry of body.entry || []) for (const ch of entry.changes || []) {
    const v = ch.value || {};
    const nomes = {};
    for (const c of v.contacts || []) nomes[c.wa_id] = (c.profile && c.profile.name) || '';
    for (const m of v.messages || []) {
      if (!m.id || st.vistos.includes(m.id)) continue;
      st.vistos.push(m.id);
      let texto = '';
      if (m.type === 'text') texto = (m.text && m.text.body) || '';
      else if (m.type === 'button') texto = (m.button && m.button.text) || '';
      else if (m.type === 'interactive') {
        const it = m.interactive || {};
        texto = (it.button_reply && it.button_reply.title) || (it.list_reply && it.list_reply.title) || '';
      }
      out.push({ json: {
        wamid: m.id, telefone: String(m.from || '').replace(/\D/g, ''), nome: nomes[m.from] || '',
        tipo: m.type, texto: texto.slice(0, 2000),
        recebido_em: new Date(Number(m.timestamp) * 1000 || Date.now()).toISOString(),
      } });
    }
  }
}
if (st.vistos.length > 2000) st.vistos = st.vistos.slice(-1000);
return out;
