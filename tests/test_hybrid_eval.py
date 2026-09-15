from eval.hybrid import avaliar


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
