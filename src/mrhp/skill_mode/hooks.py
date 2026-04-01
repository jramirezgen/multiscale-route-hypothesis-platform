"""Skill-mode / AI-assisted hooks for MRHP.

Provides structured entry points that automated agents can call
to run, compare, or inspect hypotheses without CLI parsing.
"""

from mrhp.config.loader import load_config
from mrhp.core.pipeline import run_single, run_pipeline


def hook_run(config_path, base_dir=None):
    """Run a full pipeline evaluation returning structured results.

    Parameters
    ----------
    config_path : str
        Path to YAML config.
    base_dir : str, optional
        Output directory root.

    Returns
    -------
    dict
        Pipeline result dict with score, route, bridge_eval, etc.
    """
    return run_pipeline(config_path, base_dir=base_dir)


def hook_compare(config_a_path, config_b_path, base_dir=None):
    """Compare two hypotheses and return structured comparison.

    Returns
    -------
    dict
        Keys: winner, sync_a, sync_b, scores_a, scores_b, etc.
    """
    import os
    cfg_a = load_config(config_a_path)
    cfg_b = load_config(config_b_path)
    bd = base_dir or os.path.dirname(config_a_path)
    res_a = run_single(cfg_a, config_a_path, bd)
    res_b = run_single(cfg_b, config_b_path, bd)

    score_a = res_a.get("score", {})
    score_b = res_b.get("score", {})
    sync_a = score_a.get("sync_score", 0)
    sync_b = score_b.get("sync_score", 0)

    return {
        "route_a": res_a.get("route_id"),
        "route_b": res_b.get("route_id"),
        "sync_a": sync_a,
        "sync_b": sync_b,
        "classification_a": score_a.get("classification"),
        "classification_b": score_b.get("classification"),
        "scores_a": score_a.get("scores", {}),
        "scores_b": score_b.get("scores", {}),
        "winner": res_a.get("route_id") if sync_a >= sync_b else res_b.get("route_id"),
        "result_a": res_a,
        "result_b": res_b,
    }


def hook_doctor(config_path):
    """Run diagnostics on a config, return structured report.

    Returns
    -------
    dict
        Keys: ok (list), warnings (list), issues (list), verdict (str).
    """
    from mrhp.models.frozen import (ALL_ROUTES, V4_PARAMS, BRIDGE_V5_PARAMS,
                                     EXPRESSION_CALIBRATIONS)

    issues = []
    warnings = []
    ok = []

    try:
        cfg = load_config(config_path)
        ok.append("Config loaded")
    except Exception as e:
        return {"ok": [], "warnings": [], "issues": [f"Config load FAILED: {e}"],
                "verdict": "FAIL"}

    for key in ["organism", "target", "route_hypothesis"]:
        if key in cfg:
            ok.append(f"Key '{key}' present")
        else:
            issues.append(f"Missing: '{key}'")

    hyp = cfg.get("route_hypothesis", {})
    route_id = hyp.get("route_id", "")
    dye_code = hyp.get("dye_code", "")

    if route_id:
        if route_id in ALL_ROUTES:
            ok.append(f"Route '{route_id}' in catalog")
        elif hyp.get("steps"):
            ok.append(f"Route '{route_id}' custom YAML")
        else:
            issues.append(f"Route '{route_id}' not found")

    if dye_code:
        if dye_code in V4_PARAMS:
            ok.append(f"V4 params for '{dye_code}'")
        else:
            warnings.append(f"No V4 params for '{dye_code}'")
        calib = [c[0] for c in EXPRESSION_CALIBRATIONS if c[1] == dye_code]
        if calib:
            ok.append(f"{len(calib)} calibrations for '{dye_code}'")
        else:
            warnings.append(f"No calibrations for '{dye_code}'")

    if issues:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "OK"

    return {"ok": ok, "warnings": warnings, "issues": issues, "verdict": verdict}


def hook_list_routes():
    """List all available routes in the frozen catalog.

    Returns
    -------
    dict
        Mapping route_id -> {n_steps, convergence, description}.
    """
    from mrhp.models.frozen import ALL_ROUTES

    result = {}
    for rid, rdata in ALL_ROUTES.items():
        steps = rdata.get("steps", [])
        result[rid] = {
            "n_steps": len(steps),
            "convergence": rdata.get("convergence", "?"),
            "description": rdata.get("description", ""),
        }
    return result


def hook_score_only(config_path, base_dir=None):
    """Run pipeline and return only the score dict."""
    result = hook_run(config_path, base_dir=base_dir)
    return result.get("score", {})
