"""mrhp — Multiscale Route Hypothesis Platform CLI.

Commands:
  run       Run a single hypothesis evaluation
  compare   Compare two route hypotheses head-to-head
  demo      Cross-system validation demo (requires external demo skill)
  explain   Interpret and narrate results from a config
  doctor    Diagnose issues with a config or system setup
  validate  Quick import and structural validation
"""

import argparse
import os
import sys


def _find_package_dir():
    """Return the package root (where configs/ lives)."""
    return os.path.dirname(os.path.abspath(__file__))


def _find_configs_dir():
    """Return the configs/ directory adjacent to the package."""
    pkg = _find_package_dir()
    # installed layout: src/mrhp/ → need to go up to repo root
    for candidate in [
        os.path.join(pkg, "..", "..", "..", "configs"),  # src/mrhp/ → repo/configs
        os.path.join(pkg, "..", "..", "configs"),
        os.path.join(pkg, "configs"),
    ]:
        p = os.path.normpath(candidate)
        if os.path.isdir(p):
            return p
    return None


def resolve_config(path):
    """Resolve config path: try as-is, then configs/, then inputs/."""
    if os.path.isfile(path):
        return os.path.abspath(path)
    configs_dir = _find_configs_dir()
    search_dirs = []
    if configs_dir:
        search_dirs.append(configs_dir)
    for base in search_dirs:
        candidate = os.path.join(base, path)
        if os.path.isfile(candidate):
            return candidate
        if not path.endswith(".yaml"):
            candidate = os.path.join(base, path + ".yaml")
            if os.path.isfile(candidate):
                return candidate
    return None


# ═══════════════════════════════════════════════════════════════
# COMMAND: run
# ═══════════════════════════════════════════════════════════════
def cmd_run(args):
    """Run the full 10-phase pipeline for one or more configs."""
    from mrhp.config.loader import load_config
    from mrhp.core.pipeline import run_single
    from mrhp.io.writers import get_output_dir
    from mrhp.scoring.scorer import rank_hypotheses, export_ranking

    configs = args.config
    base_dir = args.output or os.getcwd()
    all_scores = []

    for cfg_path in configs:
        resolved = resolve_config(cfg_path)
        if resolved is None:
            print(f"ERROR: Config not found: {cfg_path}")
            continue
        cfg = load_config(resolved)
        result = run_single(cfg, resolved, base_dir)
        if "score" in result:
            all_scores.append(result["score"])

    if len(all_scores) > 1:
        ranked = rank_hypotheses(all_scores)
        export_ranking(ranked, get_output_dir(base_dir))
        print(f"\n{'=' * 60}")
        print(f"  MULTI-HYPOTHESIS RANKING ({len(ranked)} hypotheses)")
        print(f"{'=' * 60}")
        for r in ranked:
            print(f"  #{r.get('rank', '?')}: {r.get('route_id', '?')} -- "
                  f"Score={r.get('sync_score', 0):.4f} -- {r.get('classification', '?')}")

    print("\nDone.")


# ═══════════════════════════════════════════════════════════════
# COMMAND: compare
# ═══════════════════════════════════════════════════════════════
def cmd_compare(args):
    """Compare two route hypotheses head-to-head."""
    import datetime
    from mrhp.config.loader import load_config
    from mrhp.core.pipeline import run_single
    from mrhp.io.writers import get_output_dir, get_report_dir, write_json, write_md

    cfg_a_path = resolve_config(args.config)
    cfg_b_path = resolve_config(args.alt)
    if not cfg_a_path:
        sys.exit(f"ERROR: Config not found: {args.config}")
    if not cfg_b_path:
        sys.exit(f"ERROR: Alt config not found: {args.alt}")

    base_dir = args.output or os.getcwd()

    print(f"{'=' * 60}")
    print(f"  MRHP COMPARE -- Head-to-Head")
    print(f"{'=' * 60}")
    print(f"  Config A: {os.path.basename(cfg_a_path)}")
    print(f"  Config B: {os.path.basename(cfg_b_path)}")
    print()

    cfg_a = load_config(cfg_a_path)
    cfg_b = load_config(cfg_b_path)
    res_a = run_single(cfg_a, cfg_a_path, base_dir)
    res_b = run_single(cfg_b, cfg_b_path, base_dir)

    score_a = res_a.get("score", {})
    score_b = res_b.get("score", {})
    route_a = res_a.get("route_id", "A")
    route_b = res_b.get("route_id", "B")

    sync_a = score_a.get("sync_score", 0)
    sync_b = score_b.get("sync_score", 0)
    cls_a = score_a.get("classification", "?")
    cls_b = score_b.get("classification", "?")
    bridge_a = res_a.get("bridge_eval", {}).get("R2_bridge_vs_v4", 0)
    bridge_b = res_b.get("bridge_eval", {}).get("R2_bridge_vs_v4", 0)
    dir_a = res_a.get("validation", {}).get("direction_accuracy", 0)
    dir_b = res_b.get("validation", {}).get("direction_accuracy", 0)

    winner = route_a if sync_a >= sync_b else route_b

    print(f"\n{'=' * 60}")
    print(f"  COMPARISON RESULTS")
    print(f"{'=' * 60}")
    print(f"  {'Metric':<30s} {'A':>12s} {'B':>12s}")
    print(f"  {'-' * 54}")
    print(f"  {'Route':<30s} {route_a:>12s} {route_b:>12s}")
    print(f"  {'Sync Score':<30s} {sync_a:>12.4f} {sync_b:>12.4f}")
    print(f"  {'Classification':<30s} {cls_a:>12s} {cls_b:>12s}")
    print(f"  {'Bridge R2':<30s} {bridge_a:>12.4f} {bridge_b:>12.4f}")
    print(f"  {'Direction Accuracy':<30s} {dir_a:>12.1%} {dir_b:>12.1%}")
    print(f"  {'-' * 54}")
    print(f"  {'WINNER':<30s} {winner:>12s}")
    print(f"{'=' * 60}")

    scores_a = score_a.get("scores", {})
    scores_b = score_b.get("scores", {})
    if scores_a and scores_b:
        print(f"\n  Layer-by-layer:")
        for layer in ["metabolism", "bridge", "expression", "omics"]:
            sa = scores_a.get(layer, 0)
            sb = scores_b.get(layer, 0)
            marker = "<" if sa > sb else (">" if sb > sa else "=")
            print(f"    {layer:<20s}  {sa:.4f}  {marker}  {sb:.4f}")

    output_dir = get_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)
    comparison = {
        "timestamp": datetime.datetime.now().isoformat(),
        "config_a": os.path.basename(cfg_a_path),
        "config_b": os.path.basename(cfg_b_path),
        "route_a": route_a, "route_b": route_b,
        "sync_a": sync_a, "sync_b": sync_b,
        "classification_a": cls_a, "classification_b": cls_b,
        "bridge_r2_a": bridge_a, "bridge_r2_b": bridge_b,
        "direction_accuracy_a": dir_a, "direction_accuracy_b": dir_b,
        "scores_a": scores_a, "scores_b": scores_b,
        "winner": winner,
    }
    write_json(os.path.join(output_dir, "comparison.json"), comparison)

    report_dir = get_report_dir(base_dir)
    os.makedirs(report_dir, exist_ok=True)
    md = [
        f"# MRHP Compare: {route_a} vs {route_b}",
        "",
        f"| Metric | {route_a} | {route_b} |",
        f"|--------|-------|-------|",
        f"| Sync Score | {sync_a:.4f} | {sync_b:.4f} |",
        f"| Classification | {cls_a} | {cls_b} |",
        f"| Bridge R2 | {bridge_a:.4f} | {bridge_b:.4f} |",
        f"| Direction Accuracy | {dir_a:.1%} | {dir_b:.1%} |",
        "",
        f"**Winner: {winner}**",
    ]
    if scores_a and scores_b:
        md += ["", "## Layer-by-Layer", "",
               "| Layer | A | B |", "|-------|---|---|",]
        for layer in ["metabolism", "bridge", "expression", "omics"]:
            md.append(f"| {layer} | {scores_a.get(layer, 0):.4f} | "
                      f"{scores_b.get(layer, 0):.4f} |")
    write_md(os.path.join(report_dir, f"compare_{route_a}_vs_{route_b}.md"),
             "\n".join(md))
    print(f"\n  Report saved.")


# ═══════════════════════════════════════════════════════════════
# COMMAND: explain
# ═══════════════════════════════════════════════════════════════
def cmd_explain(args):
    """Interpret and narrate results from a config."""
    import io
    import contextlib
    from mrhp.config.loader import load_config
    from mrhp.core.pipeline import run_single
    from mrhp.simulation.route_builder import build_route

    cfg_path = resolve_config(args.config)
    if not cfg_path:
        sys.exit(f"ERROR: Config not found: {args.config}")

    base_dir = args.output or os.getcwd()
    cfg = load_config(cfg_path)
    hyp = cfg.get("route_hypothesis", {})
    route_id = hyp.get("route_id", "?")
    dye_code = hyp.get("dye_code", "?")

    print(f"\n{'=' * 60}")
    print(f"  MRHP EXPLAIN -- {route_id}")
    print(f"{'=' * 60}\n")

    print(f"  Organism: {cfg.get('organism', '?')}")
    print(f"  Target:   {cfg.get('target', '?')}")
    print(f"  Route:    {route_id}")
    print(f"  Dye/code: {dye_code}")
    ctx = cfg.get("context", {})
    if ctx:
        print(f"  Context:  {', '.join(f'{k}={v}' for k, v in ctx.items())}")
    print()

    route = build_route(cfg)
    print(f"  Route ({route['n_steps']} steps, {len(route['all_genes'])} genes):")
    print(f"  Confidence: {route['overall_confidence']:.3f}")
    print(f"  Convergence: {route.get('convergence', '?')}")
    print()

    steps = route.get("steps", [])
    for i, s in enumerate(steps):
        enzyme = s.get("enzyme", s.get("gene", "?"))
        conf = s.get("confidence", "?")
        subs = s.get("substrates", s.get("substrate", "?"))
        prod = s.get("products", s.get("product", "?"))
        if isinstance(subs, list):
            subs = " + ".join(subs)
        if isinstance(prod, list):
            prod = " + ".join(prod)
        print(f"    [{i + 1}] {subs} -> {prod}")
        print(f"        Enzyme: {enzyme}  |  Confidence: {conf}")
    print()

    print("  Running full evaluation...")
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_single(cfg, cfg_path, base_dir)

    score = result.get("score", {})
    bridge_eval = result.get("bridge_eval", {})
    validation = result.get("validation", {})
    sim_analysis = result.get("sim_analysis", {})

    print()
    print(f"  {'=' * 50}")
    print(f"  EVALUATION RESULTS")
    print(f"  {'=' * 50}")
    print(f"  Sync score:       {score.get('sync_score', 0):.4f}")
    print(f"  Classification:   {score.get('classification', '?')}")
    print()

    scores = score.get("scores", {})
    if scores:
        print(f"  Layer Scores:")
        for layer, val in scores.items():
            filled = int(val * 20)
            bar = "#" * filled + "." * (20 - filled)
            print(f"    {layer:<15s} [{bar}] {val:.4f}")
        print()

    if bridge_eval:
        print(f"  Bridge:")
        print(f"    R2 (bridge vs V4):  {bridge_eval.get('R2_bridge_vs_v4', 0):.4f}")
        print(f"    t50 bridge:         {bridge_eval.get('t50_bridge', '?')}")
        print(f"    t50 V4:             {bridge_eval.get('t50_v4', '?')}")
        print()

    if validation and validation.get("direction_accuracy") is not None:
        print(f"  Expression:")
        print(f"    Direction accuracy: {validation['direction_accuracy']:.1%}")
        print(f"    Classification:     {validation.get('classification', '?')}")
        mag = validation.get("mean_magnitude_error_log2")
        if mag is not None:
            print(f"    Mean |delta log2 FC|: {mag:.3f}")
        print()

    sync = score.get("sync_score", 0)
    print(f"  Interpretation:")
    if sync >= 0.75:
        print(f"    The route hypothesis '{route_id}' is STRONGLY supported.")
        print(f"    All evidence layers converge.")
    elif sync >= 0.5:
        print(f"    The route hypothesis '{route_id}' has MODERATE support.")
        weak = [k for k, v in scores.items() if v < 0.5]
        if weak:
            print(f"    Weaker layers: {', '.join(weak)}")
    else:
        print(f"    The route hypothesis '{route_id}' has WEAK support (sync={sync:.3f}).")
        print(f"    This may indicate insufficient data or parameter mismatch.")
    print()


# ═══════════════════════════════════════════════════════════════
# COMMAND: doctor
# ═══════════════════════════════════════════════════════════════
def cmd_doctor(args):
    """Diagnose issues with a config or system setup."""
    from mrhp.config.loader import load_config
    from mrhp.models.frozen import (ALL_ROUTES, V4_PARAMS, BRIDGE_V5_PARAMS,
                                     EXPRESSION_CALIBRATIONS)

    cfg_path = resolve_config(args.config)
    if not cfg_path:
        sys.exit(f"ERROR: Config not found: {args.config}")

    print(f"\n{'=' * 60}")
    print(f"  MRHP DOCTOR -- Diagnostics")
    print(f"  Config: {os.path.basename(cfg_path)}")
    print(f"{'=' * 60}\n")

    issues = []
    warnings = []
    ok = []

    try:
        cfg = load_config(cfg_path)
        ok.append("Config loaded successfully")
    except Exception as e:
        issues.append(f"Config load FAILED: {e}")
        _print_diagnosis(issues, warnings, ok)
        return

    for key in ["organism", "target", "route_hypothesis"]:
        if key in cfg:
            ok.append(f"Key '{key}' present")
        else:
            issues.append(f"Missing required key: '{key}'")

    hyp = cfg.get("route_hypothesis", {})
    route_id = hyp.get("route_id", "")
    dye_code = hyp.get("dye_code", "")

    if route_id:
        if route_id in ALL_ROUTES:
            ok.append(f"Route '{route_id}' found in catalog "
                      f"({len(ALL_ROUTES[route_id].get('steps', []))} steps)")
        elif hyp.get("steps"):
            ok.append(f"Route '{route_id}' defined in YAML (custom, {len(hyp['steps'])} steps)")
        else:
            issues.append(f"Route '{route_id}' NOT found in catalog and no custom steps")
    else:
        issues.append("No route_id specified")

    if dye_code:
        if dye_code in V4_PARAMS:
            ok.append(f"Dye code '{dye_code}' has V4 parameters")
        else:
            warnings.append(f"Dye code '{dye_code}' has NO V4 parameters")
        if dye_code in BRIDGE_V5_PARAMS:
            ok.append(f"Dye code '{dye_code}' has Bridge V5 parameters")
        else:
            warnings.append(f"Dye code '{dye_code}' has NO Bridge V5 parameters")
    else:
        warnings.append("No dye_code specified")

    if dye_code:
        calib_genes = [c[0] for c in EXPRESSION_CALIBRATIONS if c[1] == dye_code]
        if calib_genes:
            ok.append(f"Expression calibrations: {len(calib_genes)} genes for {dye_code}")
        else:
            warnings.append(f"No expression calibrations for '{dye_code}'")

    ctx = cfg.get("context", {})
    if ctx.get("yc") is not None:
        ok.append(f"Context: yc={ctx['yc']} g/L")
    else:
        warnings.append("No yeast extract concentration (context.yc)")
    if ctx.get("dic") is not None:
        ok.append(f"Context: dic={ctx['dic']} mM")
    else:
        warnings.append("No DIC concentration (context.dic)")

    for pkg_name in ["numpy", "scipy", "matplotlib", "yaml"]:
        try:
            mod = __import__(pkg_name)
            ok.append(f"{pkg_name} {getattr(mod, '__version__', 'OK')}")
        except ImportError:
            (issues if pkg_name in ("numpy", "scipy", "yaml")
             else warnings).append(f"{pkg_name} not installed")

    try:
        from mrhp.simulation.route_builder import build_route
        route = build_route(cfg)
        ok.append(f"Route builds OK: {route['n_steps']} steps, "
                  f"confidence={route['overall_confidence']:.3f}")
    except Exception as e:
        issues.append(f"Route build FAILED: {e}")

    try:
        from mrhp.simulation.ode_solver import build_stoichiometry, simulate_ode
        stoich = build_stoichiometry(route, cfg)
        sim = simulate_ode(stoich, cfg)
        if sim["success"]:
            ok.append(f"ODE converges: {len(sim['t'])} time points")
        else:
            issues.append(f"ODE failed: {sim['message']}")
    except Exception as e:
        issues.append(f"ODE simulation FAILED: {e}")

    _print_diagnosis(issues, warnings, ok)


def _print_diagnosis(issues, warnings, ok):
    print(f"  CHECKS: {len(ok)} OK, {len(warnings)} warnings, {len(issues)} issues\n")
    for item in ok:
        print(f"  [OK]   {item}")
    if warnings:
        print()
        for item in warnings:
            print(f"  [WARN] {item}")
    if issues:
        print()
        for item in issues:
            print(f"  [FAIL] {item}")
    print()
    if issues:
        print(f"  VERDICT: {len(issues)} issue(s) found -- fix before running.")
    elif warnings:
        print(f"  VERDICT: Ready to run ({len(warnings)} non-critical warning(s)).")
    else:
        print(f"  VERDICT: All checks passed -- ready to run.")


# ═══════════════════════════════════════════════════════════════
# COMMAND: validate
# ═══════════════════════════════════════════════════════════════
def cmd_validate(args):
    """Quick import and structural validation."""
    print(f"\n{'=' * 60}")
    print(f"  MRHP VALIDATE -- Structural Check")
    print(f"{'=' * 60}\n")

    ok = []
    issues = []

    modules = [
        "mrhp", "mrhp.config.loader", "mrhp.io.writers",
        "mrhp.models.frozen", "mrhp.simulation.route_builder",
        "mrhp.simulation.ode_solver", "mrhp.bridge.engine",
        "mrhp.expression.simulator", "mrhp.integration.omics",
        "mrhp.scoring.scorer", "mrhp.reporting.markdown",
        "mrhp.plotting.figures", "mrhp.core.pipeline",
    ]

    for mod_name in modules:
        try:
            __import__(mod_name)
            ok.append(f"import {mod_name}")
        except Exception as e:
            issues.append(f"import {mod_name} FAILED: {e}")

    try:
        from mrhp import __version__
        ok.append(f"Version: {__version__}")
    except Exception:
        issues.append("Cannot read __version__")

    try:
        from mrhp import run_pipeline
        ok.append("Top-level API: run_pipeline available")
    except Exception:
        issues.append("Top-level API: run_pipeline not importable")

    _print_diagnosis(issues, [], ok)


# ═══════════════════════════════════════════════════════════════
# MAIN PARSER
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        prog="mrhp",
        description="Multiscale Route Hypothesis Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  run       Run a single hypothesis evaluation
  compare   Compare two route hypotheses head-to-head
  explain   Interpret and narrate results from a config
  doctor    Diagnose issues with a config or system
  validate  Quick import and structural validation

Examples:
  mrhp run      --config configs/shewanella_mo.yaml
  mrhp compare  --config configs/shewanella_rc.yaml --alt configs/shewanella_rc_gentisate.yaml
  mrhp explain  --config configs/ecoli_fucose.yaml
  mrhp doctor   --config configs/acidithiobacillus_fe.yaml
  mrhp validate
""",
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # run
    p_run = sub.add_parser("run", help="Run hypothesis evaluation")
    p_run.add_argument("--config", "-c", nargs="+", required=True, help="YAML config(s)")
    p_run.add_argument("--output", "-o", default=None, help="Output base directory")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare two hypotheses")
    p_cmp.add_argument("--config", "-c", required=True, help="Primary config YAML")
    p_cmp.add_argument("--alt", "-a", required=True, help="Alternative config YAML")
    p_cmp.add_argument("--output", "-o", default=None, help="Output base directory")

    # explain
    p_exp = sub.add_parser("explain", help="Interpret results")
    p_exp.add_argument("--config", "-c", required=True, help="YAML config")
    p_exp.add_argument("--output", "-o", default=None, help="Output base directory")

    # doctor
    p_doc = sub.add_parser("doctor", help="Diagnose config/system")
    p_doc.add_argument("--config", "-c", required=True, help="YAML config")

    # validate
    sub.add_parser("validate", help="Quick import/structure check")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "run": cmd_run,
        "compare": cmd_compare,
        "explain": cmd_explain,
        "doctor": cmd_doctor,
        "validate": cmd_validate,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
