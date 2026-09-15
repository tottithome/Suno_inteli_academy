from eval.readability import flesch_portugues


def test_texto_simples_tem_flesch_mais_alto():
    facil = (
        "O banco central mudou os juros. Isso deixa o crédito mais caro. "
        "Quem tem dívida no cartão sente o efeito no bolso."
    )
    dificil = (
        "A calibragem da política monetária internaliza a inércia inflacionária "
        "e a assimetria do canal de crédito sob um regime de metas."
    )
    assert flesch_portugues(facil).flesch_pt > flesch_portugues(dificil).flesch_pt
