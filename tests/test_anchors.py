from contracts.models import Anchors
from extract.anchor import extrair_ancoras


def test_ancoras_viram_contrato():
    dados = extrair_ancoras("O Copom manteve a Selic em 10,75%. O IPCA segue acima da meta.")
    ancora = Anchors.model_validate(dados)
    assert ancora.n_frases >= 1
    assert any("10" in n for n in ancora.numeros_chave)
