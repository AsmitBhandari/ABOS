from typing import Dict, List, Optional
from core.agent import AgentState, BaseAgent
from core.agent_profile import AgentProfile
from core.task import Task
from orchestration.scheduler.base import BaseScheduler, CandidateScore, SchedulingResult
from orchestration.scheduler.scoring import ScoringPolicy


class DeterministicScheduler(BaseScheduler):
    """
    Deterministic performance-aware scheduler for agent selection.

    Selection Pipeline:
      1. Filter by Task required capabilities (agent.capabilities must be a superset).
      2. Filter by Agent operational state (only AgentState.IDLE is eligible).
      3. Look up AgentProfile (or apply neutral baseline assumptions if missing).
      4. Calculate normalized performance scores based on ScoringPolicy.
      5. Rank eligible candidates using a deterministic multi-tier tie-breaking policy.
      6. Return a structured SchedulingResult without mutating domain objects.
    """

    def __init__(self, scoring_policy: Optional[ScoringPolicy] = None):
        self.scoring_policy = scoring_policy or ScoringPolicy()

    def schedule(
        self,
        task: Task,
        agents: List[BaseAgent],
        profiles: Optional[List[AgentProfile]] = None,
    ) -> SchedulingResult:
        """
        Evaluate candidate agents against task requirements and historical profiles,
        returning a structured SchedulingResult.
        """
        if not agents:
            return SchedulingResult(
                task_id=task.id,
                selected_agent_id=None,
                success=False,
                reason="No candidate agents provided for scheduling.",
                score=0.0,
                candidates=[],
                metadata={"total_evaluated": 0, "eligible_count": 0},
            )

        profile_map: Dict[str, AgentProfile] = {
            p.agent_id: p for p in (profiles or [])
        }

        task_reqs = set(task.required_capabilities or [])
        candidate_scores: Dict[str, CandidateScore] = {}
        eligible_agents: List[BaseAgent] = []

        # 1. Capability & State Filtering
        for agent in agents:
            agent_caps = set(agent.capabilities or [])
            if not task_reqs.issubset(agent_caps):
                missing = sorted(list(task_reqs - agent_caps))
                candidate_scores[agent.id] = CandidateScore(
                    agent_id=agent.id,
                    eligible=False,
                    rejection_reason=f"Missing required capabilities: {missing}",
                )
                continue

            if agent.state != AgentState.IDLE:
                candidate_scores[agent.id] = CandidateScore(
                    agent_id=agent.id,
                    eligible=False,
                    rejection_reason=f"Agent is in '{agent.state.value}' state (only IDLE is eligible)",
                )
                continue

            eligible_agents.append(agent)

        if not eligible_agents:
            all_scores = list(candidate_scores.values())
            has_compatible = any(
                task_reqs.issubset(set(a.capabilities or [])) for a in agents
            )
            if not has_compatible:
                reason = "No candidate agents possess the required capabilities."
            else:
                reason = "Compatible candidate agents exist, but none are in IDLE state."

            return SchedulingResult(
                task_id=task.id,
                selected_agent_id=None,
                success=False,
                reason=reason,
                score=0.0,
                candidates=all_scores,
                metadata={"total_evaluated": len(agents), "eligible_count": 0},
            )

        # 2. Collect latency data for eligible agents and normalize
        raw_latencies: Dict[str, Optional[float]] = {}
        for agent in eligible_agents:
            if agent.id in profile_map:
                raw_latencies[agent.id] = profile_map[agent.id].avg_latency_ms
            else:
                raw_latencies[agent.id] = None

        latency_scores = self.scoring_policy.normalize_latencies(raw_latencies)

        # 3. Calculate Performance Scores for eligible agents
        scored_candidates: List[CandidateScore] = []
        for agent in eligible_agents:
            if agent.id in profile_map:
                prof = profile_map[agent.id]
                success_rate = prof.success_rate
                confidence = prof.confidence_score
                raw_lat = prof.avg_latency_ms
                lat_score = latency_scores[agent.id]
            else:
                # Neutral default performance assumptions for agents without profile
                success_rate = 0.5
                confidence = 0.5
                raw_lat = 0.0
                lat_score = latency_scores[agent.id]

            total_score = self.scoring_policy.calculate_score(
                success_rate=success_rate,
                latency_score=lat_score,
                confidence_score=confidence,
            )

            cand_score = CandidateScore(
                agent_id=agent.id,
                total_score=total_score,
                success_rate=success_rate,
                latency_score=lat_score,
                confidence_score=confidence,
                raw_latency_ms=raw_lat,
                eligible=True,
                rejection_reason=None,
            )
            candidate_scores[agent.id] = cand_score
            scored_candidates.append(cand_score)

        # 4. Deterministic Multi-Tier Ranking & Tie-breaking:
        #    1. Total score (descending)
        #    2. Success rate (descending)
        #    3. Confidence score (descending)
        #    4. Raw latency ms (ascending)
        #    5. Agent ID (ascending lexicographical)
        scored_candidates.sort(
            key=lambda c: (
                -c.total_score,
                -c.success_rate,
                -c.confidence_score,
                c.raw_latency_ms,
                c.agent_id,
            )
        )

        best_candidate = scored_candidates[0]
        all_candidates_ordered = [
            candidate_scores[agent.id] for agent in agents
        ]

        return SchedulingResult(
            task_id=task.id,
            selected_agent_id=best_candidate.agent_id,
            success=True,
            reason=f"Selected agent '{best_candidate.agent_id}' with highest performance score ({round(best_candidate.total_score, 4)}).",
            score=round(best_candidate.total_score, 4),
            candidates=all_candidates_ordered,
            metadata={
                "total_evaluated": len(agents),
                "eligible_count": len(eligible_agents),
                "policy": {
                    "success_rate_weight": self.scoring_policy.success_rate_weight,
                    "latency_weight": self.scoring_policy.latency_weight,
                    "confidence_weight": self.scoring_policy.confidence_weight,
                },
            },
        )
