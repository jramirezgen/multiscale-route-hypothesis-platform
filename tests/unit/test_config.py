"""Unit tests for config loader."""

import os
import tempfile
import pytest
import yaml


def test_load_config_valid():
    """Test loading a valid config."""
    from mrhp.config.loader import load_config

    cfg_data = {
        "organism": "Test_org",
        "target": "test_target",
        "route_hypothesis": {
            "route_id": "test_route",
            "dye_code": "MO",
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(cfg_data, f)
        tmp_path = f.name

    try:
        cfg = load_config(tmp_path)
        assert cfg["organism"] == "Test_org"
        assert cfg["target"] == "test_target"
        assert cfg["route_hypothesis"]["route_id"] == "test_route"
        # Defaults filled in
        assert "context" in cfg
        assert "expression" in cfg
    finally:
        os.unlink(tmp_path)


def test_load_config_missing_keys():
    """Test that missing required keys raise ValueError."""
    from mrhp.config.loader import load_config

    cfg_data = {"organism": "Test_org"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(cfg_data, f)
        tmp_path = f.name

    try:
        with pytest.raises(ValueError):
            load_config(tmp_path)
    finally:
        os.unlink(tmp_path)


def test_get_dye_code():
    """Test dye code extraction."""
    from mrhp.config.loader import get_dye_code

    cfg = {"route_hypothesis": {"dye_code": "RC"}, "target": "x"}
    assert get_dye_code(cfg) == "RC"

    cfg = {"route_hypothesis": {"dye_code": "MO"}, "target": "MO_something"}
    assert get_dye_code(cfg) == "MO"

    # When no dye_code but target has underscore
    cfg2 = {"route_hypothesis": {}, "target": "MO_something"}
    # get_dye_code uses route_hypothesis.dye_code first
    result = get_dye_code(cfg2)
    assert isinstance(result, str)
