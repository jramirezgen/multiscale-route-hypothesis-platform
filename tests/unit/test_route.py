"""Unit tests for route builder."""


def _make_cfg(route_id="MO_DMPD_to_TCA", dye_code="MO"):
    return {
        "organism": "Test",
        "target": "test",
        "route_hypothesis": {
            "route_id": route_id,
            "dye_code": dye_code,
        },
        "context": {"t_max": 48},
        "expression": {"enabled": False},
    }


def test_build_route_from_catalog():
    """Test building a route from the frozen catalog."""
    from mrhp.simulation.route_builder import build_route

    cfg = _make_cfg()
    route = build_route(cfg)
    assert route["route_id"] == "MO_DMPD_to_TCA"
    assert route["n_steps"] > 0
    assert "all_genes" in route
    assert 0 < route["overall_confidence"] <= 1.0


def test_build_route_from_yaml():
    """Test building a route from custom YAML steps."""
    from mrhp.simulation.route_builder import build_route

    cfg = _make_cfg(route_id="custom_test")
    cfg["route_hypothesis"]["steps"] = [
        {
            "id": "S01",
            "rxn": "rxn_1",
            "substrates": ["A"],
            "products": ["B"],
            "enzyme": "Enz1",
            "gene": "gene1",
            "confidence": "exact",
        },
        {
            "id": "S02",
            "rxn": "rxn_2",
            "substrates": ["B", "NADH"],
            "products": ["C", "NAD"],
            "enzyme": "Enz2",
            "gene": "gene2",
            "confidence": "plausible",
        },
    ]
    route = build_route(cfg)
    assert route["route_id"] == "custom_test"
    assert route["n_steps"] == 2
    assert "gene1" in route["all_genes"]


def test_build_stoichiometry():
    """Test stoichiometry matrix construction."""
    from mrhp.simulation.route_builder import build_route
    from mrhp.simulation.ode_solver import build_stoichiometry

    cfg = _make_cfg()
    route = build_route(cfg)
    stoich = build_stoichiometry(route, cfg)
    assert "S" in stoich
    assert "metabolites" in stoich or "species" in stoich
    assert stoich["S"].shape[0] > 0
    assert stoich["S"].shape[1] > 0
