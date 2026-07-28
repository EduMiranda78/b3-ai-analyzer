from pathlib import Path


def test_prompt_e_curto_e_possui_placeholder():
    prompt = Path(
        "prompt_analise.txt"
    ).read_text(
        encoding="utf-8"
    )

    assert prompt.count(
        "{dados_do_ativo}"
    ) == 1

    assert len(prompt.split()) <= 250

    assert (
        "SINALIZAÇÃO FINAL"
        in prompt
    )

    assert "Não invente" in prompt
