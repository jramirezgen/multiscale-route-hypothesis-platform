"""Integration test: import validation."""


def test_all_imports():
    """Verify all submodules import cleanly."""
    import mrhp
    from mrhp import run_pipeline, load_config, __version__
    from mrhp.config.loader import load_config as lc2
    from mrhp.io.writers import write_json, write_md
    from mrhp.models.frozen import V4_PARAMS, ALL_ROUTES
    from mrhp.simulation.route_builder import build_route
    from mrhp.simulation.ode_solver import simulate_ode
    from mrhp.bridge.engine import compute_bridge
    from mrhp.expression.simulator import simulate_expression
    from mrhp.integration.omics import integrate_omics
    from mrhp.scoring.scorer import score_hypothesis
    from mrhp.reporting.markdown import generate_report
    from mrhp.plotting.figures import generate_figures
    from mrhp.core.pipeline import run_single
    from mrhp.skill_mode.hooks import hook_run, hook_doctor

    assert __version__ == "1.1.0"
    assert callable(run_pipeline)
    assert callable(hook_run)
