"""Markdown report generation."""

import os
import datetime

from mrhp.io.writers import write_md


def generate_report(cfg, route, sim_result, sim_analysis,
                    bridge_result, bridge_eval,
                    expr_result, validation,
                    omics_evidence, score, output_dir):
    """Generate comprehensive markdown report."""
    dye = route.get("dye_code", "?")
    route_id = route.get("route_id", "unknown")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"# Multiscale Route Hypothesis Report")
    lines.append(f"")
    lines.append(f"**Route:** {route_id}  ")
    lines.append(f"**Organism:** {cfg.get('organism', '?')}  ")
    lines.append(f"**Target:** {cfg.get('target', '?')}  ")
    lines.append(f"**Dye code:** {dye}  ")
    lines.append(f"**Generated:** {ts}  ")
    lines.append(f"")

    # Score overview
    if score:
        cl = score.get("classification", "?")
        ss = score.get("sync_score", 0)
        route_source = route.get("source", "unknown")
        if route_source == "catalog":
            canon_status = "VALIDATED (canonical route from project catalog)"
        else:
            canon_status = "HYPOTHETICAL (user-defined route)"

        lines.append(f"## Canon vs Platform Status")
        lines.append(f"")
        lines.append(f"| Dimension | Status |")
        lines.append(f"|-----------|--------|")
        lines.append(f"| Canonical route status | **{canon_status}** |")
        lines.append(f"| Platform execution status | **{cl}** |")
        lines.append(f"| Synchronization score | {ss:.4f} |")
        lines.append(f"")
        lines.append(f"## Overall Verdict")
        lines.append(f"")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Classification | **{cl}** |")
        lines.append(f"| Synchronization Score | {ss:.4f} |")
        sc = score.get("scores", {})
        for k in ("metabolism", "bridge", "expression", "omics"):
            lines.append(f"| {k.capitalize()} | {sc.get(k, 0):.3f} |")
        lines.append(f"")

    # Route summary
    lines.append(f"## Route Summary")
    lines.append(f"")
    lines.append(f"- Steps: {route.get('n_steps', '?')}")
    lines.append(f"- Metabolites: {len(route.get('all_metabolites', []))}")
    lines.append(f"- Enzymes: {len(route.get('all_enzymes', []))}")
    lines.append(f"- Genes: {len(route.get('all_genes', []))}")
    lines.append(f"- Overall confidence: {route.get('overall_confidence', '?'):.3f}")
    lines.append(f"")
    lines.append(f"### Step detail")
    lines.append(f"")
    lines.append(f"| # | Substrate(s) | Product(s) | Enzyme | Gene | EC | Confidence |")
    lines.append(f"|---|-------------|------------|--------|------|----|------------|")
    for i, s in enumerate(route.get("steps", []), 1):
        subs = ", ".join(s.get("substrates", [s.get("substrate", "-")]))
        prods = ", ".join(s.get("products", [s.get("product", "-")]))
        lines.append(f"| {i} | {subs} | {prods} "
                     f"| {s.get('enzyme','-')} | {s.get('gene','-')} "
                     f"| {s.get('ec', s.get('EC','-'))} | {s.get('confidence','-')} |")
    lines.append(f"")

    # Metabolic dynamics
    if sim_result:
        lines.append(f"## Metabolic Dynamics (ODE)")
        lines.append(f"")
        lines.append(f"- Solver: Radau")
        lines.append(f"- Time points: {len(sim_result.get('t', []))}")
        n_species = len(sim_result.get('metabolites', sim_result.get('species', [])))
        lines.append(f"- Species: {n_species}")
        if sim_analysis:
            t50 = sim_analysis.get('t50_substrate', sim_analysis.get('t50'))
            lines.append(f"- t50 (substrate): {f'{t50:.1f} h' if t50 is not None else 'not reached'}")
            suc = sim_analysis.get('succinylCoA_final', 0)
            ace = sim_analysis.get('acetylCoA_final', 0)
            tca_conv = 'YES' if (suc > 0.01 or ace > 0.01) else 'NO'
            lines.append(f"- TCA convergence: {tca_conv} (succinylCoA={suc:.4f}, acetylCoA={ace:.4f})")
            sub_pct = sim_analysis.get('substrate_consumed_pct')
            if sub_pct is not None:
                lines.append(f"- Substrate consumed: {sub_pct:.1f}%")
            bn = sim_analysis.get('bottleneck_reaction')
            if bn:
                lines.append(f"- Bottleneck: {bn} (avg rate: {sim_analysis.get('bottleneck_avg_rate', 0):.4e})")
            nadh_c = sim_analysis.get('NADH_consumed')
            if nadh_c is not None:
                lines.append(f"- NADH consumed: {nadh_c:.4f}")
        lines.append(f"")

    # Bridge prediction
    if bridge_result and bridge_eval:
        lines.append(f"## Bridge & Phenotype Prediction")
        lines.append(f"")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        for k, v in bridge_eval.items():
            if isinstance(v, float):
                lines.append(f"| {k} | {v:.4f} |")
            else:
                lines.append(f"| {k} | {v} |")
        lines.append(f"")

    # Expression analysis
    if expr_result:
        lines.append(f"## Gene Expression Simulation")
        lines.append(f"")
        lines.append(f"Genes simulated: {expr_result.get('n_genes', 0)}")
        lines.append(f"")
        genes = expr_result.get("genes", {})
        lines.append(f"| Gene | \u03b1 | FC_sim | FC_calib_obs | Grade |")
        lines.append(f"|------|---|--------|-------------|-------|")
        for g in sorted(genes.keys()):
            gd = genes[g]
            obs = gd.get("calib_obs_fc", "-")
            obs_str = f"{obs:.2f}" if isinstance(obs, (int, float)) else str(obs)
            lines.append(f"| {g} | {gd['alpha']:.4f} | {gd['FC_final']:.2f} "
                         f"| {obs_str} | {gd.get('calib_grade', '-')} |")
        lines.append(f"")

    # RT-qPCR validation
    if validation and validation.get("status") == "VALIDATED":
        lines.append(f"## RT-qPCR Validation")
        lines.append(f"")
        cl = validation["classification"]
        lines.append(f"**Classification: {cl}**")
        lines.append(f"")
        lines.append(f"- Direction accuracy: {validation['direction_accuracy']:.1%}")
        lines.append(f"- Mean magnitude error (log2): {validation['mean_magnitude_error_log2']:.2f}")
        lines.append(f"- Genes compared: {validation['n_genes_compared']}")
        lines.append(f"")
        comps = validation.get("comparisons", [])
        if comps:
            lines.append(f"| Gene | FC_exp | FC_sim | Dir_exp | Dir_sim | Match |")
            lines.append(f"|------|--------|--------|---------|---------|-------|")
            for c in comps:
                fc_s = f"{c['FC_simulated']:.2f}" if c["FC_simulated"] is not None else "-"
                match = "\u2713" if c["direction_match"] else "\u2717"
                lines.append(f"| {c['gene']} | {c['FC_experimental']:.2f} | {fc_s} "
                             f"| {c['direction_exp']} | {c['direction_sim']} | {match} |")
            lines.append(f"")

        fails = validation.get("failures", [])
        if fails:
            lines.append(f"### Failure Diagnostics")
            lines.append(f"")
            for f in fails:
                lines.append(f"- **{f['gene']}**: {f['possible_issue']}")
            lines.append(f"")

    # Omics evidence
    if omics_evidence:
        lines.append(f"## Omics Evidence")
        lines.append(f"")
        if "nmr" in omics_evidence:
            nmr = omics_evidence["nmr"]
            lines.append(f"### NMR")
            lines.append(f"- Confirmed metabolites: {len(nmr.get('confirmed', []))}")
            lines.append(f"- Not in route: {len(nmr.get('absent', []))}")
            lines.append(f"- Coverage: {nmr.get('coverage', 0):.1%}")
            lines.append(f"")
        if "redox" in omics_evidence:
            rdx = omics_evidence["redox"]
            lines.append(f"### Redox balance")
            lines.append(f"- Expected NADH/mol: {rdx.get('expected_nadh_per_mol', '?')}")
            lines.append(f"- Route NADH-consuming steps: {rdx.get('route_nadh_steps', '?')}")
            lines.append(f"- Route O2-consuming steps: {rdx.get('route_o2_steps', '?')}")
            lines.append(f"- Balance OK: {rdx.get('balance_ok', '?')}")
            lines.append(f"")

    lines.append(f"---")
    lines.append(f"*Generated by multiscale-route-hypothesis-platform v1.0*")

    write_md(os.path.join(output_dir, f"report_{route_id}.md"), "\n".join(lines))
    return "\n".join(lines)
