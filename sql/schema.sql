-- KAUAN AI BUSINESS — schema PostgreSQL (fase 2). Espelha as regras de src/kauan_ai.
-- Não aplicado em nenhum banco real ainda.

CREATE TABLE leads (
    cnpj              CHAR(14) PRIMARY KEY,           -- normalizado, aceita alfanumérico
    razao_social      TEXT NOT NULL,
    origem            TEXT NOT NULL CHECK (origem IN
                      ('INBOUND_WHATSAPP','INBOUND_FORMULARIO','DADOS_ABERTOS_CNPJ','INDICACAO','MANUAL')),
    base_legal        TEXT NOT NULL CHECK (base_legal IN
                      ('CONSENTIMENTO','LEGITIMO_INTERESSE','PROCEDIMENTOS_PRELIMINARES')),
    lia_referencia    TEXT,
    telefone          TEXT,
    email             TEXT,
    contato_origem    TEXT,                            -- ex.: 'cadastro_cnpj' (pode ser do contador)
    cnae              TEXT,
    municipio         TEXT,
    uf                CHAR(2),
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultima_interacao  TIMESTAMPTZ,
    CONSTRAINT lia_obrigatoria CHECK (base_legal <> 'LEGITIMO_INTERESSE' OR lia_referencia IS NOT NULL)
);

CREATE TABLE consultas_fonte (
    id                BIGSERIAL PRIMARY KEY,
    cnpj              CHAR(14) NOT NULL,
    fonte             TEXT NOT NULL,                   -- RECEITA, IBAMA_EMBARGOS, MTE_LISTA_SUJA...
    status            TEXT NOT NULL CHECK (status IN ('NADA_CONSTA','CONSTA','INDISPONIVEL','ERRO')),
    correspondencia   TEXT NOT NULL DEFAULT 'NENHUMA',
    consultado_em     TIMESTAMPTZ NOT NULL,
    data_base         TIMESTAMPTZ,                     -- data de atualização da base consultada
    referencia        TEXT,
    payload_hash      TEXT                             -- hash do retorno bruto, para auditoria
);

CREATE TABLE pareceres_compliance (
    id                BIGSERIAL PRIMARY KEY,
    cnpj              CHAR(14) NOT NULL,
    parecer           TEXT NOT NULL CHECK (parecer IN
                      ('APTO','PENDENTE','REVISAO_HUMANA','RESTRICAO_A_CONFIRMAR','INAPTO_CADASTRAL')),
    confianca         TEXT NOT NULL CHECK (confianca IN ('ALTA','MEDIA','BAIXA')),
    motivos           JSONB NOT NULL,
    evidencias        JSONB NOT NULL,
    revisado_por      TEXT,
    decisao_humana    TEXT,
    avaliado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE mensagens (
    chave             CHAR(32) PRIMARY KEY,            -- sha256(cnpj|canal|campanha|etapa)
    cnpj              CHAR(14) NOT NULL,
    canal             TEXT NOT NULL CHECK (canal IN ('EMAIL','WHATSAPP')),
    destino           TEXT NOT NULL,
    texto_rascunho    TEXT NOT NULL,
    texto_aprovado    TEXT,
    status            TEXT NOT NULL CHECK (status IN ('RASCUNHO','APROVADA','ENVIADA','BLOQUEADA','FALHA')),
    aprovada_por      TEXT,
    ref_provedor      TEXT,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    enviado_em        TIMESTAMPTZ
);

CREATE TABLE supressao (
    chave             TEXT PRIMARY KEY,                -- 'cnpj:<cnpj>' | 'telefone:<sha256>' | 'email:<sha256>'
    canal             TEXT,
    motivo            TEXT NOT NULL DEFAULT 'oposicao',
    registrado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE eventos_lgpd (
    id                BIGSERIAL PRIMARY KEY,
    evento            TEXT NOT NULL,                   -- OPOSICAO, DADOS_ELIMINADOS, DESCARTE_RETENCAO, ACESSO...
    detalhes          JSONB NOT NULL,
    em                TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agendamentos (
    cnpj              CHAR(14) PRIMARY KEY,
    inicio            TIMESTAMPTZ NOT NULL,
    fim               TIMESTAMPTZ NOT NULL CHECK (fim > inicio),
    status            TEXT NOT NULL CHECK (status IN ('SOLICITADO','CONFIRMADO','FALHA','ESCALADO_HUMANO')),
    evento_id         TEXT,
    tentativas        INT NOT NULL DEFAULT 0,
    erros             JSONB NOT NULL DEFAULT '[]'
);

CREATE INDEX ON consultas_fonte (cnpj, fonte, consultado_em DESC);
CREATE INDEX ON mensagens (cnpj);
