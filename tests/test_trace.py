"""The traceability script reads this repository's spec (REQ-110)."""

import subprocess
import sys

import pytest


@pytest.mark.req("REQ-110")
def test_trace_report_prints_the_matrix(root):
    out = subprocess.run(
        [sys.executable, str(root / "scripts" / "trace.py"), "--report-only"],
        capture_output=True, text=True, check=False,
    )
    assert out.returncode == 0, out.stdout[-400:]
    assert "REQ-111  MUST" in out.stdout
    assert "0 errors" in out.stdout


@pytest.mark.req("REQ-110")
def test_trace_fails_on_an_untested_must_in_strict_mode(root, tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("| REQ-001 | MUST | x |\n\n### 11.1 Scope\n\n| a | REQ-001 |\n", encoding="utf-8")
    (tmp_path / "t").mkdir()
    out = subprocess.run(
        [sys.executable, str(root / "scripts" / "trace.py"), "--spec", str(spec), "--tests", str(tmp_path / "t")],
        capture_output=True, text=True, check=False,
    )
    assert out.returncode == 1
    assert "NO TEST" in out.stdout
