from formats.synthesizers import _carrossel_local, _parse_formatos, _roteiro_local


def test_parse_blocos_rotulados():
    bruto = "===CARROSSEL===\nSlide 1: gancho\n===ROTEIRO===\n[0-3s] ola"
    dados = _parse_formatos(bruto)
    assert dados["carrossel"].startswith("Slide 1")
    assert "[0-3s]" in dados["roteiro"]


def test_parse_sem_marcadores():
    bruto = "Slide 1: gancho\nSlide 2: corpo\n[0-3s] ola\n[3-20s] explica"
    dados = _parse_formatos(bruto)
    assert "Slide 1" in dados["carrossel"]
    assert "[3-20s]" in dados["roteiro"]


def test_parse_so_com_slides_monta_roteiro():
    bruto = "Slide 1: CVM apresenta Otto Lobo\nSlide 2: Foco em tecnologia e fiscalizacao"
    dados = _parse_formatos(bruto)
    assert "Slide 2" in dados["carrossel"]
    assert "[45-60s]" in dados["roteiro"]
    assert "Fatos da fonte" not in dados["roteiro"]


def test_parse_json_de_formatos():
    bruto = '{"carrossel": "Slide 1: gancho", "roteiro": "[0-3s] ola"}'
    dados = _parse_formatos(bruto)
    assert dados["carrossel"].startswith("Slide 1")
    assert "[0-3s]" in dados["roteiro"]


def test_fallback_local_tem_estrutura():
    texto = "A CVM apresentou o novo presidente. O foco e fiscalizacao."
    assert "Slide 1" in _carrossel_local(texto, "iniciante")
    assert "[0-3s]" in _roteiro_local(texto, "iniciante")
