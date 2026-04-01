"""Bridge framework: metabolism \u2192 phenotype prediction."""

import os

import numpy as np
from scipy.integrate import cumulative_trapezoid

from mrhp.models.frozen import V4_PARAMS, BRIDGE_V5_PARAMS
from mrhp.io.writers import write_json, write_tsv, safe_div


def compute_v4_phenotype(dye_code, context, t_span=(0, 48), dt=0.5):
    """Compute V4 Hill decolorization curve (top-down)."""
    if dye_code not in V4_PARAMS:
        return None

    p = V4_PARAMS[dye_code]
    K_yc = V4_PARAMS["K_yc"]
    K_dic = V4_PARAMS["K_dic"]

    yc = context.get("yc", 3.0)
    dic = context.get("dic", 0.6)

    Dmax, Vmax, n, lag = p["Dmax"], p["Vmax"], p["n"], p["lag"]
    h_SI = (yc**n / (K_yc**n + yc**n)) * (K_dic / (K_dic + dic))

    t = np.arange(t_span[0], t_span[1] + dt, dt)
    t_eff = np.maximum(t - lag, 0)
    D = Dmax * (1.0 - np.exp(-Vmax * h_SI * t_eff))

    return {"t": t, "D": D, "Dmax": Dmax, "Vmax": Vmax, "n": n, "lag": lag, "h_SI": h_SI}


def compute_bridge(dye_code, context, sim_result=None, t_span=(0, 48), dt=0.5):
    """Compute bridge v5 prediction: metabolism \u2192 phenotype."""
    if dye_code not in BRIDGE_V5_PARAMS:
        return None

    bp = BRIDGE_V5_PARAMS[dye_code]
    lam = bp["lam"]
    Vmax_b = bp["Vmax"]
    Kd = bp["Kd"]
    alpha_p = bp["alpha_p"]
    k_p = bp["k_p"]

    yc = context.get("yc", 3.0)
    dic = context.get("dic", 0.6)

    t = np.arange(t_span[0], t_span[1] + dt, dt)

    v4 = compute_v4_phenotype(dye_code, context, t_span, dt)
    if v4 is None:
        return None
    D_td = v4["D"]
    B = np.clip(D_td / 100.0, 0, 1)

    S = yc
    I = dic
    Phi = Vmax_b * S * t / (Kd + I + alpha_p * S)
    dPhi_dt = np.gradient(Phi, t)

    Psi = 1.0 - np.exp(-k_p * t)

    alpha_B = 1.0
    h = lam * (dPhi_dt * Psi) * np.power(np.maximum(B, 1e-12), alpha_B)

    H = np.zeros_like(t)
    H[1:] = cumulative_trapezoid(h, t)

    beta = 0.5
    y_max = V4_PARAMS[dye_code]["Dmax"]
    y_bridge = y_max * (1.0 - np.exp(-np.power(np.maximum(H, 0), beta)))

    y_bu = None
    if sim_result is not None:
        y_bu = _bridge_from_simulation(sim_result, bp, t, B, beta, y_max)

    return {
        "t": t, "D_v4": D_td, "y_bridge": y_bridge, "y_bu": y_bu,
        "Phi": Phi, "dPhi_dt": dPhi_dt, "Psi": Psi,
        "h": h, "H": H, "B": B, "lam": lam, "beta": beta,
    }


def _bridge_from_simulation(sim_result, bp, t_bridge, B, beta, y_max):
    """Use bottom-up ODE substrate consumption as metabolic drive."""
    t_sim = sim_result["t"]
    y_sim = sim_result["y"]
    mets = sim_result["metabolites"]
    met_idx = sim_result["met_idx"]

    sub_idx = None
    for m in mets:
        if "_ext" in m:
            sub_idx = met_idx[m]
            break
    if sub_idx is None:
        return None

    sub_trace = y_sim[sub_idx, :]
    sub_interp = np.interp(t_bridge, t_sim, sub_trace)

    drive = -np.gradient(sub_interp, t_bridge)
    drive = np.maximum(drive, 0)

    Psi = 1.0 - np.exp(-bp["k_p"] * t_bridge)
    h_bu = bp["lam"] * drive * Psi * np.maximum(B, 1e-12)

    H_bu = np.zeros_like(t_bridge)
    H_bu[1:] = cumulative_trapezoid(h_bu, t_bridge)

    return y_max * (1.0 - np.exp(-np.power(np.maximum(H_bu, 0), beta)))


def evaluate_bridge(bridge_result, context=None):
    """Compute bridge quality metrics."""
    if bridge_result is None:
        return {"status": "NO_BRIDGE_AVAILABLE"}

    t = bridge_result["t"]
    D_v4 = bridge_result["D_v4"]
    y_bridge = bridge_result["y_bridge"]

    ss_res = np.sum((D_v4 - y_bridge) ** 2)
    ss_tot = np.sum((D_v4 - np.mean(D_v4)) ** 2)
    R2 = 1.0 - safe_div(ss_res, ss_tot, 1.0)

    rmse = np.sqrt(np.mean((D_v4 - y_bridge) ** 2))

    t50_v4 = _find_t50(t, D_v4)
    t50_bridge = _find_t50(t, y_bridge)

    Dmax_v4 = float(np.max(D_v4))
    Dmax_bridge = float(np.max(y_bridge))

    metrics = {
        "R2_bridge_vs_v4": float(R2),
        "RMSE": float(rmse),
        "t50_v4": t50_v4,
        "t50_bridge": t50_bridge,
        "Dmax_v4": Dmax_v4,
        "Dmax_bridge": Dmax_bridge,
    }

    y_bu = bridge_result.get("y_bu")
    if y_bu is not None:
        ss_res_bu = np.sum((D_v4 - y_bu) ** 2)
        R2_bu = 1.0 - safe_div(ss_res_bu, ss_tot, 1.0)
        rmse_bu = np.sqrt(np.mean((D_v4 - y_bu) ** 2))
        metrics["R2_bu_vs_v4"] = float(R2_bu)
        metrics["RMSE_bu"] = float(rmse_bu)
        metrics["Dmax_bu"] = float(np.max(y_bu))

    return metrics


def _find_t50(t, y):
    half = np.max(y) * 0.5
    crossings = np.where(y >= half)[0]
    if len(crossings) > 0:
        return float(t[crossings[0]])
    return None


def export_bridge(bridge_result, metrics, output_dir):
    """Export bridge results."""
    if bridge_result is None:
        return

    t = bridge_result["t"]
    headers = ["time_h", "D_v4", "y_bridge", "Phi", "dPhi_dt", "Psi", "h", "H", "B"]
    rows = []
    for ti in range(len(t)):
        rows.append([
            f"{t[ti]:.2f}",
            f"{bridge_result['D_v4'][ti]:.4f}",
            f"{bridge_result['y_bridge'][ti]:.4f}",
            f"{bridge_result['Phi'][ti]:.6f}",
            f"{bridge_result['dPhi_dt'][ti]:.6f}",
            f"{bridge_result['Psi'][ti]:.6f}",
            f"{bridge_result['h'][ti]:.8f}",
            f"{bridge_result['H'][ti]:.8f}",
            f"{bridge_result['B'][ti]:.6f}",
        ])

    write_tsv(os.path.join(output_dir, "bridge_timecourse.tsv"), headers, rows)
    write_json(os.path.join(output_dir, "bridge_metrics.json"), metrics)
