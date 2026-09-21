from adapters.personas import adaptar, saida_invalida


def test_adaptar_sem_api_usa_rascunho_da_fonte():
    texto, aviso = adaptar("iniciante", "O Copom manteve a Selic em 10,75%.", {}, [])
    assert "selic" in texto.casefold()
    assert aviso


def test_detecta_raciocinio_em_ingles():
    assert saida_invalida("We need to adapt the document for a beginner persona")
    assert not saida_invalida("A CVM apresentou o novo presidente ao mercado.")
