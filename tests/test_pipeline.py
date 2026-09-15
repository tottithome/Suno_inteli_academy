from graph.pipeline import build_graph


def test_pipeline_roda_na_amostra():
    grafo = build_graph()
    estado = grafo.invoke(
        {
            "source_text": (
                "O Copom manteve a Selic. O comunicado cita forward guidance, "
                "hiato do produto e a curva de juros."
            ),
            "retries": 0,
        }
    )
    assert estado["anchors"]["n_frases"] >= 1
    assert "iniciante" in estado["adaptations"]
    assert "artigo" in estado["outputs"]["iniciante"]
    assert "iniciante" in estado["eval_reports"]
