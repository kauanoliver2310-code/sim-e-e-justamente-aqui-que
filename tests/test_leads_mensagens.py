import unittest
from datetime import datetime, timedelta, timezone

from kauan_ai.cnpj import CNPJInvalido
from kauan_ai.leads import (
    BaseLegal, BaseLegalAusente, CadastroLeads, Lead, LeadDuplicado, LeadSuprimido, OrigemLead,
)
from kauan_ai.mensagens import Canal, MensagemDuplicada, Outbox, StatusMensagem

T0 = datetime(2026, 11, 6, 9, tzinfo=timezone.utc)
CNPJ = "11.222.333/0001-81"


def novo_lead(cnpj=CNPJ, **kw):
    base = dict(cnpj=cnpj, razao_social="Padaria Teste LTDA", origem=OrigemLead.INBOUND_WHATSAPP,
                base_legal=BaseLegal.PROCEDIMENTOS_PRELIMINARES, criado_em=T0,
                telefone="+55 11 99999-0000", email="dono@padaria.com.br")
    base.update(kw)
    return Lead(**base)


class TestLeads(unittest.TestCase):
    def setUp(self):
        self.cad = CadastroLeads()

    def test_cnpj_invalido_rejeitado(self):
        with self.assertRaises(CNPJInvalido):
            self.cad.adicionar(novo_lead(cnpj="11.222.333/0001-00"))

    def test_cnpj_duplicado_com_mascara_diferente(self):
        self.cad.adicionar(novo_lead())
        with self.assertRaises(LeadDuplicado):
            self.cad.adicionar(novo_lead(cnpj="11222333000181"))
        self.assertEqual(len(self.cad), 1)

    def test_duplicado_pode_atualizar_sem_criar_outro(self):
        self.cad.adicionar(novo_lead(email=None))
        self.cad.adicionar(novo_lead(email="novo@padaria.com.br"), atualizar_se_existir=True)
        self.assertEqual(len(self.cad), 1)
        self.assertEqual(self.cad.obter(CNPJ).email, "novo@padaria.com.br")

    def test_legitimo_interesse_exige_lia(self):
        with self.assertRaises(BaseLegalAusente):
            self.cad.adicionar(novo_lead(origem=OrigemLead.DADOS_ABERTOS_CNPJ,
                                         base_legal=BaseLegal.LEGITIMO_INTERESSE))
        self.cad.adicionar(novo_lead(origem=OrigemLead.DADOS_ABERTOS_CNPJ,
                                     base_legal=BaseLegal.LEGITIMO_INTERESSE, lia_referencia="LIA-001"))

    def test_oposicao_elimina_dados_e_impede_recadastro(self):
        self.cad.adicionar(novo_lead())
        self.cad.registrar_oposicao(cnpj=CNPJ, telefone="+55 11 99999-0000", canal="WHATSAPP", em=T0)
        self.assertIsNone(self.cad.obter(CNPJ))
        self.assertEqual([e["evento"] for e in self.cad.eventos_lgpd], ["OPOSICAO", "DADOS_ELIMINADOS"])
        with self.assertRaises(LeadSuprimido):
            self.cad.adicionar(novo_lead())

    def test_supressao_por_telefone_ignora_formatacao(self):
        self.cad.registrar_oposicao(telefone="(11) 99999-0000")
        self.assertTrue(self.cad.esta_suprimido(telefone="11999990000"))

    def test_oposicao_sem_identificador_erro(self):
        with self.assertRaises(ValueError):
            self.cad.registrar_oposicao()

    def test_retencao_descarta_lead_sem_interacao(self):
        self.cad.adicionar(novo_lead())
        removidos = self.cad.aplicar_retencao(T0 + timedelta(days=181))
        self.assertEqual(removidos, ["11222333000181"])
        self.assertEqual(self.cad.eventos_lgpd[-1]["evento"], "DESCARTE_RETENCAO")


class FalhaUmaVez:
    def __init__(self):
        self.chamadas = 0

    def enviar(self, m):
        self.chamadas += 1
        if self.chamadas == 1:
            raise TimeoutError("provedor fora")
        return "ok-ref"


class TestOutbox(unittest.TestCase):
    def setUp(self):
        self.cad = CadastroLeads()
        self.cad.adicionar(novo_lead())
        self.out = Outbox(self.cad)

    def _rascunho(self, etapa="abertura", canal=Canal.WHATSAPP, destino="+5511999990000"):
        return self.out.criar_rascunho("11222333000181", canal, destino, "Olá!", "maquininha-nov", etapa)

    def test_mensagem_duplicada_bloqueada(self):
        self._rascunho()
        with self.assertRaises(MensagemDuplicada):
            self._rascunho()

    def test_sem_aprovacao_humana_nao_envia(self):
        m = self._rascunho()
        with self.assertRaises(PermissionError):
            self.out.enviar(m.chave)

    def test_envio_simulado_e_idempotente(self):
        m = self._rascunho()
        self.out.aprovar(m.chave, "kauan")
        self.out.enviar(m.chave, T0)
        self.out.enviar(m.chave, T0)  # reprocessamento
        self.assertEqual(len(self.out.enviador.enviadas), 1)
        self.assertEqual(self.out.obter(m.chave).status, StatusMensagem.ENVIADA)

    def test_oposicao_bloqueia_envio_aprovado(self):
        m = self._rascunho()
        self.out.aprovar(m.chave, "kauan")
        self.cad.registrar_oposicao(telefone="+5511999990000")
        self.assertEqual(self.out.enviar(m.chave, T0).status, StatusMensagem.BLOQUEADA)
        self.assertEqual(len(self.out.enviador.enviadas), 0)

    def test_falha_de_envio_e_reprocessamento(self):
        out = Outbox(self.cad, enviador=FalhaUmaVez())
        m = out.criar_rascunho("11222333000181", Canal.EMAIL, "dono@padaria.com.br", "Oi", "c1", "e1")
        out.aprovar(m.chave, "kauan")
        self.assertEqual(out.enviar(m.chave, T0).status, StatusMensagem.FALHA)
        out.reprocessar_falhas(T0)
        self.assertEqual(out.obter(m.chave).status, StatusMensagem.ENVIADA)
        self.assertEqual(out.enviador.chamadas, 2)

    def test_limite_diario_de_email(self):
        out = Outbox(self.cad, limite_diario_email=1)
        a = out.criar_rascunho("11222333000181", Canal.EMAIL, "a@x.com", "Oi", "c", "1")
        b = out.criar_rascunho("11222333000181", Canal.EMAIL, "a@x.com", "Oi", "c", "2")
        for m in (a, b):
            out.aprovar(m.chave, "kauan")
        out.enviar(a.chave, T0)
        with self.assertRaises(RuntimeError):
            out.enviar(b.chave, T0)


if __name__ == "__main__":
    unittest.main()
