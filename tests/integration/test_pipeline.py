"""Integration test: full pipeline end-to-end with a catalog route."""

import os
import tempfile


def test_full_pipeline_mo():
    """Run full pipeline for MO_DMPD_to_TCA and verify results."""
    from mrhp.config.loader import load_config
    from mrhp.core.pipeline import run_single

    # Find config
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    cfg_path = os.path.join(repo_root, "configs", "shewanella_mo.yaml")

    if not os.path.isfile(cfg_path):
        import pytest
        pytest.skip("Config file not found")

    cfg = load_config(cfg_path)
    # Use full bridge mode — V5 params were calibrated for full model
    cfg.setdefault("bridge", {})["mode"] = "full"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_single(cfg, cfg_path, tmpdir)

    assert "score" in result, f"Pipeline error: {result.get('error')}"
    score = result["score"]
    assert score["sync_score"] > 0
    assert score["classification"] != ""
    assert result["bridge_eval"]["R2_bridge_vs_v4"] > 0.5
