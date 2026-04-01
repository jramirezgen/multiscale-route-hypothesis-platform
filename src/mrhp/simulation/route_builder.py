"""Route construction from hypothesis YAML or canonical catalog."""

import numpy as np

from mrhp.models.frozen import ALL_ROUTES


def build_route(cfg):
    """Build a complete route from the YAML hypothesis."""
    hyp = cfg["route_hypothesis"]
    route_id = hyp.get("route_id", "custom_route")

    if route_id in ALL_ROUTES:
        route = _build_from_catalog(ALL_ROUTES[route_id], hyp)
    else:
        route = _build_from_yaml(hyp, route_id)

    route["route_id"] = route_id
    route["source"] = "catalog" if route_id in ALL_ROUTES else "yaml_custom"
    route["dye_code"] = hyp.get("dye_code", "")
    route["substrate_name"] = cfg.get("target", "unknown")
    route["all_metabolites"] = _collect_metabolites(route["steps"])
    route["all_enzymes"] = _collect_enzymes(route["steps"])
    route["all_genes"] = _collect_genes(route["steps"])
    route["n_steps"] = len(route["steps"])
    route["confidence_summary"] = _confidence_summary(route["steps"])
    route["overall_confidence"] = _overall_confidence(route["steps"])

    return route


def _build_from_catalog(catalog_route, hyp):
    """Use canonical route from catalog, overlay any YAML customizations."""
    route = {
        "steps": catalog_route["steps"],
        "probability": catalog_route.get("probability", 1.0),
        "convergence": catalog_route.get("convergence", "unknown"),
    }
    if "branches" in hyp:
        for br in hyp["branches"]:
            route.setdefault("branches", []).append(br)
    return route


def _build_from_yaml(hyp, route_id):
    """Build route entirely from YAML definition."""
    if "steps" in hyp and isinstance(hyp["steps"], list):
        steps = []
        for s in hyp["steps"]:
            step = dict(s)
            step.setdefault("substrates", [])
            step.setdefault("products", [])
            step.setdefault("confidence", "yaml_defined")
            steps.append(step)
        return {
            "steps": steps,
            "probability": hyp.get("probability", 1.0),
            "convergence": hyp.get("convergence", "unknown"),
        }

    steps = []
    step_idx = 0

    for rxn_name in hyp.get("entry_reactions", []):
        step_idx += 1
        steps.append({
            "id": f"{route_id}_{step_idx:02d}",
            "rxn": rxn_name,
            "type": "entry",
            "substrates": [], "products": [],
            "confidence": "yaml_defined",
        })

    for br in hyp.get("branches", []):
        for rxn_name in br.get("reactions", []):
            step_idx += 1
            steps.append({
                "id": f"{route_id}_{step_idx:02d}",
                "rxn": rxn_name,
                "type": "branch:" + br.get("name", "unnamed"),
                "substrates": [], "products": [],
                "confidence": "yaml_defined",
            })

    return {
        "steps": steps,
        "probability": hyp.get("probability", 1.0),
        "convergence": hyp.get("convergence", "unknown"),
    }


def _collect_metabolites(steps):
    mets = set()
    for s in steps:
        mets.update(s.get("substrates", []))
        mets.update(s.get("products", []))
    return sorted(mets)


def _collect_enzymes(steps):
    return sorted({s["enzyme"] for s in steps if "enzyme" in s})


def _collect_genes(steps):
    genes = set()
    for s in steps:
        g = s.get("gene", "")
        if g:
            for part in g.replace("/", ",").split(","):
                genes.add(part.strip())
    return sorted(genes)


def _confidence_summary(steps):
    counts = {}
    for s in steps:
        c = s.get("confidence", "unknown")
        counts[c] = counts.get(c, 0) + 1
    return counts


def _overall_confidence(steps):
    """Geometric mean of numeric confidence scores."""
    conf_map = {"exact": 1.0, "plausible": 0.7, "yaml_defined": 0.5, "unknown": 0.3}
    if not steps:
        return 0.0
    scores = [conf_map.get(s.get("confidence", "unknown"), 0.5) for s in steps]
    return float(np.prod(scores) ** (1.0 / len(scores)))


def route_story(route):
    """Generate a narrative markdown string of the route."""
    lines = [
        f"## Route: {route['route_id']}",
        f"**Probability:** {route.get('probability', '?')}",
        f"**Convergence:** {route.get('convergence', '?')}",
        f"**Source:** {route.get('source', '?')}",
        "",
        "### Step-by-Step",
        "",
        "| # | ID | Reaction | Type | Enzyme | Gene | Confidence |",
        "|---|-----|----------|------|--------|------|------------|",
    ]
    for i, s in enumerate(route["steps"], 1):
        rxn_name = s.get("rxn", s.get("substrate", "-") + " \u2192 " + s.get("product", "-"))
        lines.append(
            f"| {i} | {s.get('id','-')} | {rxn_name} | {s.get('type','')} "
            f"| {s.get('enzyme','-')} | {s.get('gene','-')} | {s.get('confidence','?')} |"
        )

    lines += ["", "### Metabolites", ""]
    for m in route.get("all_metabolites", []):
        lines.append(f"- {m}")

    lines += ["", "### Confidence Summary", ""]
    for k, v in route.get("confidence_summary", {}).items():
        lines.append(f"- **{k}**: {v} steps")

    return "\n".join(lines)
