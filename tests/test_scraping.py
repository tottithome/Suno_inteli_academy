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


def test_auto_noticias_nao_roda_se_tem_texto():
    texto, aviso = extrair_texto(None, "fonte local", None, auto_noticias=True)
    assert texto == "fonte local"
    assert aviso == ""
