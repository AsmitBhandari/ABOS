import math
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ScoringPolicy:
    """
    Defines the weighting policy and calculation rules for agent performance scoring.
    Default weighting:
      - success_rate:     0.50
      - latency_score:    0.20
      - confidence_score: 0.30
      Total: 1.00
    """

    success_rate_weight: float = 0.50
    latency_weight: float = 0.20
    confidence_weight: float = 0.30

    def __post_init__(self):
        if (
            self.success_rate_weight < 0.0
            or self.latency_weight < 0.0
            or self.confidence_weight < 0.0
        ):
            raise ValueError("Scoring weights must be non-negative.")

        total_weight = (
            self.success_rate_weight + self.latency_weight + self.confidence_weight
        )
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5, abs_tol=1e-5):
            raise ValueError(
                f"Scoring weights must sum to 1.0 (received sum: {total_weight:.4f})."
            )

    def calculate_score(
        self,
        success_rate: float,
        latency_score: float,
        confidence_score: float,
    ) -> float:
        """
        Calculate total weighted performance score from normalized component scores.
        All input components are expected to be bounded within [0.0, 1.0].
        Returns final score bounded within [0.0, 1.0].
        """
        clamped_success = max(0.0, min(1.0, float(success_rate)))
        clamped_latency = max(0.0, min(1.0, float(latency_score)))
        clamped_confidence = max(0.0, min(1.0, float(confidence_score)))

        raw_score = (
            (clamped_success * self.success_rate_weight)
            + (clamped_latency * self.latency_weight)
            + (clamped_confidence * self.confidence_weight)
        )
        return max(0.0, min(1.0, raw_score))

    @staticmethod
    def normalize_latencies(raw_latencies: Dict[str, Optional[float]]) -> Dict[str, float]:
        """
        Normalize a mapping of {agent_id: avg_latency_ms} to {agent_id: latency_score in [0.0, 1.0]}.
        Lower raw latency yields a higher latency score (1.0 = best/lowest latency).

        Normalization Rules:
        - If an agent has no latency data (None), assign neutral score 0.5.
        - If all candidates with latency data have identical latency, assign 1.0 (no penalty).
        - If latencies differ, apply inverted min-max normalization:
            latency_score = (max_lat - lat) / (max_lat - min_lat)
        """
        scores: Dict[str, float] = {}
        known_latencies = [
            lat for lat in raw_latencies.values() if lat is not None and lat >= 0.0
        ]

        if not known_latencies:
            for agent_id in raw_latencies:
                scores[agent_id] = 0.5
            return scores

        min_lat = min(known_latencies)
        max_lat = max(known_latencies)

        for agent_id, lat in raw_latencies.items():
            if lat is None or lat < 0.0:
                scores[agent_id] = 0.5
            elif math.isclose(min_lat, max_lat):
                scores[agent_id] = 1.0
            else:
                normalized = (max_lat - lat) / (max_lat - min_lat)
                scores[agent_id] = max(0.0, min(1.0, normalized))

        return scores
