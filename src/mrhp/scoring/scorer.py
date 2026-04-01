"""Multi-hypothesis scoring and ranking."""

import os

import numpy as np

from mrhp.io.writers import write_json, write_tsv, safe_div


def score_hypothesis(route, sim_analysis, bridge_eval, validation, omics_evidence):
    """Compute synchronization score across all layers."""
    scores = {}
    weights = {
        "metabolism": 0.25,
        "bridge": 0.25,
        "expression": 0.30,
        "omics": 0.20,
    }

    if sim_analysis:
        tca_met = any(sim_analysis.get(k, 0) > 0.01
                      for k in ("succinylCoA_final", "acetylCoA_final"))
        nadh_consumed = sim_analysis.get("NADH_consumed", 0) > 0
        met_score = 1.0
        if sim_analysis.get("bottleneck_avg_rate", 1.0) < 0.01:
            met_score -= 0.3
        if not tca_met:
            met_score -= 0.3
        if not nadh_consumed:
            met_score -= 0.2
        scores["metabolism"] = max(0.0, met_score)
    else:
        scores["metabolism"] = 0.0

    if bridge_eval:
        r2 = bridge_eval.get("R2_bridge_vs_v4", 0.0)
        scores["bridge"] = max(0.0, min(1.0, r2))
    else:
        scores["bridge"] = 0.0

    if validation and validation.get("status") == "VALIDATED":
        dir_acc = validation.get("direction_accuracy", 0.0)
        mag_err = validation.get("mean_magnitude_error_log2", 5.0)
        expr_score = dir_acc * 0.7 + max(0.0, 1.0 - mag_err / 5.0) * 0.3
        scores["expression"] = max(0.0, min(1.0, expr_score))
    else:
        scores["expression"] = 0.0

    if omics_evidence:
        omics_sub = []
        if "nmr" in omics_evidence:
            omics_sub.append(omics_evidence["nmr"].get("coverage", 0.0))
        if "redox" in omics_evidence:
            omics_sub.append(1.0 if omics_evidence["redox"].get("balance_ok") else 0.0)
        if "gene_coverage" in omics_evidence:
            omics_sub.append(omics_evidence["gene_coverage"].get("coverage", 0.0))
        scores["omics"] = float(np.mean(omics_sub)) if omics_sub else 0.0
    else:
        scores["omics"] = 0.0

    total = sum(scores[k] * weights[k] for k in weights)

    return {
        "route_id": route.get("route_id", "unknown"),
        "dye_code": route.get("dye_code", ""),
        "scores": scores,
        "weights": weights,
        "sync_score": round(total, 4),
        "classification": validation.get("classification", "UNKNOWN") if validation else "UNKNOWN",
        "confidence": route.get("overall_confidence"),
    }


def rank_hypotheses(all_results):
    """Rank multiple hypothesis results by synchronization score."""
    if not all_results:
        return []
    ranked = sorted(all_results, key=lambda x: x["sync_score"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    return ranked


def iterate_hypotheses(cfg_list, runner_fn):
    """Run the platform on multiple configs and rank results."""
    results = []
    for cfg in cfg_list:
        try:
            result = runner_fn(cfg)
            if result and "score" in result:
                results.append(result["score"])
        except Exception as e:
            results.append({
                "route_id": cfg.get("route_hypothesis", {}).get("route_id", "error"),
                "sync_score": 0.0,
                "error": str(e),
            })
    return rank_hypotheses(results)


def export_ranking(ranked, output_dir):
    """Export hypothesis ranking."""
    headers = ["Rank", "Route_ID", "Dye", "Sync_Score", "Metabolism", "Bridge",
               "Expression", "Omics", "Classification"]
    rows = []
    for r in ranked:
        sc = r.get("scores", {})
        rows.append([
            str(r.get("rank", "-")),
            r.get("route_id", ""),
            r.get("dye_code", ""),
            f"{r.get('sync_score', 0):.4f}",
            f"{sc.get('metabolism', 0):.3f}",
            f"{sc.get('bridge', 0):.3f}",
            f"{sc.get('expression', 0):.3f}",
            f"{sc.get('omics', 0):.3f}",
            r.get("classification", ""),
        ])
    write_tsv(os.path.join(output_dir, "hypothesis_ranking.tsv"), headers, rows)
    write_json(os.path.join(output_dir, "hypothesis_ranking.json"), ranked)
