import unittest

from kauan_ai import cnpj


class TestCNPJ(unittest.TestCase):
    def test_numerico_valido_com_e_sem_mascara(self):
        self.assertEqual(cnpj.validar("11.222.333/0001-81"), "11222333000181")
        self.assertEqual(cnpj.validar("11222333000181"), "11222333000181")

    def test_alfanumerico_exemplo_oficial_receita(self):
        # Exemplo publicado pela Receita Federal para o CNPJ alfanumérico
        self.assertEqual(cnpj.validar("12.ABC.345/01DE-35"), "12ABC34501DE35")
        self.assertEqual(cnpj.validar("12abc34501de35"), "12ABC34501DE35")

    def test_dv_errado(self):
        with self.assertRaises(cnpj.CNPJInvalido):
            cnpj.validar("11.222.333/0001-82")
        with self.assertRaises(cnpj.CNPJInvalido):
            cnpj.validar("12.ABC.345/01DE-36")

    def test_formato_invalido(self):
        for ruim in ["", "123", "11222333000181999", "11.222.333/0001-8X", "1122233300@181"]:
            with self.subTest(ruim=ruim):
                self.assertFalse(cnpj.eh_valido(ruim))

    def test_sequencia_repetida(self):
        self.assertFalse(cnpj.eh_valido("00000000000000"))
        self.assertFalse(cnpj.eh_valido("11111111111111"))

    def test_tipo_errado(self):
        with self.assertRaises(cnpj.CNPJInvalido):
            cnpj.validar(11222333000181)  # type: ignore[arg-type]

    def test_formatar_e_raiz(self):
        self.assertEqual(cnpj.formatar("11222333000181"), "11.222.333/0001-81")
        self.assertEqual(cnpj.raiz("11.222.333/0001-81"), "11222333")


if __name__ == "__main__":
    unittest.main()
