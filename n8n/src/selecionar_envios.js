// Só APROVADA sai. Supressão, janela de 24h e envio já feito são checados aqui.
const cfg = $('Config').first().json;
const st = $getWorkflowStaticData('global');
st.enviados = st.enviados || [];
const sup = new Set($input.all().map(r => String(r.json.chave || '')));
const agora = Date.now();
const out = [];
for (const i of $('Hash telefone').all()) {
  const j = i.json;
  const status = String(j.status || '').toUpperCase();
  const FINAIS = ['ENVIADA', 'SIMULADA', 'BLOQUEADA', 'JANELA_EXPIRADA', 'FALHA', 'FILA_HUMANA', 'DESCARTADA'];
  if (FINAIS.includes(status) && j.telefone && agora - Date.parse(j.criado_em || j.recebido_em) > (cfg.retencao_dias || 30) * 864e5) {
    out.push({ json: { chave: j.chave, telefone: '', mensagem_cliente: '', motivo: 'anonimizado (retenção)', acao: 'atualizar' } });
    continue;
  }
  if (status !== 'APROVADA') continue;
  const texto = String(j.rascunho || '').trim();
  const row = { chave: j.chave };
  if (st.enviados.includes(j.chave)) { row.status = 'ENVIADA'; row.motivo = 'já enviada (idempotência)'; row.acao = 'atualizar'; }
  else if (!j.aprovado_por) { row.status = 'RASCUNHO'; row.motivo = 'falta preencher aprovado_por'; row.acao = 'atualizar'; }
  else if (sup.has('telefone:' + j.telefone_hash)) { row.status = 'BLOQUEADA'; row.motivo = 'oposição registrada'; row.acao = 'atualizar'; }
  else if (!texto) { row.status = 'FILA_HUMANA'; row.motivo = 'rascunho vazio'; row.acao = 'atualizar'; }
  else if (agora - Date.parse(j.recebido_em) > cfg.janela_horas * 3600e3) {
    row.status = 'JANELA_EXPIRADA'; row.motivo = 'passou de 24h: exige template pago'; row.acao = 'atualizar';
  } else if (cfg.dry_run) {
    row.status = 'SIMULADA'; row.motivo = 'dry_run=true'; row.enviado_em = new Date().toISOString(); row.acao = 'atualizar';
  } else {
    out.push({ json: { chave: j.chave, acao: 'enviar', req: {
      messaging_product: 'whatsapp', to: String(j.telefone), type: 'text', text: { body: texto } } } });
    continue;
  }
  out.push({ json: row });
}
return out;
