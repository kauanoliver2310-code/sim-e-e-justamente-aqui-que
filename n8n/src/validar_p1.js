// Port de src/kauan_ai/classificacao.py. Saída inválida nunca vira resposta automática.
const INT = ['INTERESSADO', 'QUER_AGENDAR', 'DUVIDA', 'SEM_INTERESSE', 'OPOSICAO', 'INDEFINIDO'];
const ICP = ['DENTRO', 'FORA', 'INCERTO'];
function textoDe(r) {
  if (!r || r.error) return null;
  if (r.stop_reason === 'refusal' || r.stop_reason === 'max_tokens') return null;
  const b = (r.content || []).find(c => c.type === 'text');
  return b ? b.text : null;
}
function validar(t) {
  if (t == null) return { valida: false, erro: 'sem resposta da IA' };
  let d; try { d = JSON.parse(t); } catch (e) { return { valida: false, erro: 'JSON inválido' }; }
  if (!d || typeof d !== 'object' || Array.isArray(d)) return { valida: false, erro: 'não é objeto' };
  if (!INT.includes(d.intencao)) return { valida: false, erro: 'intencao inválida' };
  if (!ICP.includes(d.icp)) return { valida: false, erro: 'icp inválido' };
  if (typeof d.confianca !== 'number' || d.confianca < 0 || d.confianca > 1) return { valida: false, erro: 'confianca inválida' };
  if (typeof d.justificativa !== 'string' || !d.justificativa.trim()) return { valida: false, erro: 'justificativa ausente' };
  return { valida: true, ...d };
}
const base = $('Montar P1').all();
return $input.all().map((r, k) => {
  const j = { ...base[k].json }; delete j.req;
  const v = validar(textoDe(r.json));
  j.intencao = v.intencao || ''; j.icp = v.icp || ''; j.confianca = v.confianca ?? '';
  j.justificativa = v.justificativa || v.erro || '';
  if (!v.valida) { j.rota = 'humano'; j.motivo = 'FALHA_CLASSIFICACAO: ' + v.erro; }
  else if (v.intencao === 'OPOSICAO') { j.rota = 'oposicao'; }
  else if (v.confianca < 0.7) { j.rota = 'humano'; j.motivo = 'REVISAO_HUMANA: confiança baixa'; }
  else if (['INTERESSADO', 'QUER_AGENDAR', 'DUVIDA'].includes(v.intencao)) { j.rota = 'rascunho'; }
  else { j.rota = 'humano'; j.motivo = 'intenção ' + v.intencao; }
  return { json: j };
});
