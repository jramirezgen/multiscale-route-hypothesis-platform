"""Unit tests for bridge engine."""

import pytest


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


def test_bridge_core_mode():
    """Test core bridge mode (canonical): no Ψ, no B^α."""
    from mrhp.bridge.engine import compute_bridge, evaluate_bridge
    import numpy as np

    context = {"yc": 3.0, "dic": 0.6, "beta": 0.5}
    bridge = compute_bridge("MO", context, mode="core")
    assert bridge is not None
    assert bridge["mode"] == "core"
    # Core mode: Psi should be all ones (not used)
    assert np.allclose(bridge["Psi"], 1.0)
    # Bridge should produce a valid prediction
    assert bridge["y_bridge"][-1] > 0
    evaluation = evaluate_bridge(bridge)
    assert isinstance(evaluation["R2_bridge_vs_v4"], float)


def test_bridge_full_mode():
    """Test full bridge mode (legacy): includes Ψ and B^α."""
    from mrhp.bridge.engine import compute_bridge
    import numpy as np

    context = {"yc": 3.0, "dic": 0.6}
    bridge = compute_bridge("MO", context, mode="full")
    assert bridge is not None
    assert bridge["mode"] == "full"
    # Full mode: Psi should vary (not all ones)
    assert not np.allclose(bridge["Psi"], 1.0)
    assert bridge["Psi"][0] < bridge["Psi"][-1]


def test_bridge_core_vs_full_differ():
    """Core and full modes should produce different predictions."""
    from mrhp.bridge.engine import compute_bridge
    import numpy as np

    context = {"yc": 3.0, "dic": 0.6}
    core = compute_bridge("MO", context, mode="core")
    full = compute_bridge("MO", context, mode="full")
    # Predictions should differ (Ψ and B^α modulate the full model)
    assert not np.allclose(core["y_bridge"], full["y_bridge"], atol=0.1)


def test_bridge_default_is_core():
    """Default bridge mode should be 'core' (canonical)."""
    from mrhp.bridge.engine import compute_bridge

    context = {"yc": 3.0, "dic": 0.6}
    bridge = compute_bridge("MO", context)
    assert bridge["mode"] == "core"


def test_bridge_beta_passthrough():
    """Beta parameter should be passed through to bridge result."""
    from mrhp.bridge.engine import compute_bridge
    import numpy as np

    context = {"yc": 3.0, "dic": 0.6}
    bridge = compute_bridge("MO", context, beta=0.35)
    assert bridge["beta"] == 0.35


def test_bridge_invalid_mode_raises():
    """Invalid bridge mode should raise ValueError."""
    from mrhp.bridge.engine import compute_bridge

    context = {"yc": 3.0, "dic": 0.6}
    with pytest.raises(ValueError, match="Invalid bridge mode"):
        compute_bridge("MO", context, mode="invalid")


def test_bridge_core_all_dyes():
    """Core bridge should work for all dye codes."""
    from mrhp.bridge.engine import compute_bridge, evaluate_bridge

    context = {"yc": 3.0, "dic": 0.6}
    for dye in ["MO", "RC", "DB"]:
        bridge = compute_bridge(dye, context, mode="core")
        assert bridge is not None, f"Core bridge failed for {dye}"
        evaluation = evaluate_bridge(bridge)
        assert isinstance(evaluation["R2_bridge_vs_v4"], float)


def test_core_revalidation_frozen():
    """Verify frozen revalidation results are accessible."""
    from mrhp.models.frozen import CORE_REVALIDATION, LAMBDA_B_LAW

    assert CORE_REVALIDATION["verdict"] == "CORE_MODEL_SUFFICIENT"
    assert CORE_REVALIDATION["shewanella"]["core3_R2"] > 0.95
    assert CORE_REVALIDATION["ecoli"]["core_R2"] > 0.95
    assert CORE_REVALIDATION["acidithiobacillus"]["core_R2"] > 0.95

    assert abs(LAMBDA_B_LAW["slope"] + 1.013) < 0.01
    assert LAMBDA_B_LAW["R2"] > 0.99
