// LGPD: guarda só o hash do telefone. Nada de oferta depois disso.
return $input.all().map(i => ({ json: {
  chave: 'telefone:' + i.json.telefone_hash, canal: 'WHATSAPP',
  motivo: i.json.oposicao_palavra ? 'palavra-chave' : 'IA: OPOSICAO',
  registrado_em: new Date().toISOString(),
} }));
