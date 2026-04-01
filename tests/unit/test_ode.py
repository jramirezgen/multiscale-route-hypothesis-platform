"""Unit tests for ODE solver."""

import numpy as np


def _make_route_and_stoich():
    from mrhp.simulation.route_builder import build_route
    from mrhp.simulation.ode_solver import build_stoichiometry

    cfg = {
        "organism": "Test",
        "target": "test",
        "route_hypothesis": {"route_id": "MO_DMPD_to_TCA", "dye_code": "MO"},
        "context": {"t_max": 48},
        "expression": {"enabled": False},
    }
    route = build_route(cfg)
    stoich = build_stoichiometry(route, cfg)
    return stoich, cfg


def test_simulate_ode_converges():
    """Test that the ODE solver converges."""
    from mrhp.simulation.ode_solver import simulate_ode

    stoich, cfg = _make_route_and_stoich()
    result = simulate_ode(stoich, cfg)
    assert result["success"] is True
    assert len(result["t"]) > 10
    assert np.all(np.isfinite(result["y"]))


def test_analyze_dynamics():
    """Test dynamics analysis returns expected keys."""
    from mrhp.simulation.ode_solver import simulate_ode, analyze_dynamics
    from mrhp.simulation.route_builder import build_route

    cfg = {
        "organism": "Test",
        "target": "test",
        "route_hypothesis": {"route_id": "MO_DMPD_to_TCA", "dye_code": "MO"},
        "context": {"t_max": 48},
        "expression": {"enabled": False},
    }
    route = build_route(cfg)
    from mrhp.simulation.ode_solver import build_stoichiometry
    stoich = build_stoichiometry(route, cfg)
    sim = simulate_ode(stoich, cfg)
    analysis = analyze_dynamics(sim, route)
    # Check for expected keys in analysis output
    assert "bottleneck_reaction" in analysis or "connectivity_score" in analysis
    assert "substrate_consumed_pct" in analysis or "robustness_score" in analysis
