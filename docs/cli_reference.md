# CLI Reference

## Installation

```bash
pip install -e .
```

After installation, the `mrhp` command is available system-wide.

## Commands

### `mrhp run`

Run the full 10-phase pipeline for one or more hypothesis configs.

```bash
mrhp run --config configs/shewanella_mo.yaml
mrhp run -c configs/shewanella_mo.yaml configs/shewanella_rc.yaml
mrhp run -c configs/shewanella_mo.yaml -o ./my_output_dir
```

Options:
- `--config`, `-c`: One or more YAML config paths (required)
- `--output`, `-o`: Output base directory (default: current directory)

When multiple configs are provided, a multi-hypothesis ranking is generated.

### `mrhp compare`

Compare two route hypotheses head-to-head.

```bash
mrhp compare --config configs/shewanella_rc.yaml --alt configs/shewanella_rc_gentisate.yaml
```

Options:
- `--config`, `-c`: Primary config YAML (required)
- `--alt`, `-a`: Alternative config YAML (required)
- `--output`, `-o`: Output base directory

### `mrhp explain`

Interpret and narrate results from a config.

```bash
mrhp explain --config configs/ecoli_fucose.yaml
```

### `mrhp doctor`

Diagnose issues with a config or system setup.

```bash
mrhp doctor --config configs/acidithiobacillus_fe.yaml
```

### `mrhp validate`

Quick import and structural validation.

```bash
mrhp validate
```

## Python API

```python
from mrhp import run_pipeline, load_config

# Full pipeline
result = run_pipeline("configs/shewanella_mo.yaml")
print(result["score"]["sync_score"])
print(result["score"]["classification"])

# Load config only
cfg = load_config("configs/shewanella_mo.yaml")
```

## Skill Mode (AI-Assisted)

```python
from mrhp.skill_mode.hooks import hook_run, hook_compare, hook_doctor

# Run
result = hook_run("configs/shewanella_mo.yaml")

# Compare
comparison = hook_compare("configs/shewanella_rc.yaml",
                          "configs/shewanella_rc_gentisate.yaml")
print(comparison["winner"])

# Doctor
diag = hook_doctor("configs/shewanella_mo.yaml")
print(diag["verdict"])
```
