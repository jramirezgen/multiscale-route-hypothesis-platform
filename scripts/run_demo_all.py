#!/usr/bin/env python3
"""Run all 6 example configs as a demo."""

import os
import sys
import tempfile


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(repo, "src")
    if src not in sys.path:
        sys.path.insert(0, src)

    from mrhp.config.loader import load_config
    from mrhp.core.pipeline import run_single

    configs_dir = os.path.join(repo, "configs")
    yamls = sorted(f for f in os.listdir(configs_dir) if f.endswith(".yaml"))

    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for yf in yamls:
            cfg_path = os.path.join(configs_dir, yf)
            print(f"\n{'=' * 60}")
            print(f"  Running: {yf}")
            print(f"{'=' * 60}")
            try:
                cfg = load_config(cfg_path)
                result = run_single(cfg, cfg_path, tmpdir)
                score = result.get("score", {})
                results.append({
                    "config": yf,
                    "route_id": result.get("route_id", "?"),
                    "sync_score": score.get("sync_score", 0),
                    "classification": score.get("classification", "?"),
                    "error": result.get("error"),
                })
            except Exception as e:
                results.append({"config": yf, "error": str(e)})

    print(f"\n\n{'=' * 60}")
    print(f"  DEMO SUMMARY ({len(results)} configs)")
    print(f"{'=' * 60}")
    for r in results:
        if r.get("error"):
            print(f"  {r['config']}: ERROR - {r['error']}")
        else:
            print(f"  {r['config']}: {r['route_id']} -- "
                  f"Score={r['sync_score']:.4f} -- {r['classification']}")


if __name__ == "__main__":
    main()
