import json
import unittest
from datetime import datetime, timedelta, timezone

from kauan_ai.agenda import ServicoAgenda, StatusAgendamento
from kauan_ai.classificacao import validar_saida

INI = datetime(2026, 11, 10, 14, tzinfo=timezone.utc)
FIM = INI + timedelta(minutes=30)


class ProvedorFake:
    def __init__(self, livre=True, falhas=0):
        self.livre = livre
        self.falhas = falhas
        self.eventos = []

    def horario_livre(self, i, f):
        if self.falhas:
            self.falhas -= 1
            raise ConnectionError("calendar fora")
        return self.livre

    def criar_evento(self, i, f, t):
        self.eventos.append((i, f, t))
        return f"evt-{len(self.eventos)}"


class TestAgenda(unittest.TestCase):
    def test_sucesso_e_idempotencia(self):
        p = ProvedorFake()
        s = ServicoAgenda(p)
        a1 = s.agendar("11222333000181", INI, FIM, "Reunião")
        a2 = s.agendar("11222333000181", INI, FIM, "Reunião")
        self.assertEqual(a1.status, StatusAgendamento.CONFIRMADO)
        self.assertIs(a1, a2)
        self.assertEqual(len(p.eventos), 1)

    def test_falha_do_provedor_e_retentativa(self):
        p = ProvedorFake(falhas=1)
        s = ServicoAgenda(p)
        self.assertEqual(s.agendar("x", INI, FIM, "R").status, StatusAgendamento.FALHA)
        self.assertEqual(s.agendar("x", INI, FIM, "R").status, StatusAgendamento.CONFIRMADO)

    def test_escala_para_humano_apos_max_tentativas(self):
        s = ServicoAgenda(ProvedorFake(livre=False), max_tentativas=2)
        s.agendar("x", INI, FIM, "R")
        a = s.agendar("x", INI, FIM, "R")
        self.assertEqual(a.status, StatusAgendamento.ESCALADO_HUMANO)
        self.assertIn("horario_ocupado", a.erros)

    def test_intervalo_invalido(self):
        with self.assertRaises(ValueError):
            ServicoAgenda(ProvedorFake()).agendar("x", FIM, INI, "R")


class TestClassificacao(unittest.TestCase):
    def ok(self, **kw):
        d = {"intencao": "QUER_AGENDAR", "icp": "DENTRO", "confianca": 0.9,
             "justificativa": "Pediu horário"}
        d.update(kw)
        return json.dumps(d)

    def test_saida_valida(self):
        s = validar_saida(self.ok())
        self.assertTrue(s.valida)
        self.assertEqual(s.status, "OK")

    def test_json_quebrado(self):
        s = validar_saida("Claro! Aqui está: {intencao: ...")
        self.assertFalse(s.valida)
        self.assertEqual(s.status, "FALHA_CLASSIFICACAO")

    def test_valores_fora_do_dominio(self):
        for kw in ({"intencao": "TALVEZ"}, {"icp": "SIM"}, {"confianca": 1.5},
                   {"confianca": "alta"}, {"confianca": True}, {"justificativa": ""}):
            with self.subTest(kw=kw):
                self.assertEqual(validar_saida(self.ok(**kw)).status, "FALHA_CLASSIFICACAO")

    def test_baixa_confianca_vai_para_humano(self):
        self.assertEqual(validar_saida(self.ok(confianca=0.5)).status, "REVISAO_HUMANA")

    def test_oposicao_detectada_obriga_descadastro(self):
        self.assertEqual(validar_saida(self.ok(intencao="OPOSICAO")).status, "REGISTRAR_OPOSICAO")

    def test_nao_objeto(self):
        self.assertEqual(validar_saida("[1,2]").status, "FALHA_CLASSIFICACAO")


if __name__ == "__main__":
    unittest.main()
