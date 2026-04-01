"""Stoichiometric matrix construction and ODE simulation."""

import os

import numpy as np
from scipy.integrate import solve_ivp

from mrhp.models.frozen import NADH_PER_DYE
from mrhp.io.writers import write_json, write_tsv


def build_stoichiometry(route, cfg):
    """Build stoichiometric matrix from route steps."""
    steps = route["steps"]
    mets = route["all_metabolites"]
    n_met = len(mets)
    n_rxn = len(steps)
    met_idx = {m: i for i, m in enumerate(mets)}

    S = np.zeros((n_met, n_rxn))
    for j, step in enumerate(steps):
        for sub in step.get("substrates", []):
            if sub in met_idx:
                S[met_idx[sub], j] -= 1.0
        for prod in step.get("products", []):
            if prod in met_idx:
                S[met_idx[prod], j] += 1.0

    # Initial concentrations
    x0 = np.zeros(n_met)
    dye_code = route.get("dye_code", "")

    for m in mets:
        if "_ext" in m or m == route.get("substrate_name", ""):
            x0[met_idx[m]] = 1.0
            break

    if "NADH" in met_idx:
        nadh_need = NADH_PER_DYE.get(dye_code, 1) * 10
        x0[met_idx["NADH"]] = float(nadh_need)
    if "O2" in met_idx:
        x0[met_idx["O2"]] = 5.0
    if "CoA" in met_idx:
        x0[met_idx["CoA"]] = 2.0
    if "succinylCoA" in met_idx:
        x0[met_idx["succinylCoA"]] = 1.0

    # Rate constants
    context = cfg.get("context", {})
    k_default = context.get("k_default", 0.5)
    k = np.full(n_rxn, k_default)
    for j, step in enumerate(steps):
        if step.get("confidence") == "exact":
            k[j] = k_default * 2.0
        elif step.get("confidence") == "plausible":
            k[j] = k_default * 0.8

    return {
        "S": S, "metabolites": mets, "met_idx": met_idx,
        "reactions": [s["id"] for s in steps],
        "x0": x0, "k": k, "n_met": n_met, "n_rxn": n_rxn,
    }


def simulate_ode(stoich, cfg, t_span=(0, 48), dt=0.5):
    """Simulate metabolic dynamics using ODE with mass-action kinetics."""
    S = stoich["S"]
    x0 = stoich["x0"]
    k = stoich["k"]
    n_met = stoich["n_met"]
    n_rxn = stoich["n_rxn"]

    t_eval = np.arange(t_span[0], t_span[1] + dt, dt)

    def rhs(t, x):
        x_pos = np.maximum(x, 0)
        v = np.zeros(n_rxn)
        for j in range(n_rxn):
            rate = k[j]
            for i in range(n_met):
                if S[i, j] < 0:
                    rate *= x_pos[i] ** abs(S[i, j])
            v[j] = rate
        return S @ v

    sol = solve_ivp(rhs, t_span, x0, method="Radau", t_eval=t_eval,
                    rtol=1e-8, atol=1e-10, max_step=1.0)

    if not sol.success:
        print(f"  [WARNING] ODE solver: {sol.message}")

    sim_result = {
        "t": sol.t,
        "y": sol.y,
        "metabolites": stoich["metabolites"],
        "met_idx": stoich["met_idx"],
        "success": sol.success,
        "message": sol.message,
    }

    rates = np.zeros((n_rxn, len(sol.t)))
    for ti in range(len(sol.t)):
        x_pos = np.maximum(sol.y[:, ti], 0)
        for j in range(n_rxn):
            rate = k[j]
            for i in range(n_met):
                if S[i, j] < 0:
                    rate *= x_pos[i] ** abs(S[i, j])
            rates[j, ti] = rate
    sim_result["rates"] = rates
    sim_result["reactions"] = stoich["reactions"]

    return sim_result


def analyze_dynamics(sim_result, route):
    """Analyze the simulation: bottlenecks, balance, convergence."""
    t = sim_result["t"]
    y = sim_result["y"]
    rates = sim_result["rates"]
    mets = sim_result["metabolites"]
    rxns = sim_result["reactions"]
    met_idx = sim_result["met_idx"]

    analysis = {}

    for m in mets:
        if "_ext" in m:
            idx = met_idx[m]
            analysis["substrate_initial"] = float(y[idx, 0])
            analysis["substrate_final"] = float(y[idx, -1])
            analysis["substrate_consumed_pct"] = float(
                100.0 * (1.0 - max(y[idx, -1], 0) / max(y[idx, 0], 1e-30))
            )
            break

    avg_rates = np.mean(rates, axis=1)
    bottleneck_idx = int(np.argmin(avg_rates))
    analysis["bottleneck_reaction"] = rxns[bottleneck_idx]
    analysis["bottleneck_avg_rate"] = float(avg_rates[bottleneck_idx])
    analysis["rate_ranking"] = sorted(
        [(rxns[j], float(avg_rates[j])) for j in range(len(rxns))],
        key=lambda x: x[1]
    )

    if "NADH" in met_idx and "NAD" in met_idx:
        analysis["NADH_initial"] = float(y[met_idx["NADH"], 0])
        analysis["NADH_final"] = float(y[met_idx["NADH"], -1])
        analysis["NAD_final"] = float(y[met_idx["NAD"], -1])
        analysis["NADH_consumed"] = float(y[met_idx["NADH"], 0] - max(y[met_idx["NADH"], -1], 0))

    for tca_met in ["succinylCoA", "acetylCoA"]:
        if tca_met in met_idx:
            analysis[f"{tca_met}_final"] = float(y[met_idx[tca_met], -1])

    for m in mets:
        if "_ext" in m:
            idx = met_idx[m]
            half = y[idx, 0] * 0.5
            crossings = np.where(y[idx, :] <= half)[0]
            if len(crossings) > 0:
                analysis["t50_substrate"] = float(t[crossings[0]])
            else:
                analysis["t50_substrate"] = None
            break

    return analysis


def export_simulation(sim_result, analysis, output_dir):
    """Export simulation results to TSV and JSON."""
    t = sim_result["t"]
    y = sim_result["y"]
    mets = sim_result["metabolites"]

    headers = ["time_h"] + mets
    rows = []
    for ti in range(len(t)):
        row = [f"{t[ti]:.2f}"] + [f"{y[i, ti]:.8e}" for i in range(len(mets))]
        rows.append(row)
    write_tsv(os.path.join(output_dir, "simulation_timecourse.tsv"), headers, rows)

    rates = sim_result["rates"]
    rxns = sim_result["reactions"]
    headers_r = ["time_h"] + rxns
    rows_r = []
    for ti in range(len(t)):
        row = [f"{t[ti]:.2f}"] + [f"{rates[j, ti]:.8e}" for j in range(len(rxns))]
        rows_r.append(row)
    write_tsv(os.path.join(output_dir, "simulation_rates.tsv"), headers_r, rows_r)

    write_json(os.path.join(output_dir, "dynamics_analysis.json"), analysis)
