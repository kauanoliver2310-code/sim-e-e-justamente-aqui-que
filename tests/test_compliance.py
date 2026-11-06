import unittest
from datetime import datetime, timedelta, timezone

from kauan_ai.compliance import (
    Confianca, Parecer, ResultadoFonte, StatusFonte, TipoCorrespondencia,
    avaliar, pode_seguir_para_abordagem,
)

AGORA = datetime(2026, 11, 6, 12, tzinfo=timezone.utc)
CNPJ = "11222333000181"


def receita(situacao="ATIVA", status=StatusFonte.NADA_CONSTA, base=AGORA - timedelta(days=10)):
    return ResultadoFonte("RECEITA", status, AGORA, base, situacao_cadastral=situacao)


def ibama(status=StatusFonte.NADA_CONSTA, corr=TipoCorrespondencia.NENHUMA, base=AGORA - timedelta(days=1)):
    return ResultadoFonte("IBAMA_EMBARGOS", status, AGORA, base, corr, referencia="ibama-ref")


def mte(status=StatusFonte.NADA_CONSTA, corr=TipoCorrespondencia.NENHUMA,
        base=datetime(2026, 10, 6, tzinfo=timezone.utc)):
    return ResultadoFonte("MTE_LISTA_SUJA", status, AGORA, base, corr, referencia="mte-2026-10")


class TestCompliance(unittest.TestCase):
    def test_tudo_limpo_e_atual_apto(self):
        r = avaliar(CNPJ, [receita(), ibama(), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.APTO)
        self.assertEqual(r.confianca, Confianca.ALTA)
        self.assertEqual(len(r.evidencias), 3)
        self.assertTrue(all(e["consultado_em"] for e in r.evidencias))
        self.assertTrue(pode_seguir_para_abordagem(r))

    def test_api_indisponivel_gera_pendente_nunca_aprovacao(self):
        r = avaliar(CNPJ, [receita(), ibama(StatusFonte.INDISPONIVEL), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)
        self.assertIn("IBAMA_EMBARGOS", r.fontes_pendentes)
        self.assertFalse(pode_seguir_para_abordagem(r))

    def test_erro_de_fonte_gera_pendente(self):
        r = avaliar(CNPJ, [receita(), ibama(), mte(StatusFonte.ERRO)], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)

    def test_fonte_nao_consultada_gera_pendente(self):
        r = avaliar(CNPJ, [receita(), ibama()], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)
        self.assertIn("MTE_LISTA_SUJA", r.fontes_pendentes)

    def test_base_desatualizada_gera_pendente(self):
        velha = AGORA - timedelta(days=400)
        r = avaliar(CNPJ, [receita(), ibama(), mte(base=velha)], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)
        self.assertTrue(any("desatualizada" in m for m in r.motivos))

    def test_base_sem_data_gera_pendente(self):
        r = avaliar(CNPJ, [receita(), ibama(base=None), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)

    def test_empresa_inativa(self):
        r = avaliar(CNPJ, [receita("BAIXADA"), ibama(), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.INAPTO_CADASTRAL)
        self.assertFalse(pode_seguir_para_abordagem(r))

    def test_dados_incompletos_receita_sem_situacao(self):
        r = avaliar(CNPJ, [receita(situacao=None), ibama(), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.PENDENTE)

    def test_homonimo_nao_gera_restricao(self):
        r = avaliar(CNPJ, [receita(), ibama(StatusFonte.CONSTA, TipoCorrespondencia.NOME_APROXIMADO), mte()], AGORA)
        self.assertEqual(r.parecer, Parecer.REVISAO_HUMANA)
        self.assertEqual(r.confianca, Confianca.BAIXA)
        self.assertNotEqual(r.parecer, Parecer.RESTRICAO_A_CONFIRMAR)

    def test_cnpj_exato_restricao_a_confirmar_por_humano(self):
        r = avaliar(CNPJ, [receita(), ibama(), mte(StatusFonte.CONSTA, TipoCorrespondencia.CNPJ_EXATO)], AGORA)
        self.assertEqual(r.parecer, Parecer.RESTRICAO_A_CONFIRMAR)
        self.assertTrue(r.requer_revisao_humana)
        self.assertTrue(any("mte-2026-10" in m for m in r.motivos))

    def test_restricao_exata_prevalece_sobre_pendencia(self):
        r = avaliar(CNPJ, [receita(), ibama(StatusFonte.INDISPONIVEL),
                           mte(StatusFonte.CONSTA, TipoCorrespondencia.CNPJ_EXATO)], AGORA)
        self.assertEqual(r.parecer, Parecer.RESTRICAO_A_CONFIRMAR)

    def test_reprocessamento_pendente_vira_apto_quando_fonte_volta(self):
        r1 = avaliar(CNPJ, [receita(), ibama(StatusFonte.INDISPONIVEL), mte()], AGORA)
        self.assertEqual(r1.parecer, Parecer.PENDENTE)
        r2 = avaliar(CNPJ, [receita(), ibama(), mte()], AGORA + timedelta(hours=2))
        self.assertEqual(r2.parecer, Parecer.APTO)


if __name__ == "__main__":
    unittest.main()
