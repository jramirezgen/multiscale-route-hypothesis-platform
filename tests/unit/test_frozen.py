"""Unit tests for frozen models."""


def test_v4_params_keys():
    """Test V4 params have expected dye codes."""
    from mrhp.models.frozen import V4_PARAMS
    assert "MO" in V4_PARAMS
    assert "RC" in V4_PARAMS
    assert "DB" in V4_PARAMS


def test_bridge_v5_params():
    """Test Bridge V5 params exist."""
    from mrhp.models.frozen import BRIDGE_V5_PARAMS
    assert "MO" in BRIDGE_V5_PARAMS
    # V5 bridge params have specific parameter names
    mo_params = BRIDGE_V5_PARAMS["MO"]
    assert isinstance(mo_params, dict)
    assert len(mo_params) > 0
    # Check some known keys
    assert "Vmax" in mo_params or "alpha_p" in mo_params


def test_all_routes():
    """Test route catalog completeness."""
    from mrhp.models.frozen import ALL_ROUTES
    assert "MO_DMPD_to_TCA" in ALL_ROUTES
    assert "RC_catechol_route" in ALL_ROUTES
    assert "DB_protocatechuate_route" in ALL_ROUTES
    for rid, rdata in ALL_ROUTES.items():
        assert "steps" in rdata
        assert len(rdata["steps"]) > 0


def test_expression_calibrations():
    """Test calibration tuples are well-formed."""
    from mrhp.models.frozen import EXPRESSION_CALIBRATIONS
    assert len(EXPRESSION_CALIBRATIONS) >= 20
    for entry in EXPRESSION_CALIBRATIONS:
        assert len(entry) >= 6
        gene = entry[0]
        dye = entry[1]
        assert isinstance(gene, str)
        assert isinstance(dye, str)
        assert isinstance(entry[2], (int, float))


def test_core_revalidation_structure():
    """Test CORE_REVALIDATION frozen dict has required structure."""
    from mrhp.models.frozen import CORE_REVALIDATION
    assert CORE_REVALIDATION["verdict"] == "CORE_MODEL_SUFFICIENT"
    for system in ["shewanella", "ecoli", "acidithiobacillus"]:
        assert system in CORE_REVALIDATION
        assert "core_R2" in CORE_REVALIDATION[system] or "core3_R2" in CORE_REVALIDATION[system]


def test_lambda_b_law_structure():
    """Test LAMBDA_B_LAW frozen dict has required structure."""
    from mrhp.models.frozen import LAMBDA_B_LAW
    assert "intercept" in LAMBDA_B_LAW
    assert "slope" in LAMBDA_B_LAW
    assert "R2" in LAMBDA_B_LAW
    assert "formula" in LAMBDA_B_LAW
    assert LAMBDA_B_LAW["R2"] > 0.99
