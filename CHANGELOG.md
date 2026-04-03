# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-03

### Added
- Core bridge mode (canonical): `y = y_max * (1 - exp(-H^β))`, `H = ∫ λ · dΦ/dt dt`
- Bridge mode selection: "core" (default, canonical) or "full" (legacy v5)
- `beta` parameter passthrough in `compute_bridge()`
- `CORE_REVALIDATION` frozen results in `frozen.py`
- `LAMBDA_B_LAW` structural law: `log₁₀(λ_b) = 0.918 − 1.013 × N_NADH`
- Unit tests for core bridge mode
- Reproducibility test comparing core vs full bridge output

### Changed
- Default bridge mode is now "core" (was implicit "full")
- `compute_bridge()` accepts `mode` and `beta` keyword arguments
- Pipeline reads `bridge.mode` from YAML config
- Version bumped to 1.1.0

### Backward Compatibility
- Full bridge mode preserved as `mode="full"` — identical to v1.0.0 behavior
- All existing configs work without changes (core mode is backward-compatible)
- Existing test suite passes without modification

## [1.0.0] - 2026-03-30

### Added
- Full 10-phase pipeline orchestrator
- V4 Hill phenotype model (frozen)
- Bridge V5 dual canonical (frozen)
- Expression V3 ODE with 27 calibrated genes (frozen)
- Route catalogs: MO (2), RC (1), DB (1)
- CLI with 6 commands: run, compare, explain, doctor, validate
- Python API: `run_pipeline()`, `load_config()`
- AI-assisted hooks: `hook_run()`, `hook_compare()`, `hook_doctor()`
- 5 publication-grade figure types
- Cross-system validation: Shewanella, E. coli, Acidithiobacillus
- 6 example configs (3 organisms, 4 dye routes)
- Full documentation: architecture, configuration, CLI reference
- Unit and integration tests
