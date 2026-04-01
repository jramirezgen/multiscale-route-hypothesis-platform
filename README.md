# Multiscale Route Hypothesis Platform (MRHP)

A computational framework for evaluating metabolic route hypotheses through
multiscale integration of ODE simulation, phenotype bridging, gene expression
dynamics, and omics evidence.

## Features

- **10-phase pipeline**: From config to scored hypothesis in one command
- **Frozen models**: V4 Hill phenotype, Bridge V5 dual canonical, Expression V3 ODE
- **Cross-system validated**: Shewanella (azo dyes), E. coli (L-fucose), Acidithiobacillus (Fe²⁺)
- **3 usage modes**: CLI, Python API, AI-assisted hooks
- **Publication-grade figures**: 5 figure types with matplotlib GridSpec

## Quick Start

### Install

```bash
git clone https://github.com/jramirezgen/multiscale-route-hypothesis-platform.git
cd multiscale-route-hypothesis-platform
pip install -e .
```

### CLI

```bash
# Run a hypothesis evaluation
mrhp run --config configs/shewanella_mo.yaml

# Compare two routes
mrhp compare --config configs/shewanella_rc.yaml --alt configs/shewanella_rc_gentisate.yaml

# Diagnose config issues
mrhp doctor --config configs/acidithiobacillus_fe.yaml

# Explain results
mrhp explain --config configs/ecoli_fucose.yaml

# Validate installation
mrhp validate
```

### Python API

```python
from mrhp import run_pipeline

result = run_pipeline("configs/shewanella_mo.yaml")
print(f"Score: {result['score']['sync_score']:.4f}")
print(f"Class: {result['score']['classification']}")
```

### AI-Assisted Mode

```python
from mrhp.skill_mode.hooks import hook_run, hook_compare, hook_doctor

result = hook_run("configs/shewanella_mo.yaml")
diag = hook_doctor("configs/shewanella_mo.yaml")
```

## Architecture

```
src/mrhp/
├── config/loader.py          # YAML config loading
├── core/pipeline.py          # 10-phase orchestrator
├── models/frozen.py          # Frozen parameters & routes
├── simulation/               # Route builder + ODE solver
├── bridge/engine.py          # V4 Hill + V5 bridge
├── expression/simulator.py   # Gene expression ODE
├── integration/omics.py      # Omics evidence
├── scoring/scorer.py         # Sync scoring
├── reporting/markdown.py     # Report generation
├── plotting/figures.py       # Publication figures
├── skill_mode/hooks.py       # AI-assisted entry points
└── cli.py                    # CLI entry point
```

## Scoring

Weighted synchronization score across 4 evidence layers:

| Layer | Weight | Source |
|-------|--------|--------|
| Metabolism | 0.25 | ODE connectivity & convergence |
| Bridge | 0.25 | R² phenotype prediction |
| Expression | 0.30 | Gene direction & magnitude accuracy |
| Omics | 0.20 | NMR & redox balance evidence |

## Cross-System Validation

| Organism | Target | R² | Classification |
|----------|--------|----|----------------|
| *S. xiamenensis* LC6 | Azo dye degradation | 0.9545 | CANONICAL_ROUTE_CONFIRMED |
| *E. coli* BL21 | L-fucose production | 0.9990 | ROUTE_COMPATIBLE |
| *A. ferrooxidans* | Fe²⁺ oxidation | 0.9413 | ROUTE_COMPATIBLE |

Platform classification: **UNIVERSAL_PREDICTIVE**

## Requirements

- Python >= 3.9
- numpy >= 1.21
- scipy >= 1.7
- matplotlib >= 3.5
- pyyaml >= 5.4

## Example GEM Models

Canonical genome-scale metabolic models are included in `examples/gems/` for
reproducing the published validation results.

## License

MIT License. See [LICENSE](LICENSE).

## Citation

If you use MRHP in your research, please cite:

```bibtex
@software{ramirez2026mrhp,
  author = {Ramirez, J.},
  title = {Multiscale Route Hypothesis Platform},
  year = {2026},
  version = {1.0.0},
  url = {https://github.com/jramirezgen/multiscale-route-hypothesis-platform}
}
```

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [CLI Reference](docs/cli_reference.md)
- [Frozen Models](docs/frozen_models.md)
