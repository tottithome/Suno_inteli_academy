from adapters.personas import adaptar


def test_adaptar_sem_api_usa_rascunho():
    texto = adaptar("iniciante", "O Copom manteve a Selic em 10,75%.", {}, [])
    assert "juros" in texto.casefold() or "selic" in texto.casefold()
