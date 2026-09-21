from extract.anchor import extrair_texto
from scraping.news import url_parece_artigo


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


def test_rejeita_listagem_e_aceita_slug():
    assert url_parece_artigo("https://www.gov.br/cvm/pt-br/assuntos/noticias/2026") is False
    assert url_parece_artigo(
        "https://www.gov.br/cvm/pt-br/assuntos/noticias/2026/suspensao-de-ofertas"
    )
    assert url_parece_artigo(
        "https://www.gov.br/cvm/pt-br/centrais-de-conteudo/atas-de-comites"
    ) is False
