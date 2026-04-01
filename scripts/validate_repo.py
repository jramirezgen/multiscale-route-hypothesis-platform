#!/usr/bin/env python3
"""Validate repository structure and imports."""

import os
import sys


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(repo, "src")
    if src not in sys.path:
        sys.path.insert(0, src)

    ok = 0
    fail = 0

    # Check directories
    for d in ["src/mrhp", "configs", "templates", "docs", "tests"]:
        path = os.path.join(repo, d)
        if os.path.isdir(path):
            print(f"  [OK]   {d}/")
            ok += 1
        else:
            print(f"  [FAIL] {d}/ missing")
            fail += 1

    # Check key files
    for f in ["pyproject.toml", "README.md", "LICENSE", "CITATION.cff"]:
        path = os.path.join(repo, f)
        if os.path.isfile(path):
            print(f"  [OK]   {f}")
            ok += 1
        else:
            print(f"  [FAIL] {f} missing")
            fail += 1

    # Check imports
    modules = [
        "mrhp", "mrhp.config.loader", "mrhp.io.writers",
        "mrhp.models.frozen", "mrhp.simulation.route_builder",
        "mrhp.simulation.ode_solver", "mrhp.bridge.engine",
        "mrhp.expression.simulator", "mrhp.integration.omics",
        "mrhp.scoring.scorer", "mrhp.reporting.markdown",
        "mrhp.plotting.figures", "mrhp.core.pipeline",
        "mrhp.skill_mode.hooks", "mrhp.cli",
    ]

    for mod in modules:
        try:
            __import__(mod)
            print(f"  [OK]   import {mod}")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] import {mod}: {e}")
            fail += 1

    # Check configs
    configs_dir = os.path.join(repo, "configs")
    if os.path.isdir(configs_dir):
        yamls = [f for f in os.listdir(configs_dir) if f.endswith(".yaml")]
        print(f"  [OK]   {len(yamls)} config files")
        ok += 1

    print(f"\n  Results: {ok} OK, {fail} FAIL")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
