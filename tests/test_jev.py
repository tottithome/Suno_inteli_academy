from contracts.models import Anchors
from eval.jev import julgar, montar_estado


def test_montar_estado_usa_ancoras():
    estado = montar_estado(
        "Selic em 10,75%.",
        "iniciante",
        Anchors(numeros_chave=["10,75%"], frases_ancora=["O Copom manteve a Selic."]),
    )
    assert estado["audiencia_alvo"] == "iniciante"
    assert "10,75%" in estado["numeros_chave"]


def test_julgar_pula_sem_chave(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    veredito = julgar("texto", "iniciante")
    assert veredito.pulou is True
