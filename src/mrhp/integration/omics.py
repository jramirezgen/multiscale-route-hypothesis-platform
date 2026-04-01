"""Omics integration (NMR, redox, gene coverage)."""

import numpy as np

from mrhp.models.frozen import NMR_MO, NMR_SA, NADH_PER_DYE
from mrhp.io.writers import safe_div


def integrate_omics(cfg, route, sim_result, bridge_result, expr_result, validation):
    """Integrate available omics data to refine hypothesis evaluation."""
    omics_cfg = cfg.get("omics", {})
    dye_code = route.get("dye_code", "")
    evidence = {}

    if omics_cfg.get("nmr", True):
        nmr_data = _get_nmr_evidence(dye_code)
        if nmr_data:
            route_metabolites = set(route.get("all_metabolites", []))
            nmr_confirmed = []
            nmr_absent = []
            for met, info in nmr_data.items():
                met_lower = met.lower().replace("-", "_")
                found = any(met_lower in rm.lower().replace("-", "_")
                            for rm in route_metabolites)
                if found:
                    nmr_confirmed.append({"metabolite": met, "ppm": info.get("ppm"),
                                          "status": "confirmed"})
                else:
                    nmr_absent.append({"metabolite": met, "ppm": info.get("ppm"),
                                       "status": "not_in_route"})
            evidence["nmr"] = {
                "confirmed": nmr_confirmed,
                "absent": nmr_absent,
                "coverage": safe_div(len(nmr_confirmed),
                                     len(nmr_confirmed) + len(nmr_absent)),
            }

    if omics_cfg.get("redox_balance", True):
        nadh = NADH_PER_DYE.get(dye_code, 0)
        route_nadh = sum(1 for s in route.get("steps", [])
                         if "NADH" in s.get("substrates", []))
        route_o2 = sum(1 for s in route.get("steps", [])
                       if "O2" in s.get("substrates", []))
        route_nad_produced = sum(1 for s in route.get("steps", [])
                                 if "NAD" in s.get("products", []))
        evidence["redox"] = {
            "expected_nadh_per_mol": nadh,
            "route_nadh_steps": route_nadh,
            "route_o2_steps": route_o2,
            "route_nad_produced_steps": route_nad_produced,
            "balance_ok": route_nadh >= nadh,
        }

    route_genes = set(route.get("all_genes", []))
    expr_genes = set(expr_result["genes"].keys()) if expr_result else set()
    if route_genes:
        evidence["gene_coverage"] = {
            "route_genes": sorted(route_genes),
            "expression_data_genes": sorted(expr_genes),
            "coverage": safe_div(len(route_genes & expr_genes), len(route_genes)),
        }

    return evidence


def _get_nmr_evidence(dye_code):
    if dye_code == "MO":
        return {"DMPD": {"ppm": None}, "sulfanilate": {"ppm": None},
                "catechol": {"ppm": None}}
    elif dye_code in ("RC", "DB"):
        return {"sulfanilate": {"ppm": None}, "catechol": {"ppm": None}}
    return {}
