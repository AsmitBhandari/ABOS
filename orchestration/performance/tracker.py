from typing import Any, Dict, Optional, Set
from core.agent_profile import AgentProfile
from core.evaluation import Evaluation


class PerformanceTracker:
    """
    Orchestration component responsible for recording task execution evaluations
    and deterministically updating quantitative historical AgentProfile metrics.

    Key responsibilities:
      - Validates agent identity matching between Evaluation and AgentProfile.
      - Enforces evaluation idempotency using evaluation.id in memory.
      - Updates cumulative execution counts and success rate.
      - Updates cumulative average latency using incremental calculation.
      - Updates evidence-based confidence score based on configurable saturation.
      - Aggregates execution quality and correctness scores inside profile.metadata.
      - Updates last execution timestamp from evaluation metadata.
      - Returns the updated AgentProfile without relying on external persistence.
    """

    def __init__(self, confidence_saturation: int = 20):
        if confidence_saturation <= 0:
            raise ValueError("confidence_saturation must be a positive integer.")
        self.confidence_saturation: int = confidence_saturation
        self._processed_evaluation_ids: Set[str] = set()

    def is_processed(self, evaluation_id: str) -> bool:
        """Check if an evaluation ID has already been recorded."""
        return evaluation_id in self._processed_evaluation_ids

    def processed_count(self) -> int:
        """Return the number of unique evaluation IDs processed."""
        return len(self._processed_evaluation_ids)

    def reset(self) -> None:
        """Clear in-memory processed evaluation history."""
        self._processed_evaluation_ids.clear()

    def update(self, evaluation: Evaluation, profile: AgentProfile) -> AgentProfile:
        """
        Update an AgentProfile using an Evaluation record.

        Args:
            evaluation: The single execution assessment from ABOS.
            profile: The AgentProfile to update.

        Returns:
            The updated AgentProfile instance.

        Raises:
            ValueError: If agent IDs do not match or if inputs fail validation.
        """
        if not isinstance(evaluation, Evaluation):
            raise TypeError("evaluation must be an instance of Evaluation.")
        if not isinstance(profile, AgentProfile):
            raise TypeError("profile must be an instance of AgentProfile.")

        # 1. Agent ID Consistency Check
        if evaluation.agent_id != profile.agent_id:
            raise ValueError(
                f"Agent ID mismatch: Evaluation agent_id '{evaluation.agent_id}' "
                f"does not match AgentProfile agent_id '{profile.agent_id}'."
            )

        # 2. Idempotency Check
        if evaluation.id in self._processed_evaluation_ids:
            return profile

        # 3. Defensive Validation
        if evaluation.latency_ms < 0.0:
            raise ValueError("Evaluation latency_ms cannot be negative.")
        if evaluation.quality_score is not None and not (0.0 <= evaluation.quality_score <= 1.0):
            raise ValueError("Evaluation quality_score must be between 0.0 and 1.0.")
        if evaluation.correctness_score is not None and not (0.0 <= evaluation.correctness_score <= 1.0):
            raise ValueError("Evaluation correctness_score must be between 0.0 and 1.0.")

        # 4. Cumulative Execution Counts & Success Rate
        old_total = profile.total_executions
        old_successful = profile.successful_executions

        new_total = old_total + 1
        new_successful = old_successful + (1 if evaluation.success else 0)
        new_success_rate = new_successful / new_total if new_total > 0 else 0.0

        # 5. Incremental Cumulative Average Latency
        # Formula: new_avg = ((old_avg * old_count) + new_latency) / new_count
        eval_latency = float(evaluation.latency_ms)
        if old_total == 0:
            new_avg_latency = eval_latency
        else:
            new_avg_latency = ((profile.avg_latency_ms * old_total) + eval_latency) / new_total

        # 6. Evidence-Based Confidence Score
        # Formula: confidence = min(1.0, total_executions / confidence_saturation)
        new_confidence = min(1.0, new_total / self.confidence_saturation)

        # 7. Quality and Correctness Aggregation in Metadata
        if "performance" not in profile.metadata or not isinstance(profile.metadata["performance"], dict):
            perf_meta: Dict[str, Any] = {
                "total_quality_score": 0.0,
                "total_correctness_score": 0.0,
                "evaluation_count": 0,
                "quality_eval_count": 0,
                "correctness_eval_count": 0,
                "average_quality": None,
                "average_correctness": None,
            }
            profile.metadata["performance"] = perf_meta
        else:
            perf_meta = profile.metadata["performance"]

        perf_meta["evaluation_count"] = perf_meta.get("evaluation_count", 0) + 1

        if evaluation.quality_score is not None:
            total_qual = perf_meta.get("total_quality_score", 0.0) + float(evaluation.quality_score)
            qual_count = perf_meta.get("quality_eval_count", 0) + 1
            perf_meta["total_quality_score"] = total_qual
            perf_meta["quality_eval_count"] = qual_count
            perf_meta["average_quality"] = total_qual / qual_count

        if evaluation.correctness_score is not None:
            total_corr = perf_meta.get("total_correctness_score", 0.0) + float(evaluation.correctness_score)
            corr_count = perf_meta.get("correctness_eval_count", 0) + 1
            perf_meta["total_correctness_score"] = total_corr
            perf_meta["correctness_eval_count"] = corr_count
            perf_meta["average_correctness"] = total_corr / corr_count

        # 8. Apply Updates to Profile
        profile.total_executions = new_total
        profile.successful_executions = new_successful
        profile.success_rate = new_success_rate
        profile.avg_latency_ms = new_avg_latency
        profile.confidence_score = new_confidence
        if evaluation.created_at:
            profile.last_execution_at = evaluation.created_at

        # 9. Mark Evaluation ID as processed
        self._processed_evaluation_ids.add(evaluation.id)

        return profile
