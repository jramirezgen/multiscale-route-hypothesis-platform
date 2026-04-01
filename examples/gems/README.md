# Canonical GEM Models

Reference genome-scale metabolic models used for MRHP validation.

| Organism | File | Reactions | Metabolites | Genes |
|----------|------|-----------|-------------|-------|
| *S. xiamenensis* BC01 (LC6) | `LC6_CANONICAL.xml` | 2972 | 2565 | 871 |
| *E. coli* BL21(DE3) — fucose | `Ecoli_BL21.xml` | 2583 | 1878 | 1267 |
| *A. ferrooxidans* ATCC 23270 | `Aferro_ATCC23270_curated_v6.xml` | 3353 | 2747 | 867 |

## Usage

These GEMs are referenced by configs in `configs/`. The `gem.model_path` key
in each YAML points to the model file. Example:

```yaml
gem:
  model_path: "examples/gems/LC6_CANONICAL.xml"
```

## Format

All models are SBML Level 3 Version 1 with FBC v2 package.
