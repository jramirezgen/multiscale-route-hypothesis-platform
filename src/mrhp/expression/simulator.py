"""Expression simulation (ODE v3) and RT-qPCR validation."""

import os

import numpy as np
from scipy.integrate import solve_ivp

from mrhp.models.frozen import (
    V4_PARAMS, EXPRESSION_V3, EXPRESSION_CALIBRATIONS,
    RTQPCR_RAW, REFERENCE_GENES,
)
from mrhp.io.writers import write_json, write_tsv, safe_div


# ═══════════════════════════════════════════════════════════════
# EXPRESSION SIMULATION
# ═══════════════════════════════════════════════════════════════

def simulate_expression(cfg, route, bridge_result=None):
    """Simulate gene expression for all genes using ODE v3."""
    dye_code = route.get("dye_code", "")
    expr_cfg = cfg.get("expression", {})
    if not expr_cfg.get("enabled", True):
        return None

    genes_key = expr_cfg.get("genes_key", [])
    if not genes_key:
        genes_key = route.get("all_genes", [])
    calib_genes = {c[0] for c in EXPRESSION_CALIBRATIONS
                   if c[1] == _map_dye_to_calib(dye_code)}
    all_genes = sorted(set(genes_key) | calib_genes)

    if not all_genes:
        return None

    if dye_code not in V4_PARAMS:
        return None

    context = cfg.get("context", {})
    v4p = V4_PARAMS[dye_code]
    K_yc = V4_PARAMS["K_yc"]
    K_dic = V4_PARAMS["K_dic"]
    yc = context.get("yc", 3.0)
    dic = context.get("dic", 0.6)

    Dmax = v4p["Dmax"]
    Vmax = v4p["Vmax"]
    n_hill = v4p["n"]
    lag = v4p["lag"]
    h_SI = (yc**n_hill / (K_yc**n_hill + yc**n_hill)) * (K_dic / (K_dic + dic))

    beta_m = EXPRESSION_V3["beta_m"]
    beta_p = EXPRESSION_V3["beta_p"]
    delta_m = EXPRESSION_V3["delta_m"]
    delta_p = EXPRESSION_V3["delta_p"]
    sigma = EXPRESSION_V3["sigma"]
    P_BASAL_SS = EXPRESSION_V3["P_BASAL_SS"]

    t_max = context.get("t_max", 48.0)
    dt = 1.0 if expr_cfg.get("simulate_hourly", True) else 0.5
    t_eval = np.arange(0, t_max + dt, dt)

    def D_prime(t):
        t_eff = max(t - lag, 0)
        if t > lag:
            return Dmax * Vmax * h_SI * np.exp(-Vmax * h_SI * t_eff)
        return 0.0

    calib_map = _calib_map_for_dye(dye_code)
    gene_results = {}

    for gene in all_genes:
        alpha = calib_map.get(gene, {}).get("alpha", 0.0)
        t_onset = calib_map.get(gene, {}).get("t_onset", 0.0)

        m_basal_ss = delta_p * P_BASAL_SS / beta_p if beta_p > 0 else 0.0

        def ode_expr(t, state, _alpha=alpha, _t_onset=t_onset):
            m, p = state
            dD = D_prime(t) if t >= _t_onset else 0.0
            signal = _alpha * dD / (1.0 + (dD / sigma) ** 2)
            dm = beta_m * signal - delta_m * m
            dp = beta_p * m - delta_p * p
            return [dm, dp]

        sol = solve_ivp(ode_expr, (0, t_max), [m_basal_ss, P_BASAL_SS],
                        t_eval=t_eval, method="RK45", rtol=1e-8, atol=1e-10)

        mRNA = sol.y[0]
        protein = np.maximum(sol.y[1], 1e-12)
        FC = protein / P_BASAL_SS if P_BASAL_SS > 0 else protein

        gene_results[gene] = {
            "t": sol.t.tolist(),
            "mRNA": mRNA.tolist(),
            "protein": protein.tolist(),
            "FC": FC.tolist(),
            "FC_final": float(FC[-1]),
            "alpha": alpha,
            "t_onset": t_onset,
            "calib_obs_fc": calib_map.get(gene, {}).get("obs_fc"),
            "calib_model_fc": calib_map.get(gene, {}).get("model_fc"),
            "calib_grade": calib_map.get(gene, {}).get("grade"),
        }

    return {
        "genes": gene_results,
        "dye_code": dye_code,
        "t_eval": t_eval.tolist(),
        "n_genes": len(gene_results),
    }


def _map_dye_to_calib(dye_code):
    return dye_code


def _calib_map_for_dye(dye_code):
    calib_label = _map_dye_to_calib(dye_code)
    result = {}
    for gene, dye, alpha, t_onset, obs_fc, model_fc, grade in EXPRESSION_CALIBRATIONS:
        if dye == calib_label:
            result[gene] = {
                "alpha": alpha, "t_onset": t_onset,
                "obs_fc": obs_fc, "model_fc": model_fc, "grade": grade,
            }
    return result


def build_hourly_table(expr_result):
    if expr_result is None:
        return "", []

    genes = expr_result["genes"]
    t_eval = expr_result["t_eval"]
    gene_names = sorted(genes.keys())

    headers = ["Hour"] + [f"{g}_mRNA" for g in gene_names] + [f"{g}_FC" for g in gene_names]
    rows = []
    for ti, t in enumerate(t_eval):
        row = [f"{t:.0f}"]
        for g in gene_names:
            row.append(f"{genes[g]['mRNA'][ti]:.4f}")
        for g in gene_names:
            row.append(f"{genes[g]['FC'][ti]:.2f}")
        rows.append(row)

    return headers, rows


# ═══════════════════════════════════════════════════════════════
# RT-qPCR VALIDATION
# ═══════════════════════════════════════════════════════════════

def compute_rtqpcr_fc(dye_code):
    """Compute \u0394\u0394Ct fold-changes from raw RT-qPCR data."""
    dye_to_cond = {"MO": ["MO"], "RC": ["CR", "RC"], "DB": ["AD"]}
    conditions = dye_to_cond.get(dye_code, [dye_code])

    results = {}

    ref_ct_zz = []
    for rg in REFERENCE_GENES:
        if rg in RTQPCR_RAW and "ZZ" in RTQPCR_RAW[rg]:
            ref_ct_zz.extend(RTQPCR_RAW[rg]["ZZ"])

    for gene, cond_data in RTQPCR_RAW.items():
        if gene in REFERENCE_GENES:
            continue

        ct_zz = cond_data.get("ZZ", [])
        mean_ct_zz = np.mean(ct_zz) if ct_zz else None

        ct_dye = []
        for c in conditions:
            if c in cond_data:
                ct_dye.extend(cond_data[c])
        mean_ct_dye = np.mean(ct_dye) if ct_dye else None

        if mean_ct_zz is not None and mean_ct_dye is not None:
            ref_zz_vals = []
            ref_dye_vals = []
            for rg in REFERENCE_GENES:
                if rg in RTQPCR_RAW:
                    if "ZZ" in RTQPCR_RAW[rg]:
                        ref_zz_vals.extend(RTQPCR_RAW[rg]["ZZ"])
                    for c in conditions:
                        if c in RTQPCR_RAW[rg]:
                            ref_dye_vals.extend(RTQPCR_RAW[rg][c])

            ref_zz_mean = np.mean(ref_zz_vals) if ref_zz_vals else 25.0
            ref_dye_mean = np.mean(ref_dye_vals) if ref_dye_vals else 25.0

            delta_ct_zz = mean_ct_zz - ref_zz_mean
            delta_ct_dye = mean_ct_dye - ref_dye_mean
            delta_delta_ct = delta_ct_dye - delta_ct_zz
            fc = 2.0 ** (-delta_delta_ct)

            results[gene] = {
                "Ct_ZZ": float(mean_ct_zz),
                "Ct_dye": float(mean_ct_dye),
                "delta_Ct_ZZ": float(delta_ct_zz),
                "delta_Ct_dye": float(delta_ct_dye),
                "delta_delta_Ct": float(delta_delta_ct),
                "FC_experimental": float(fc),
                "direction": "UP" if fc > 1.5 else ("DOWN" if fc < 0.67 else "STABLE"),
                "n_replicates_zz": len(ct_zz),
                "n_replicates_dye": len(ct_dye),
            }

    return results


def validate_expression(expr_result, rtqpcr_fc, route):
    """Compare simulated expression with RT-qPCR and classify route."""
    if expr_result is None or not rtqpcr_fc:
        return {"status": "NO_EXPRESSION_DATA", "classification": "ROUTE_MISSING_STEPS"}

    genes_sim = expr_result["genes"]
    comparisons = []
    direction_matches = 0
    direction_total = 0
    magnitude_errors = []

    for gene, qpcr in rtqpcr_fc.items():
        fc_exp = qpcr["FC_experimental"]
        dir_exp = qpcr["direction"]

        fc_sim = None
        dir_sim = "UNKNOWN"
        if gene in genes_sim:
            fc_sim = genes_sim[gene]["FC_final"]
            dir_sim = "UP" if fc_sim > 1.5 else ("DOWN" if fc_sim < 0.67 else "STABLE")
        elif gene.replace("/", "_") in genes_sim:
            g2 = gene.replace("/", "_")
            fc_sim = genes_sim[g2]["FC_final"]
            dir_sim = "UP" if fc_sim > 1.5 else ("DOWN" if fc_sim < 0.67 else "STABLE")

        direction_match = (dir_exp == dir_sim) if fc_sim is not None else False
        mag_err = 0.0
        if fc_sim is not None:
            direction_total += 1
            if direction_match:
                direction_matches += 1
            mag_err = abs(np.log2(max(fc_sim, 0.01)) - np.log2(max(fc_exp, 0.01)))
            magnitude_errors.append(mag_err)

        comparisons.append({
            "gene": gene,
            "FC_experimental": fc_exp,
            "FC_simulated": fc_sim,
            "direction_exp": dir_exp,
            "direction_sim": dir_sim,
            "direction_match": direction_match,
            "magnitude_error_log2": float(mag_err) if fc_sim is not None else None,
        })

    dir_accuracy = safe_div(direction_matches, direction_total)
    mean_mag_err = float(np.mean(magnitude_errors)) if magnitude_errors else 999.0

    if dir_accuracy >= 0.85 and mean_mag_err < 1.5:
        classification = "CANONICAL_ROUTE_CONFIRMED"
    elif dir_accuracy >= 0.70 and mean_mag_err < 2.5:
        classification = "PLATFORM_ALIGNED"
    elif dir_accuracy >= 0.50:
        classification = "PLATFORM_PARTIAL"
    else:
        classification = "PLATFORM_INCOMPLETE"

    failures = []
    for comp in comparisons:
        if not comp["direction_match"] and comp["FC_simulated"] is not None:
            gene = comp["gene"]
            step_types = {s.get("gene", ""): s.get("type", "unknown") for s in route["steps"]}
            relevant_type = "unknown"
            for sg, st in step_types.items():
                if gene.lower() in sg.lower():
                    relevant_type = st
                    break

            failures.append({
                "gene": gene,
                "expected": comp["direction_exp"],
                "got": comp["direction_sim"],
                "possible_issue": _diagnose_failure(gene, comp, relevant_type),
            })

    return {
        "status": "VALIDATED",
        "classification": classification,
        "direction_accuracy": float(dir_accuracy),
        "mean_magnitude_error_log2": mean_mag_err,
        "n_genes_compared": direction_total,
        "n_direction_matches": direction_matches,
        "comparisons": comparisons,
        "failures": failures,
    }


def _diagnose_failure(gene, comp, step_type):
    fc_exp = comp["FC_experimental"]
    fc_sim = comp["FC_simulated"]

    if fc_sim is None:
        return f"Gene {gene} not in simulation \u2014 possible missing step"

    if comp["direction_exp"] == "UP" and comp["direction_sim"] == "DOWN":
        if step_type in ("transport", "reductase"):
            return f"Gene {gene} expected UP but sim DOWN \u2014 route may need additional transport/reductase step"
        elif step_type in ("dioxygenase", "oxidase"):
            return f"Gene {gene} expected UP but sim DOWN \u2014 ring processing pathway may be incomplete"
        else:
            return f"Gene {gene} expected UP but sim DOWN \u2014 possible missing regulatory connection"

    if comp["direction_exp"] == "DOWN" and comp["direction_sim"] == "UP":
        return f"Gene {gene} expected DOWN but sim UP \u2014 possible competitive pathway not modeled"

    if comp["direction_exp"] == "STABLE" and comp["direction_sim"] != "STABLE":
        return f"Gene {gene} expected STABLE but shows {comp['direction_sim']} \u2014 check if gene is truly on-route"

    return f"Gene {gene}: magnitude differs (exp={fc_exp:.2f} vs sim={fc_sim:.2f})"


def export_expression(expr_result, validation, output_dir):
    """Export expression results."""
    if expr_result is None:
        return

    genes = expr_result["genes"]

    headers, rows = build_hourly_table(expr_result)
    if headers:
        write_tsv(os.path.join(output_dir, "expression_hourly.tsv"), headers, rows)

    gene_names = sorted(genes.keys())
    sum_headers = ["Gene", "alpha", "FC_final_sim", "FC_obs_calib", "FC_model_calib", "Grade"]
    sum_rows = []
    for g in gene_names:
        gd = genes[g]
        sum_rows.append([
            g,
            f"{gd['alpha']:.4f}",
            f"{gd['FC_final']:.2f}",
            str(gd.get("calib_obs_fc", "-")),
            str(gd.get("calib_model_fc", "-")),
            str(gd.get("calib_grade", "-")),
        ])
    write_tsv(os.path.join(output_dir, "expression_summary.tsv"), sum_headers, sum_rows)

    if validation:
        write_json(os.path.join(output_dir, "expression_validation.json"), validation)
