import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from kauan_ai.custos import (
    PremissaInvalida, calcular, carregar_premissas, ponto_de_equilibrio, simular,
)

RAIZ = Path(__file__).resolve().parents[1]
DADOS = carregar_premissas(RAIZ / "config" / "premissas.json")
INTER = DADOS["cenarios"]["intermediario"]


def premissas_chatgpt():
    p = copy.deepcopy(INTER)
    p.update(cambio_brl_usd=5.5, infra_mensal_brl=30.0, dominio_mensal_brl=0.0,
             llm_preco_entrada_usd_mtok=0.10, llm_preco_saida_usd_mtok=0.60,
             llm_tokens_entrada_por_lead=2000, llm_tokens_saida_por_lead=500,
             taxa_qualificacao=1.0, fracao_qualificados_whatsapp=1.0,
             preco_whatsapp_marketing_brl=0.3217, emails_por_lead_qualificado=0)
    return p


class TestCustos(unittest.TestCase):
    def test_reproduz_tabela_do_chatgpt(self):
        # 4 de 5 linhas conferem com a tabela do ChatGPT.
        esperado = {100: 62.45, 500: 192.22, 1000: 354.45, 3000: 1003.35}
        for v, total in esperado.items():
            with self.subTest(v=v):
                r = calcular(v, premissas_chatgpt())
                self.assertAlmostEqual(r.total_caixa_brl, total, delta=0.01)

    def test_linha_5000_do_chatgpt_tem_erro_de_soma(self):
        # ChatGPT publicou R$ 1.762,25. Correto: 30 + 13,75 + 1.608,50 = 1.652,25.
        r = calcular(5000, premissas_chatgpt())
        self.assertAlmostEqual(r.custo_ia_brl, 13.75, delta=0.01)
        self.assertAlmostEqual(r.custo_whatsapp_brl, 1608.50, delta=0.01)
        self.assertAlmostEqual(r.total_caixa_brl, 1652.25, delta=0.01)
        self.assertNotAlmostEqual(r.total_caixa_brl, 1762.25, delta=1)

    def test_formula_ia(self):
        p = premissas_chatgpt()
        r = calcular(1000, p)
        self.assertAlmostEqual(r.custo_ia_brl, 1000 * (2000 * 0.10 + 500 * 0.60) / 1e6 * 5.5)

    def test_batch_corta_ia_pela_metade(self):
        p = premissas_chatgpt()
        a = calcular(1000, p).custo_ia_brl
        p["llm_usa_batch"] = True
        self.assertAlmostEqual(calcular(1000, p).custo_ia_brl, a / 2)

    def test_email_gratis_e_estouro_diario(self):
        p = copy.deepcopy(INTER)
        self.assertEqual(calcular(100, p).custo_email_brl, 0.0)  # 120 emails/mês
        r = calcular(3000, p)  # 3600 emails > 3000
        self.assertGreater(r.custo_email_brl, 0)
        self.assertTrue(any("E-mail excede" in a for a in r.alertas))
        # 2.400 e-mails/mês cabe no mensal mas não no diário (2400/22 > 100)
        r = calcular(2000, p)
        self.assertTrue(any("diário" in a for a in r.alertas))

    def test_custo_por_reuniao_e_por_lead(self):
        r = calcular(1000, INTER)
        self.assertAlmostEqual(r.reunioes, 1000 * 0.6 * 0.05 * 0.4)
        self.assertAlmostEqual(r.custo_por_reuniao_brl, r.total_caixa_brl / r.reunioes)
        self.assertAlmostEqual(r.custo_por_lead_brl, r.total_caixa_brl / 1000)

    def test_sem_reuniao_custo_infinito_e_alerta(self):
        p = copy.deepcopy(INTER)
        p["taxa_resposta"] = 0.0
        r = calcular(100, p)
        self.assertTrue(math.isinf(r.custo_por_reuniao_brl))
        self.assertTrue(r.alertas)

    def test_orcamento(self):
        self.assertTrue(calcular(100, INTER, orcamento_brl=250).cabe_no_orcamento)
        self.assertFalse(calcular(5000, DADOS["cenarios"]["conservador"], orcamento_brl=250).cabe_no_orcamento)

    def test_manutencao_separada_do_caixa(self):
        r = calcular(100, INTER)
        self.assertAlmostEqual(r.total_economico_brl - r.total_caixa_brl, 6 * 30)

    def test_simulacao_completa(self):
        rs = simular(DADOS)
        self.assertEqual(len(rs), 3 * 5)
        # custo cresce com volume dentro do cenário
        for cen in DADOS["cenarios"]:
            tot = [r.total_caixa_brl for r in rs if r.cenario == cen]
            self.assertEqual(tot, sorted(tot))

    def test_ponto_de_equilibrio(self):
        r = calcular(1000, INTER)
        pe = ponto_de_equilibrio(r, comissao_por_venda_brl=50, taxa_fechamento_reuniao=0.5)
        self.assertEqual(pe["vendas_para_empatar"], math.ceil(r.total_caixa_brl / 50))
        with self.assertRaises(PremissaInvalida):
            ponto_de_equilibrio(r, 0, 0.5)
        with self.assertRaises(PremissaInvalida):
            ponto_de_equilibrio(r, 50, 0)

    # ---- tratamento de erros ----
    def test_volume_invalido(self):
        for v in (0, -10, 10.5, "100", True):
            with self.subTest(v=v):
                with self.assertRaises(PremissaInvalida):
                    calcular(v, INTER)  # type: ignore[arg-type]

    def test_premissa_negativa_taxa_fora_e_ausente(self):
        for campo, valor in (("infra_mensal_brl", -1), ("taxa_resposta", 1.5),
                             ("cambio_brl_usd", 0), ("llm_usa_batch", "sim"),
                             ("preco_whatsapp_marketing_brl", float("nan"))):
            with self.subTest(campo=campo):
                p = copy.deepcopy(INTER)
                p[campo] = valor
                with self.assertRaises(PremissaInvalida):
                    calcular(100, p)
        p = copy.deepcopy(INTER)
        del p["valor_hora_brl"]
        with self.assertRaises(PremissaInvalida):
            calcular(100, p)

    def test_arquivo_sem_cenarios(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"cenarios": {}}, f)
        with self.assertRaises(PremissaInvalida):
            carregar_premissas(f.name)


if __name__ == "__main__":
    unittest.main()
