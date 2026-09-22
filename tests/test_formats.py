from formats.synthesizers import _carrossel_local, _parse_formatos, _roteiro_local


def test_parse_blocos_rotulados():
    bruto = "===CARROSSEL===\nSlide 1: gancho\n===ROTEIRO===\n[0-3s] ola"
    dados = _parse_formatos(bruto)
    assert dados["carrossel"].startswith("Slide 1")
    assert "[0-3s]" in dados["roteiro"]


def test_parse_json_de_formatos():
    bruto = '{"carrossel": "Slide 1: gancho", "roteiro": "[0-3s] ola"}'
    dados = _parse_formatos(bruto)
    assert dados["carrossel"].startswith("Slide 1")
    assert "[0-3s]" in dados["roteiro"]


def test_fallback_local_tem_estrutura():
    texto = "A CVM apresentou o novo presidente. O foco e fiscalizacao."
    assert "Slide 1" in _carrossel_local(texto, "iniciante")
    assert "[0-3s]" in _roteiro_local(texto, "iniciante")
