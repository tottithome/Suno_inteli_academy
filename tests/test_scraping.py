from extract.anchor import extrair_texto


def test_url_invalida_quebra():
    try:
        extrair_texto(None, None, "ftp://x")
    except ValueError:
        return
    raise AssertionError("esperava ValueError")


def test_texto_ganha_da_url():
    texto, aviso = extrair_texto(None, "Selic em 10%.", "https://example.com")
    assert texto.startswith("Selic")
    assert aviso == ""
