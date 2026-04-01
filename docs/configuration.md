# Configuration Guide

## Overview

MRHP uses YAML configuration files to define hypothesis evaluations.
Each config specifies an organism, target, metabolic route hypothesis,
and optional expression/omics settings.

## Required Fields

```yaml
organism: Shewanella_xiamenensis_LC6
target: methyl_orange_decolorization
route_hypothesis:
  route_id: MO_DMPD_to_TCA
  dye_code: MO
```

## Context Parameters

```yaml
context:
  yc: 3.0        # yeast extract (g/L)
  dic: 0.6       # dissolved inorganic carbon (mM)
  t_max: 48.0    # simulation time (h)
  dye_conc: 100  # initial dye concentration (mg/L)
  temperature: 30
```

## Route Hypothesis

Routes can come from two sources:

### 1. Frozen Catalog

If `route_id` matches a catalog route (e.g., `MO_DMPD_to_TCA`), the
steps are loaded automatically from `models/frozen.py`.

### 2. Custom YAML Steps

Define steps directly in the config:

```yaml
route_hypothesis:
  route_id: my_custom_route
  steps:
    - id: S01
      rxn: reaction_name
      substrates: [A, NADH]
      products: [B, NAD]
      enzyme: MyEnzyme
      gene: myGene
      confidence: plausible
```

### Confidence Levels

| Level | Weight | Meaning |
|-------|--------|---------|
| exact | 1.0 | Experimentally verified |
| strong | 0.8 | Strong bioinformatic evidence |
| plausible | 0.5 | Literature-supported |
| speculative | 0.3 | Hypothetical |

## Expression Settings

```yaml
expression:
  enabled: true
  simulate_hourly: true
  genes_key:
    - AzoR
    - CymA
```

When `enabled: true`, the platform simulates gene expression dynamics
and validates against RT-qPCR data (if available for the dye_code).

## Omics Settings

```yaml
omics:
  nmr: true           # Use NMR metabolite evidence
  redox_balance: true  # Check NADH/NAD balance
```

## Templates

See `templates/config_minimal.yaml` and `templates/config_full.yaml`
for ready-to-use starting points.
