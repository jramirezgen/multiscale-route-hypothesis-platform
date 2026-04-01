"""YAML configuration loader and validator."""

import yaml


_REQUIRED_KEYS = ("organism", "target", "route_hypothesis")


def load_config(yaml_path: str) -> dict:
    """Load and validate a YAML experiment configuration.

    Parameters
    ----------
    yaml_path : str
        Path to the YAML config file.

    Returns
    -------
    dict
        Validated configuration dictionary.

    Raises
    ------
    ValueError
        If required keys are missing.
    """
    with open(yaml_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    for key in _REQUIRED_KEYS:
        if key not in cfg:
            raise ValueError(f"Missing required config key: '{key}'")

    cfg.setdefault("bridge", {"enabled": True})
    cfg.setdefault("expression", {"enabled": True})
    cfg.setdefault("validation", {})
    cfg.setdefault("output", {})
    cfg.setdefault("context", {})
    cfg.setdefault("gem", {})

    return cfg


def get_dye_code(cfg: dict) -> str:
    """Return internal dye code from config."""
    return cfg.get("route_hypothesis", {}).get("dye_code", "")
