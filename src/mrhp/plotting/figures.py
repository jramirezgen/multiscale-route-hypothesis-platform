"""Publication-grade matplotlib figures."""

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from mrhp.models.frozen import V4_PARAMS

DPI = 300
COLORS = {
    "MO": "#FF8C00",
    "RC": "#DC143C",
    "DB": "#00008B",
    "default": "#4682B4",
}


def _dye_color(dye_code):
    return COLORS.get(dye_code, COLORS["default"])


def generate_figures(cfg, route, sim_result, sim_analysis,
                     bridge_result, bridge_eval,
                     expr_result, validation,
                     score, fig_dir):
    """Generate publication-grade figures."""
    dye = route.get("dye_code", "?")
    color = _dye_color(dye)
    route_id = route.get("route_id", "unknown")
    figs_made = []

    # Fig 1: Metabolic dynamics
    if sim_result and "t" in sim_result and "y" in sim_result:
        fig, ax = plt.subplots(figsize=(8, 5))
        t = np.array(sim_result["t"])
        y = np.array(sim_result["y"])
        species = sim_result.get("species", sim_result.get("metabolites", []))
        for si, sp in enumerate(species):
            if si < y.shape[0]:
                ax.plot(t, y[si], label=sp, linewidth=1.2)
        ax.set_xlabel("Time (h)", fontsize=11)
        ax.set_ylabel("Concentration (mM)", fontsize=11)
        ax.set_title(f"Metabolic dynamics \u2014 {route_id}", fontsize=12)
        ax.legend(fontsize=8, ncol=2, loc="upper right")
        ax.grid(True, alpha=0.3)
        path = os.path.join(fig_dir, f"dynamics_{route_id}.png")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        figs_made.append(path)

    # Fig 2: Bridge / phenotype
    if bridge_result and "t" in bridge_result:
        fig, ax = plt.subplots(figsize=(8, 5))
        t = np.array(bridge_result["t"])
        if "y_bridge" in bridge_result:
            ax.plot(t, bridge_result["y_bridge"], color=color, linewidth=2, label="Bridge v5")
        if "D_v4" in bridge_result:
            ax.plot(t, bridge_result["D_v4"], "--", color="gray", linewidth=1.5, label="V4 Hill (top-down)")
        if "y_bu" in bridge_result and bridge_result["y_bu"] is not None:
            ax.plot(t, bridge_result["y_bu"], ":", color="green", linewidth=1.5, label="Bottom-up ODE")
        ax.set_xlabel("Time (h)", fontsize=11)
        ax.set_ylabel("Decolorization (%)", fontsize=11)
        ax.set_title(f"Bridge prediction \u2014 {dye}", fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        path = os.path.join(fig_dir, f"bridge_{route_id}.png")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        figs_made.append(path)

    # Fig 3: Gene expression FC
    if expr_result and expr_result.get("genes"):
        genes = expr_result["genes"]
        gene_names = sorted(genes.keys())

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        ax = axes[0]
        t = np.array(expr_result["t_eval"])
        for g in gene_names:
            fc = np.array(genes[g]["FC"])
            ax.plot(t, fc, label=g, linewidth=1.1)
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.set_xlabel("Time (h)", fontsize=11)
        ax.set_ylabel("Fold change", fontsize=11)
        ax.set_title(f"Expression dynamics \u2014 {dye}", fontsize=12)
        ax.legend(fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        fc_sims = [genes[g]["FC_final"] for g in gene_names]
        fc_obs = []
        for g in gene_names:
            obs = genes[g].get("calib_obs_fc")
            fc_obs.append(obs if isinstance(obs, (int, float)) else None)

        x_pos = np.arange(len(gene_names))
        width = 0.35
        ax.bar(x_pos - width / 2, fc_sims, width, label="Simulated", color=color, alpha=0.7)
        obs_vals = [v if v is not None else 0 for v in fc_obs]
        ax.bar(x_pos + width / 2, obs_vals, width, label="Observed (calib)", color="gray", alpha=0.7)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(gene_names, rotation=45, ha="right", fontsize=8)
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.set_ylabel("Fold change", fontsize=11)
        ax.set_title(f"Expression: sim vs observed \u2014 {dye}", fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")

        path = os.path.join(fig_dir, f"expression_{route_id}.png")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        figs_made.append(path)

    # Fig 4: RT-qPCR validation
    if validation and validation.get("comparisons"):
        comps = validation["comparisons"]
        genes_comp = [c["gene"] for c in comps]
        fc_exp = [c["FC_experimental"] for c in comps]
        fc_sim_vals = [c["FC_simulated"] if c["FC_simulated"] is not None else 0 for c in comps]

        fig, ax = plt.subplots(figsize=(8, 5))
        x_pos = np.arange(len(genes_comp))
        width = 0.35
        ax.bar(x_pos - width / 2, fc_exp, width, label="RT-qPCR (\u0394\u0394Ct)", color="#2196F3", alpha=0.8)
        ax.bar(x_pos + width / 2, fc_sim_vals, width, label="Simulated", color=color, alpha=0.8)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(genes_comp, rotation=45, ha="right", fontsize=9)
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.set_ylabel("Fold change", fontsize=11)
        ax.set_title(f"RT-qPCR validation \u2014 {dye} ({validation['classification']})", fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis="y")

        path = os.path.join(fig_dir, f"rtqpcr_validation_{route_id}.png")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        figs_made.append(path)

    # Fig 5: Multi-layer synchronization panel
    if score and sim_result and bridge_result and expr_result:
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)

        # Panel A: Metabolic dynamics
        ax = fig.add_subplot(gs[0, 0])
        t = np.array(sim_result["t"])
        y = np.array(sim_result["y"])
        species = sim_result.get("species", sim_result.get("metabolites", []))
        for si, sp in enumerate(species[:6]):
            if si < y.shape[0]:
                ax.plot(t, y[si], label=sp, linewidth=1.0)
        ax.set_title("A. Metabolic dynamics", fontsize=11, fontweight="bold")
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Conc (mM)")
        ax.legend(fontsize=6, ncol=2)
        ax.grid(True, alpha=0.2)

        # Panel B: Bridge prediction
        ax = fig.add_subplot(gs[0, 1])
        bt = np.array(bridge_result["t"])
        if "y_bridge" in bridge_result:
            ax.plot(bt, bridge_result["y_bridge"], color=color, linewidth=2, label="Bridge")
        if "D_v4" in bridge_result:
            ax.plot(bt, bridge_result["D_v4"], "--", color="gray", label="V4")
        ax.set_title("B. Bridge phenotype", fontsize=11, fontweight="bold")
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Decolorization (%)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.2)

        # Panel C: Expression dynamics
        ax = fig.add_subplot(gs[1, 0])
        t_ex = np.array(expr_result["t_eval"])
        genes_data = expr_result["genes"]
        for g in sorted(genes_data.keys()):
            ax.plot(t_ex, genes_data[g]["FC"], label=g, linewidth=0.9)
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.set_title("C. Gene expression dynamics", fontsize=11, fontweight="bold")
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Fold change")
        ax.legend(fontsize=6, ncol=2)
        ax.grid(True, alpha=0.2)

        # Panel D: RT-qPCR comparison
        ax = fig.add_subplot(gs[1, 1])
        if validation and validation.get("comparisons"):
            comps = validation["comparisons"]
            g_names = [c["gene"] for c in comps]
            fc_e = [c["FC_experimental"] for c in comps]
            fc_s = [c["FC_simulated"] if c["FC_simulated"] else 0 for c in comps]
            x = np.arange(len(g_names))
            ax.bar(x - 0.17, fc_e, 0.34, label="RT-qPCR", color="#2196F3", alpha=0.8)
            ax.bar(x + 0.17, fc_s, 0.34, label="Simulated", color=color, alpha=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(g_names, rotation=45, ha="right", fontsize=7)
            ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5)
            ax.legend(fontsize=8)
        ax.set_title("D. RT-qPCR validation", fontsize=11, fontweight="bold")
        ax.set_ylabel("Fold change")
        ax.grid(True, alpha=0.2, axis="y")

        # Panel E: Score breakdown
        ax = fig.add_subplot(gs[2, 0])
        sc = score.get("scores", {})
        cats = ["Metabolism", "Bridge", "Expression", "Omics"]
        vals = [sc.get("metabolism", 0), sc.get("bridge", 0),
                sc.get("expression", 0), sc.get("omics", 0)]
        bars = ax.barh(cats, vals, color=[color] * 4, alpha=0.7)
        ax.set_xlim(0, 1.05)
        ax.axvline(0.7, color="green", linestyle="--", alpha=0.4, label="Threshold")
        for bar, v in zip(bars, vals):
            ax.text(v + 0.02, bar.get_y() + bar.get_height() / 2,
                    f"{v:.3f}", va="center", fontsize=9)
        ax.set_title("E. Layer scores", fontsize=11, fontweight="bold")
        ax.set_xlabel("Score")

        # Panel F: Overall verdict
        ax = fig.add_subplot(gs[2, 1])
        ax.axis("off")
        ss = score.get("sync_score", 0)
        cl = score.get("classification", "?")
        verdict_color = {
            "CANONICAL_ROUTE_CONFIRMED": "green", "PLATFORM_ALIGNED": "#2196F3",
            "PLATFORM_PARTIAL": "#DAA520", "PLATFORM_INCOMPLETE": "orange",
            "ROUTE_COMPATIBLE": "green", "ROUTE_PARTIAL": "#DAA520",
            "ROUTE_MISSING_STEPS": "orange", "ROUTE_INCOMPATIBLE": "red",
        }.get(cl, "gray")
        ax.text(0.5, 0.6, cl, fontsize=22, fontweight="bold",
                ha="center", va="center", color=verdict_color, transform=ax.transAxes)
        ax.text(0.5, 0.35, f"Sync Score: {ss:.4f}", fontsize=16,
                ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.15, f"Route: {route_id}", fontsize=11,
                ha="center", va="center", color="gray", transform=ax.transAxes)
        ax.set_title("F. Verdict", fontsize=11, fontweight="bold")

        fig.suptitle(f"Multiscale Route Hypothesis \u2014 {cfg.get('organism', '?')} / {dye}",
                     fontsize=14, fontweight="bold", y=0.98)

        path = os.path.join(fig_dir, f"multilayer_panel_{route_id}.png")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        figs_made.append(path)

    return figs_made
