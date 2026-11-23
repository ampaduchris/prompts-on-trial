import tomllib

import prompts_on_trial


def test_version_matches_pyproject(root):
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert prompts_on_trial.__version__ == data["project"]["version"]
