from eval.hybrid import avaliar
from contracts.models import JevVerdict


def test_iniciante_rejeita_jargao_sem_analogia():
    texto = (
        "O forward guidance e o hiato do produto mudam a taxa terminal "
        "na curva de juros sem explicar nada ao leitor leigo."
    )
    relatorio = avaliar(texto, "iniciante")
    assert relatorio.passou is False
    assert relatorio.falhas


def test_avancado_aceita_jargao_tecnico():
    texto = (
        "O forward guidance ancora as expectativas em torno da taxa terminal, "
        "enquanto o hiato do produto e a curva de juros informam o ciclo. "
        "Covenants e EBITDA ajustado descrevem o canal de crédito corporativo "
        "sob a Selic vigente e o CDI de referência, com o IPCA ainda acima da meta."
    )
    relatorio = avaliar(texto, "avancado")
    assert "jargão sem analogia" not in " ".join(relatorio.falhas)


def test_jev_reprova_nivel_errado():
    jev = JevVerdict(
        nivel_aparente="avancado",
        nivel_confianca=0.9,
        falhas=["Jev: nivel aparente avancado != alvo iniciante"],
    )
    relatorio = avaliar("O banco mudou os juros basicos do pais.", "iniciante", jev=jev)
    assert relatorio.passou is False
    assert any("Jev" in f for f in relatorio.falhas)
