# Frozen Models Reference

All model parameters in MRHP are version-locked ("frozen") to ensure
reproducibility. This document describes each frozen model.

## V4 Hill Model

14-parameter phenotype model for dye decolorization kinetics.

```
D(t) = Dmax / (1 + ((t_lag / t)^n) * exp(-k * (t - t_lag)))
```

Parameters per dye code (MO, RC, DB):
- `Dmax`: maximum decolorization (%)
- `k`: rate constant (h⁻¹)
- `n`: Hill coefficient
- `t_lag`: lag phase duration (h)
- Additional context-dependent corrections

## Bridge V5 Dual Canonical

Connects top-down phenotype prediction (V4 Hill) with bottom-up
ODE metabolic simulation via a dual canonical bridge function.

Key parameters:
- `Vmax`, `Kd`: substrate-level bridge kinetics
- `alpha_p`, `k_p`: phenotype coupling
- `lam`: bridge scaling factor

## Expression V3 ODE

Gene expression dynamics modeled as first-order ODE with induction:

```
dE/dt = k_basal + k_ind * S(t) - k_deg * E
```

Where:
- `k_basal`: basal transcription rate
- `k_ind`: induction rate by substrate
- `k_deg`: mRNA degradation rate
- `S(t)`: inducer concentration from metabolic ODE

## Calibrated Genes

27 gene calibrations for Shewanella LC6 across MO, RC, DB:

| Gene | Dyes | Calibration Source |
|------|------|---------|
| AzoR | MO, RC, DB | RT-qPCR ΔΔCt |
| CymA | MO, RC, DB | RT-qPCR ΔΔCt |
| YhhW | MO, RC | RT-qPCR ΔΔCt |
| fhuE_1 | MO, RC, DB | RT-qPCR ΔΔCt |
| fhuF | MO, RC, DB | RT-qPCR ΔΔCt |
| iucA_iucC | MO, RC, DB | RT-qPCR ΔΔCt |
| iucD | MO, RC, DB | RT-qPCR ΔΔCt |

## Route Catalogs

### MO (Methyl Orange)
- `MO_DMPD_to_TCA`: DMPD branch via catechol to TCA (8 steps)
- `MO_sulfanilic_acid_route`: SA branch via protocatechuate (6 steps)

### RC (Reactive Crimson)
- `RC_catechol_route`: Catechol ortho-cleavage to TCA (8 steps)

### DB (Direct Blue 71)
- `DB_protocatechuate_route`: Protocatechuate meta-cleavage to TCA (8 steps)

## NMR Evidence

Metabolite detection data from NMR experiments on Shewanella LC6:
- MO: succinate detected, acetate detected
- Sulfanilic acid: detected in spent medium
