"""Unit tests for bridge engine."""


def test_compute_bridge_mo():
    """Test bridge computation for MO."""
    from mrhp.simulation.route_builder import build_route
    from mrhp.simulation.ode_solver import build_stoichiometry, simulate_ode
    from mrhp.bridge.engine import compute_bridge, evaluate_bridge

    cfg = {
        "organism": "Test",
        "target": "test",
        "route_hypothesis": {"route_id": "MO_DMPD_to_TCA", "dye_code": "MO"},
        "context": {"yc": 3.0, "dic": 0.6, "t_max": 48},
        "expression": {"enabled": False},
    }
    route = build_route(cfg)
    stoich = build_stoichiometry(route, cfg)
    sim = simulate_ode(stoich, cfg)

    bridge = compute_bridge("MO", cfg["context"], sim)
    assert "t" in bridge
    assert "D_v4" in bridge

    evaluation = evaluate_bridge(bridge)
    assert "R2_bridge_vs_v4" in evaluation
    r2 = evaluation["R2_bridge_vs_v4"]
    assert isinstance(r2, float)
