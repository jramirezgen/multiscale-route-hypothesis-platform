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

## Bridge — Core Model (Canonical, v1.1.0)

The canonical bridge connects metabolic drive (Φ) to observable phenotype:

```
y(t) = y_max · (1 − exp(−H(t)^β))
H(t) = ∫ λ · dΦ/dt dt
```

3 free parameters:
- `λ`: coupling constant (metabolic-to-phenotype scale factor)
- `β`: temporal heterogeneity exponent (< 1, stretched exponential)
- `y_max`: maximum observable level

### Structural Law

```
log₁₀(λ_b) = 0.918 − 1.013 × N_NADH
```

λ reflects redox cost per NADH equivalent consumed in observable transformation.

### Cross-System Revalidation (Core Model)

| System | R²_core | R²_full | Loss |
|--------|---------|---------|------|
| Shewanella (25 conditions) | 0.9839 | 0.9916 | 0.0077 |
| E. coli (7 datasets) | 0.9815 | 0.9959 | 0.0144 |
| Acidithiobacillus (1 experiment) | 0.9921 | 0.9942 | 0.0021 |

Verdict: **CORE_MODEL_SUFFICIENT**

## Bridge — Full Model (Legacy V5)

The full bridge includes activation gate and capacity feedback:

```
H(t) = ∫ λ · dΦ/dt · Ψ(t) · B^α dt
Ψ(t) = 1 − exp(−k_p · t)
B = min(D_v4 / 100, 1)
```

Use `bridge.mode: full` in YAML config to select this mode.

Key parameters per dye:
- `Vmax`: maximum bridge driving rate
- `Kd`: dye inhibition constant
- `alpha_p`: substrate-dye interaction
- `k_p`: activation rate constant
- `lam`: coupling constant (λ)

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
|------|------|--------------------|
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
