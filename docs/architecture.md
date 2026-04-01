# Architecture

## Package Layout

```
src/mrhp/
├── __init__.py          # Top-level API: run_pipeline, load_config
├── cli.py               # CLI entry point (mrhp command)
├── config/
│   └── loader.py        # YAML config loading and validation
├── core/
│   └── pipeline.py      # 10-phase orchestrator
├── models/
│   └── frozen.py        # All frozen parameters, calibrations, routes
├── simulation/
│   ├── route_builder.py # Route construction from catalog or YAML
│   └── ode_solver.py    # Stoichiometry + Radau ODE solver
├── bridge/
│   └── engine.py        # V4 Hill + V5 dual canonical bridge
├── expression/
│   └── simulator.py     # Gene expression ODE + RT-qPCR validation
├── integration/
│   └── omics.py         # Omics evidence integration
├── scoring/
│   └── scorer.py        # Weighted sync scoring + ranking
├── reporting/
│   └── markdown.py      # Markdown report generation
├── plotting/
│   └── figures.py       # Publication-grade matplotlib figures
└── skill_mode/
    └── hooks.py         # AI-assisted mode entry points
```

## Pipeline Phases

The core pipeline (`run_single`) executes 10 sequential phases:

| Phase | Name | Module |
|-------|------|--------|
| 0 | Snapshot inputs | `io.writers` |
| 1 | Config validation | `config.loader` |
| 2 | Route construction | `simulation.route_builder` |
| 3 | ODE simulation | `simulation.ode_solver` |
| 4 | Bridge prediction | `bridge.engine` |
| 5 | Expression simulation | `expression.simulator` |
| 6 | RT-qPCR validation | `expression.simulator` |
| 7 | Omics integration | `integration.omics` |
| 8 | Hypothesis scoring | `scoring.scorer` |
| 9 | Report generation | `reporting.markdown` |
| 10 | Figure generation | `plotting.figures` |

## Frozen Models

All model parameters are version-locked in `models/frozen.py`:

- **V4 Hill**: 14-parameter phenotype model (Dmax, k, n, t_lag, ...)
- **Bridge V5**: Dual canonical bridge connecting top-down and bottom-up
- **Expression V3**: ODE-based gene expression with 27 calibrated genes
- **Route Catalogs**: MO (2 routes), RC (1 route), DB (1 route)

## Scoring

Weighted synchronization score with 4 layers:

| Layer | Weight | Source |
|-------|--------|--------|
| Metabolism | 0.25 | ODE connectivity + convergence |
| Bridge | 0.25 | R² bridge vs V4 |
| Expression | 0.30 | Direction accuracy + magnitude |
| Omics | 0.20 | NMR + redox evidence |

## Cross-System Generalization

The platform was validated across 3 organisms:
- *Shewanella xiamenensis* LC6 (azo dye degradation)
- *E. coli* BL21 (L-fucose production)
- *Acidithiobacillus ferrooxidans* (Fe²⁺ oxidation)

Achieving UNIVERSAL_PREDICTIVE classification (R² > 0.93 for all three).
