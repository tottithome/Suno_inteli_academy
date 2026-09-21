from adapters.personas import adaptar


def test_adaptar_sem_api_usa_rascunho_da_fonte():
    texto, aviso = adaptar("iniciante", "O Copom manteve a Selic em 10,75%.", {}, [])
    assert "selic" in texto.casefold()
    assert aviso
