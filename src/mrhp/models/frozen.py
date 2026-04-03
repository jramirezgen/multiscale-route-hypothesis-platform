"""Frozen canonical model parameters.

DO NOT MODIFY these values. They are validated results from the project.
All parameters are frozen and version-controlled.
"""

# ═══════════════════════════════════════════════════════════════
# V4 HILL PHYSIOLOGICAL MODEL (14 parameters, frozen)
# ═══════════════════════════════════════════════════════════════
# D(t) = Dmax * (1 - exp(-Vmax * h(S,I) * max(t-lag, 0)))
# h(S,I) = (S^n / (K_S^n + S^n)) * (K_I / (K_I + I))

V4_PARAMS = {
    "K_yc": 5.23111,
    "K_dic": 0.141446,
    "MO": {"Dmax": 95.88, "Vmax": 3.29, "n": 1.81, "lag": 1.65},
    "RC": {"Dmax": 92.26, "Vmax": 2.93, "n": 2.83, "lag": 6.40},
    "DB": {"Dmax": 94.63, "Vmax": 0.74, "n": 0.84, "lag": 2.30},
}

# ═══════════════════════════════════════════════════════════════
# BRIDGE v5 DUAL CANONICAL (frozen)
# ═══════════════════════════════════════════════════════════════
BRIDGE_V5_PARAMS = {
    "MO": {
        "Vmax": 11.5198, "Kd": 1.0, "alpha_p": 0.2691, "k_p": 0.2104,
        "a_p": 63.9262, "b_p": 0.0637, "k2_p": 0.0414,
        "tau_1": 72.4185, "c_p": -1.3819, "lam": 0.53,
    },
    "RC": {
        "Vmax": 8.5434, "Kd": 2.2067, "alpha_p": 0.6581, "k_p": 0.1049,
        "a_p": 61.4251, "b_p": 0.0738, "k2_p": 0.0338,
        "tau_1": 67.1153, "c_p": -0.6957, "lam": 0.18,
    },
    "DB": {
        "Vmax": 17.7687, "Kd": 1.0, "alpha_p": 0.2205, "k_p": 0.1163,
        "a_p": 8.6559, "b_p": 0.3209, "k2_p": 0.0116,
        "tau_1": 70.5958, "c_p": -1.3702, "lam": 0.005,
    },
}

# ═══════════════════════════════════════════════════════════════
# EXPRESSION ODE v3 (frozen)
# ═══════════════════════════════════════════════════════════════
EXPRESSION_V3 = {
    "beta_m": 8.3178,
    "beta_p": 0.3466,
    "delta_m": 1.0,
    "delta_p": 0.1,
    "sigma": 2.0,
    "P_BASAL_SS": 0.3469,
    "R2": 0.9988,
    "RMSE": 0.1087,
    "direction_accuracy": 1.0,
    "grade_A_count": 23,
    "grade_total": 27,
}

# Per-gene calibrations: (gene, dye, alpha, t_onset, obs_fc, model_fc, grade)
EXPRESSION_CALIBRATIONS = [
    ("AzoR", "MO", 8.65, 0.0, 104.4, 78.3, "A"),
    ("AzoR", "RC", 8.18, 0.0, 80.7, 76.7, "A"),
    ("AzoR", "DB", 6.62, 0.0, 371.1, 360.2, "A"),
    ("CymA", "MO", -0.02, 0.0, 0.31, 0.96, "B"),
    ("CymA", "RC", 3.42, 0.0, 6.64, 10.3, "A"),
    ("CymA", "DB", 2.77, 0.0, 5.47, 6.19, "A"),
    ("YhhW", "MO", 0.02, 0.0, 1.19, 1.05, "A"),
    ("YhhW", "RC", 2.79, 0.0, 4.66, 6.26, "A"),
    ("YhhW", "DB", 1.91, 0.0, 3.55, 3.50, "A"),
    ("fhuE_1", "MO", 0.21, 0.0, 1.33, 1.51, "A"),
    ("fhuE_1", "RC", -2.56, 0.0, 0.08, 0.11, "A"),
    ("fhuE_1", "DB", -0.59, 0.0, 0.57, 0.62, "A"),
    ("fhuF", "MO", -0.78, 0.0, 0.46, 0.55, "A"),
    ("fhuF", "RC", -2.18, 0.0, 0.14, 0.15, "A"),
    ("fhuF", "DB", -0.72, 0.0, 0.50, 0.58, "A"),
    ("iucA_iucC", "MO", 0.60, 0.0, 1.82, 2.01, "A"),
    ("iucA_iucC", "RC", -3.35, 0.0, 0.05, 0.06, "A"),
    ("iucA_iucC", "DB", 0.06, 0.0, 1.06, 1.13, "A"),
    ("iucD", "MO", -0.86, 0.0, 0.42, 0.51, "A"),
    ("iucD", "RC", -2.56, 0.0, 0.08, 0.11, "B"),
    ("iucD", "DB", -0.14, 0.0, 0.88, 0.77, "A"),
    ("gyrA", "MO", -0.02, 0.0, 0.96, 0.96, "A"),
    ("gyrA", "RC", 0.87, 0.0, 2.52, 2.86, "A"),
    ("gyrA", "DB", -0.07, 0.0, 0.93, 0.87, "A"),
    ("rho", "MO", 0.18, 0.0, 1.35, 1.44, "A"),
    ("rho", "RC", 1.36, 0.0, 3.96, 4.33, "B"),
    ("rho", "DB", -0.07, 0.0, 0.93, 0.87, "B"),
]

# ═══════════════════════════════════════════════════════════════
# RT-qPCR REFERENCE Ct VALUES (ZZ = control, triplicates)
# ═══════════════════════════════════════════════════════════════
RTQPCR_RAW = {
    "AzoR": {
        "ZZ": [30.793, 30.946, 31.070],
        "MO": [23.383, 23.331, 23.684],
        "CR": [23.573, 23.675, 23.634],
        "AD": [21.939, 21.598, 21.555],
    },
    "CymA": {
        "ZZ": [29.937, 32.733, 32.759],
        "MO": [32.083, 32.443, 32.483],
        "CR": [29.466, 28.463, 28.949],
        "AD": [29.120, 29.313, 29.245],
    },
    "YhhW": {
        "ZZ": [31.322, 31.987, 31.630],
        "MO": [31.729, 31.530, 32.022],
        "CR": [29.938, 29.916, 29.755],
        "AD": [29.961, 29.903, 29.926],
    },
    "fhuE_1": {
        "ZZ": [30.963], "MO": [30.559], "RC": [34.573], "AD": [31.780],
    },
    "fhuF": {
        "ZZ": [31.119], "MO": [32.247], "RC": [34.196], "AD": [32.130],
    },
    "iucA_iucC": {
        "ZZ": [30.814], "MO": [29.946], "RC": [35.060], "AD": [30.729],
    },
    "iucD": {
        "ZZ": [28.397], "MO": [29.627], "RC": [32.130], "AD": [28.732],
    },
    "gyrA": {
        "ZZ": [26.854, 26.942, 27.178, 25.422, 25.255, 25.674, 25.431],
        "MO": [27.051, 27.077, 27.067, 25.558, 25.280, 25.641, 25.432],
        "CR": [25.886, 25.593, 25.603],
        "RC": [26.259, 26.403, 26.597, 26.077],
        "AD": [27.155, 27.269, 27.303, 25.605, 25.426, 25.698, 25.477],
    },
    "rho": {
        "ZZ": [26.302, 26.152, 26.079, 24.230, 24.564, 24.633, 24.585],
        "MO": [25.935, 25.863, 25.941, 23.628, 24.121, 23.363, 24.112],
        "CR": [24.454, 24.253, 24.817],
        "RC": [24.187, 25.059, 24.802, 24.673],
        "AD": [26.402, 26.250, 26.478, 24.335, 24.790, 24.749, 24.447],
    },
}

REFERENCE_GENES = ["gyrA", "rho"]

# ═══════════════════════════════════════════════════════════════
# METABOLIC ROUTE CATALOG
# ═══════════════════════════════════════════════════════════════

MO_ROUTES = {
    "MO_DMPD_to_TCA": {
        "probability": 0.52,
        "convergence": "Succinyl-CoA + Acetyl-CoA \u2192 TCA",
        "steps": [
            {"id": "MO_D01", "rxn": "MO_transport", "type": "transport",
             "substrates": ["MO_ext"], "products": ["MO_c"], "confidence": "exact"},
            {"id": "MO_D02", "rxn": "azo_reduction", "type": "reductase",
             "substrates": ["MO_c", "NADH"], "products": ["DMPD", "sulfanilate", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "MO_D03", "rxn": "DMPD_to_pphenylenediamine", "type": "oxidase",
             "substrates": ["DMPD", "O2", "NADH"], "products": ["pPhenylenediamine", "NAD", "H2O"],
             "enzyme": "PhhA", "gene": "phhA", "ec": "1.14.16.1", "confidence": "plausible"},
            {"id": "MO_D04", "rxn": "pphenylenediamine_to_catechol", "type": "oxidase",
             "substrates": ["pPhenylenediamine", "O2", "NADH"], "products": ["catechol", "NH3", "NAD"],
             "enzyme": "PhhA", "gene": "phhA", "ec": "1.14.13.x", "confidence": "plausible"},
            {"id": "MO_D05", "rxn": "catechol_ring_cleavage", "type": "dioxygenase",
             "substrates": ["catechol", "O2"], "products": ["beta_ketoadipate"],
             "enzyme": "CatA", "gene": "catA", "ec": "1.13.11.1", "confidence": "exact"},
            {"id": "MO_D06", "rxn": "beta_ketoadipate_to_succinylCoA", "type": "transferase",
             "substrates": ["beta_ketoadipate", "succinylCoA"],
             "products": ["beta_ketoadipyl_CoA", "succinate"],
             "enzyme": "PcaIJ", "gene": "pcaI/pcaJ", "ec": "2.8.3.6", "confidence": "exact"},
            {"id": "MO_D07", "rxn": "thiolase_to_TCA", "type": "thiolase",
             "substrates": ["beta_ketoadipyl_CoA", "CoA"], "products": ["succinylCoA", "acetylCoA"],
             "enzyme": "PcaF", "gene": "pcaF", "ec": "2.3.1.174", "confidence": "exact"},
        ],
    },
    "MO_sulfanilate_to_TCA": {
        "probability": 0.48,
        "convergence": "Succinyl-CoA + Acetyl-CoA \u2192 TCA",
        "steps": [
            {"id": "MO_S01", "rxn": "MO_transport", "type": "transport",
             "substrates": ["MO_ext"], "products": ["MO_c"], "confidence": "exact"},
            {"id": "MO_S02", "rxn": "azo_reduction", "type": "reductase",
             "substrates": ["MO_c", "NADH"], "products": ["DMPD", "sulfanilate", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "MO_S03", "rxn": "sulfanilate_desulfonation", "type": "desulfonase",
             "substrates": ["sulfanilate", "O2", "NADH"],
             "products": ["catechol", "SO3", "NH3", "NAD"],
             "enzyme": "SadABC", "gene": "sadA", "ec": "1.14.12.x", "confidence": "plausible"},
            {"id": "MO_S04", "rxn": "catechol_ring_cleavage", "type": "dioxygenase",
             "substrates": ["catechol", "O2"], "products": ["beta_ketoadipate"],
             "enzyme": "CatA", "gene": "catA", "ec": "1.13.11.1", "confidence": "exact"},
            {"id": "MO_S05", "rxn": "beta_ketoadipate_to_succinylCoA", "type": "transferase",
             "substrates": ["beta_ketoadipate", "succinylCoA"],
             "products": ["beta_ketoadipyl_CoA", "succinate"],
             "enzyme": "PcaIJ", "gene": "pcaI/pcaJ", "ec": "2.8.3.6", "confidence": "exact"},
            {"id": "MO_S06", "rxn": "thiolase_to_TCA", "type": "thiolase",
             "substrates": ["beta_ketoadipyl_CoA", "CoA"], "products": ["succinylCoA", "acetylCoA"],
             "enzyme": "PcaF", "gene": "pcaF", "ec": "2.3.1.174", "confidence": "exact"},
        ],
    },
}

RC_ROUTES = {
    "RC_catechol_route": {
        "probability": 0.839,
        "convergence": "Succinyl-CoA + Acetyl-CoA \u2192 TCA",
        "steps": [
            {"id": "RC_C01", "rxn": "RC_transport", "type": "transport",
             "substrates": ["RC_ext"], "products": ["RC_c"], "confidence": "exact"},
            {"id": "RC_C02", "rxn": "azo_reduction_1", "type": "reductase",
             "substrates": ["RC_c", "NADH"], "products": ["RC_half", "amine_1", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "RC_C03", "rxn": "azo_reduction_2", "type": "reductase",
             "substrates": ["RC_half", "NADH"], "products": ["amine_2", "amine_3", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "RC_C04", "rxn": "amine_to_catechol", "type": "oxidase",
             "substrates": ["amine_2", "O2", "NADH"], "products": ["catechol", "NH3", "NAD"],
             "enzyme": "PhhA", "gene": "phhA", "ec": "1.14.16.1", "confidence": "plausible"},
            {"id": "RC_C05", "rxn": "catechol_ring_cleavage", "type": "dioxygenase",
             "substrates": ["catechol", "O2"], "products": ["beta_ketoadipate"],
             "enzyme": "CatA", "gene": "catA", "ec": "1.13.11.1", "confidence": "exact"},
            {"id": "RC_C06", "rxn": "beta_ketoadipate_to_TCA", "type": "transferase",
             "substrates": ["beta_ketoadipate"], "products": ["succinylCoA", "acetylCoA"],
             "enzyme": "PcaIJ/PcaF", "gene": "pcaI/pcaJ/pcaF", "confidence": "exact"},
        ],
    },
}

DB_ROUTES = {
    "DB_protocatechuate_route": {
        "probability": 0.73,
        "convergence": "Succinyl-CoA + Acetyl-CoA \u2192 TCA",
        "steps": [
            {"id": "DB_P01", "rxn": "DB_transport", "type": "transport",
             "substrates": ["DB_ext"], "products": ["DB_c"], "confidence": "exact"},
            {"id": "DB_P02", "rxn": "azo_reduction_1", "type": "reductase",
             "substrates": ["DB_c", "NADH"], "products": ["DB_2azo", "amine_frag1", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "DB_P03", "rxn": "azo_reduction_2", "type": "reductase",
             "substrates": ["DB_2azo", "NADH"], "products": ["DB_1azo", "amine_frag2", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "DB_P04", "rxn": "azo_reduction_3", "type": "reductase",
             "substrates": ["DB_1azo", "NADH"], "products": ["amine_frag3", "amine_frag4", "NAD"],
             "enzyme": "AzoR", "gene": "azoR", "ec": "1.7.1.6", "confidence": "exact"},
            {"id": "DB_P05", "rxn": "amine_to_protocatechuate", "type": "oxidase",
             "substrates": ["amine_frag3", "O2"], "products": ["protocatechuate"],
             "enzyme": "PcaGH", "gene": "pcaG/pcaH", "ec": "1.13.11.3",
             "confidence": "plausible"},
            {"id": "DB_P06", "rxn": "protocatechuate_cleavage", "type": "dioxygenase",
             "substrates": ["protocatechuate", "O2"], "products": ["beta_ketoadipate"],
             "enzyme": "PcaGH", "gene": "pcaG/pcaH", "ec": "1.13.11.3", "confidence": "exact"},
            {"id": "DB_P07", "rxn": "beta_ketoadipate_to_TCA", "type": "transferase",
             "substrates": ["beta_ketoadipate"], "products": ["succinylCoA", "acetylCoA"],
             "enzyme": "PcaIJ/PcaF", "gene": "pcaI/pcaJ/pcaF", "confidence": "exact"},
        ],
    },
}

ALL_ROUTES = {**MO_ROUTES, **RC_ROUTES, **DB_ROUTES}

# ═══════════════════════════════════════════════════════════════
# NADH CONSUMPTION PER DYE (redox budget)
# ═══════════════════════════════════════════════════════════════
NADH_PER_DYE = {"MO": 1, "RC": 2, "DB": 3}

# ═══════════════════════════════════════════════════════════════
# NMR reference data
# ═══════════════════════════════════════════════════════════════
NMR_MO = [
    (0, 100.0), (2, 85.0), (4, 60.0), (6, 30.0),
    (8, 10.0), (10, 5.0), (12, 2.0),
]
NMR_SA = [
    (0, 0.0), (2, 5.0), (4, 15.0), (6, 35.0),
    (8, 55.0), (10, 70.0), (12, 80.0),
]

# ═══════════════════════════════════════════════════════════════
# CORE MODEL REVALIDATION RESULTS (v1.1.0, frozen)
# ═══════════════════════════════════════════════════════════════
# Core bridge canonical:
#   y(t) = y_max * (1 - exp(-H(t)^β))
#   H(t) = ∫ λ · dΦ/dt dt
#   3 free parameters: λ, β, y_max
#   Ψ(t) and B^α removed from canonical formula
#
# Full (legacy) bridge:
#   H(t) = ∫ λ · dΦ/dt · Ψ · B^α dt
#   Includes Ψ(t) = 1 - exp(-k_p·t) and B^α

CORE_REVALIDATION = {
    "verdict": "CORE_MODEL_SUFFICIENT",
    "shewanella": {
        "core3_R2": 0.9839,
        "full_R2": 0.9916,
        "loss": 0.0077,
        "n_conditions": 25,
    },
    "ecoli": {
        "core_R2": 0.9815,
        "full_R2": 0.9959,
        "loss": 0.0144,
        "n_datasets": 7,
    },
    "acidithiobacillus": {
        "core_R2": 0.9921,
        "full_R2": 0.9942,
        "loss": 0.0021,
        "n_datasets": 1,
    },
}

# λ_b structural law: log10(λ_b) = 0.918 - 1.013 × N_NADH
LAMBDA_B_LAW = {
    "intercept": 0.9181,
    "slope": -1.0127,
    "R2": 0.999,
    "formula": "log10(lambda_b) = 0.918 - 1.013 * N_NADH",
    "interpretation": "redox cost per observable (NADH equivalents)",
}
