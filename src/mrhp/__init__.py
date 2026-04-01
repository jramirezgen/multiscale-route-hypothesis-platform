""" 
MRHP — Multiscale Route Hypothesis Platform
============================================

Evaluate metabolic route hypotheses from YAML config to phenotype prediction.

Quick start::

    from mrhp import run_pipeline, load_config

    result = run_pipeline("configs/shewanella_mo.yaml")
    print(result["score"]["sync_score"])

"""

__version__ = "1.0.0"

from mrhp.config.loader import load_config  # noqa: F401
from mrhp.core.pipeline import run_pipeline, run_single  # noqa: F401

__all__ = ["load_config", "run_pipeline", "run_single", "__version__"]
