from glossary.finance_terms import analogia_presente, termos_no_texto
from eval.term_density import densidade_terminologica


def test_detecta_selic_e_analogia():
    texto = "A taxa Selic e o juros basico do pais e mexe no credito."
    termos = termos_no_texto(texto)
    assert any(t.canonical == "selic" for t in termos)
    assert analogia_presente(texto, termos[0])


def test_densidade_iniciante_marca_jargao_avancado():
    texto = "O hiato do produto esta positivo."
    score = densidade_terminologica(texto, "iniciante")
    assert "hiato do produto" in score.termos_acima_do_nivel
    assert "hiato do produto" in score.jargao_sem_analogia
