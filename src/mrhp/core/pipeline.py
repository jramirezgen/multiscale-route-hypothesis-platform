"""Core 10-phase pipeline orchestrator."""

import os
import datetime
import traceback

from mrhp.config.loader import load_config, get_dye_code
from mrhp.io.writers import (write_json, snapshot_inputs, ensure_dir,
                              get_output_dir, get_report_dir,
                              get_figure_dir, get_log_dir)
from mrhp.simulation.route_builder import build_route, route_story
from mrhp.simulation.ode_solver import (build_stoichiometry, simulate_ode,
                                         analyze_dynamics, export_simulation)
from mrhp.bridge.engine import (compute_bridge, evaluate_bridge, export_bridge)
from mrhp.expression.simulator import (simulate_expression, compute_rtqpcr_fc,
                                        validate_expression, export_expression)
from mrhp.integration.omics import integrate_omics
from mrhp.scoring.scorer import score_hypothesis, rank_hypotheses, export_ranking
from mrhp.reporting.markdown import generate_report
from mrhp.plotting.figures import generate_figures


def run_single(cfg, yaml_path, base_dir):
    """Run the full 10-phase pipeline for a single config.

    Returns a dict with keys: route_id, dye_code, score, bridge_eval,
    validation, sim_analysis, route, and optionally 'error'.
    """
    route_id = cfg.get("route_hypothesis", {}).get("route_id", "unknown")
    dye_code = get_dye_code(cfg)

    print(f"\n{'=' * 60}")
    print(f"  MULTISCALE ROUTE HYPOTHESIS PLATFORM")
    print(f"  Route: {route_id}")
    print(f"  Organism: {cfg.get('organism', '?')}")
    print(f"  Target: {cfg.get('target', '?')}")
    print(f"{'=' * 60}\n")

    output_dir = get_output_dir(base_dir)
    report_dir = get_report_dir(base_dir)
    fig_dir = get_figure_dir(base_dir)
    log_dir = get_log_dir(base_dir)
    for d in [output_dir, report_dir, fig_dir, log_dir]:
        ensure_dir(d)

    results = {"route_id": route_id, "dye_code": dye_code}
    log_lines = []

    def log(msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        log_lines.append(line)

    try:
        # Phase 0
        log("Phase 0: Snapshot inputs...")
        snap = snapshot_inputs(cfg, yaml_path)
        write_json(os.path.join(output_dir, "snapshot.json"), snap)

        # Phase 1
        log("Phase 1: Config loaded OK")

        # Phase 2
        log("Phase 2: Building route from hypothesis...")
        route = build_route(cfg)
        route["dye_code"] = dye_code
        log(f"  Route: {route['n_steps']} steps, {len(route['all_genes'])} genes, "
            f"confidence={route['overall_confidence']:.3f}")
        results["route"] = route

        # Phase 3
        log("Phase 3: Stoichiometry + ODE simulation...")
        stoich = build_stoichiometry(route, cfg)
        sim_result = simulate_ode(stoich, cfg)
        sim_analysis = analyze_dynamics(sim_result, route)
        export_simulation(sim_result, sim_analysis, output_dir)
        log(f"  S: {stoich['S'].shape[0]}x{stoich['S'].shape[1]}, "
            f"{len(sim_result['t'])} time points")
        results["sim_result"] = sim_result
        results["sim_analysis"] = sim_analysis

        # Phase 4
        log("Phase 4: Bridge + phenotype prediction...")
        context = cfg.get("context", {})
        bridge_result = compute_bridge(dye_code, context, sim_result)
        bridge_eval = evaluate_bridge(bridge_result)
        export_bridge(bridge_result, bridge_eval, output_dir)
        log(f"  Bridge R2: {bridge_eval.get('R2_bridge_vs_v4', 'N/A'):.4f}")
        results["bridge_result"] = bridge_result
        results["bridge_eval"] = bridge_eval

        # Phase 5
        log("Phase 5: Expression simulation...")
        expr_result = simulate_expression(cfg, route, bridge_result)
        if expr_result:
            log(f"  {expr_result['n_genes']} genes simulated")
        else:
            log("  Skipped (no calibrations or disabled)")
        results["expr_result"] = expr_result

        # Phase 6
        log("Phase 6: RT-qPCR validation...")
        rtqpcr_fc = compute_rtqpcr_fc(dye_code)
        validation = validate_expression(expr_result, rtqpcr_fc, route)
        if expr_result:
            export_expression(expr_result, validation, output_dir)
        log(f"  Classification: {validation.get('classification', 'N/A')}")
        results["validation"] = validation

        # Phase 7
        log("Phase 7: Omics integration...")
        omics_evidence = integrate_omics(cfg, route, sim_result,
                                         bridge_result, expr_result, validation)
        write_json(os.path.join(output_dir, "omics_evidence.json"), omics_evidence)
        results["omics_evidence"] = omics_evidence

        # Phase 8
        log("Phase 8: Hypothesis scoring...")
        score = score_hypothesis(route, sim_analysis, bridge_eval,
                                 validation, omics_evidence)
        write_json(os.path.join(output_dir, "score.json"), score)
        log(f"  Sync score: {score['sync_score']:.4f} -- {score['classification']}")
        results["score"] = score

        # Phase 9
        log("Phase 9: Report...")
        generate_report(cfg, route, sim_result, sim_analysis,
                        bridge_result, bridge_eval, expr_result, validation,
                        omics_evidence, score, report_dir)

        # Phase 10
        log("Phase 10: Figures...")
        figs = generate_figures(cfg, route, sim_result, sim_analysis,
                                bridge_result, bridge_eval, expr_result,
                                validation, score, fig_dir)
        log(f"  {len(figs)} figures generated")

    except Exception as e:
        log(f"ERROR: {e}")
        log(traceback.format_exc())
        results["error"] = str(e)

    log_path = os.path.join(log_dir, f"execution_{route_id}.log")
    with open(log_path, "w") as fh:
        fh.write("\n".join(log_lines))

    return results


def run_pipeline(config_path, base_dir=None):
    """Top-level API entry point.

    Parameters
    ----------
    config_path : str
        Path to a YAML configuration file.
    base_dir : str, optional
        Base directory for outputs. Defaults to directory containing config.

    Returns
    -------
    dict
        Pipeline results including score, route, bridge_eval, etc.
    """
    config_path = os.path.abspath(config_path)
    if base_dir is None:
        base_dir = os.path.dirname(config_path)
    cfg = load_config(config_path)
    return run_single(cfg, config_path, base_dir)
