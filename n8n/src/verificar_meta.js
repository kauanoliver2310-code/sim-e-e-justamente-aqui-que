// Verificação do webhook (GET) pela Meta. Troque o token aqui e no painel da Meta.
const TOKEN = 'TROQUE_ESTE_TOKEN_DE_VERIFICACAO';
const q = $input.first().json.query || {};
const ok = q['hub.mode'] === 'subscribe' && q['hub.verify_token'] === TOKEN;
return [{ json: { ok, challenge: ok ? String(q['hub.challenge']) : 'forbidden' } }];
