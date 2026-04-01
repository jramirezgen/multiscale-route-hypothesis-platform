"""Unit tests for scoring."""


def test_score_hypothesis():
    """Test scoring with mock inputs."""
    from mrhp.scoring.scorer import score_hypothesis

    route = {"n_steps": 5, "overall_confidence": 0.8}
    sim_analysis = {"connectivity_score": 0.9, "robustness_score": 0.85}
    bridge_eval = {"R2_bridge_vs_v4": 0.95}
    validation = {"direction_accuracy": 0.8, "classification": "GOOD",
                  "mean_magnitude_error_log2": 0.5}
    omics = {"has_nmr": True, "has_redox": True, "nmr_score": 0.9,
             "redox_score": 0.8}

    score = score_hypothesis(route, sim_analysis, bridge_eval,
                             validation, omics)
    assert "sync_score" in score
    assert "classification" in score
    assert "scores" in score
    assert 0 <= score["sync_score"] <= 1.0


def test_rank_hypotheses():
    """Test ranking of multiple scores."""
    from mrhp.scoring.scorer import rank_hypotheses

    scores = [
        {"sync_score": 0.8, "classification": "A", "route_id": "r1"},
        {"sync_score": 0.6, "classification": "B", "route_id": "r2"},
        {"sync_score": 0.9, "classification": "C", "route_id": "r3"},
    ]
    ranked = rank_hypotheses(scores)
    assert ranked[0]["rank"] == 1
    assert ranked[0]["route_id"] == "r3"
    assert ranked[-1]["route_id"] == "r2"
