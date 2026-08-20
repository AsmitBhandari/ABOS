import re
from typing import Any, Dict, Optional, Tuple, Union
from core.agent import AgentState, BaseAgent
from core.result import Result
from core.task import Task


class UnitConversionAgent(BaseAgent):
    """
    Agent capable of performing deterministic unit conversions for length measurements.
    Supported conversions:
      - kilometers <-> meters (km <-> m)
      - meters <-> centimeters (m <-> cm)
    """

    # Canonical conversion factors to base unit (meters)
    UNIT_TO_METERS = {
        "km": 1000.0,
        "kilometer": 1000.0,
        "kilometers": 1000.0,
        "m": 1.0,
        "meter": 1.0,
        "meters": 1.0,
        "cm": 0.01,
        "centimeter": 0.01,
        "centimeters": 0.01,
    }

    # Supported conversion pairs (from_unit_canonical, to_unit_canonical)
    SUPPORTED_PAIRS = {
        ("km", "m"),
        ("m", "km"),
        ("m", "cm"),
        ("cm", "m"),
    }

    def __init__(self, agent_id: str = "agent-unit-conversion-01", name: str = "UnitConversionAgent"):
        super().__init__(
            name=name,
            capabilities=["unit_conversion"],
            agent_id=agent_id,
        )

    @classmethod
    def _normalize_unit(cls, unit_str: str) -> Optional[str]:
        cleaned = unit_str.strip().lower()
        if cleaned in ("km", "kilometer", "kilometers"):
            return "km"
        if cleaned in ("m", "meter", "meters"):
            return "m"
        if cleaned in ("cm", "centimeter", "centimeters"):
            return "cm"
        return None

    def _parse_input(self, raw_input: Any, task_desc: Optional[str]) -> Tuple[Optional[float], Optional[str], Optional[str], Optional[str]]:
        """
        Parse input into (value, from_unit, to_unit, error_message).
        """
        # Case 1: Dict input
        if isinstance(raw_input, dict):
            val_raw = raw_input.get("value") or raw_input.get("amount")
            from_u = raw_input.get("from_unit") or raw_input.get("from")
            to_u = raw_input.get("to_unit") or raw_input.get("to")

            if val_raw is None:
                return None, None, None, "Malformed input: missing 'value' or 'amount' in dict input."
            if not from_u or not to_u:
                return None, None, None, "Malformed input: missing 'from_unit' or 'to_unit' in dict input."

            try:
                numeric_val = float(val_raw)
            except (ValueError, TypeError):
                return None, None, None, f"Invalid numeric value: '{val_raw}'."

            return numeric_val, str(from_u), str(to_u), None

        # Case 2: String input (either from input_data or task_desc)
        target_str = ""
        if isinstance(raw_input, str) and raw_input.strip():
            target_str = raw_input.strip()
        elif task_desc and task_desc.strip():
            target_str = task_desc.strip()
        else:
            return None, None, None, "Malformed input: empty or missing conversion request."

        # Regex patterns for string conversion requests:
        # e.g., "5 km to m", "5000 m -> km", "convert 2 m to cm", "300 cm to meters"
        pattern = re.compile(
            r"(?:convert\s+)?([+-]?(?:\d+\.?\d*|\.\d+))\s*([a-zA-Z]+)\s*(?:to|->|in)\s*([a-zA-Z]+)",
            re.IGNORECASE,
        )
        match = pattern.search(target_str)
        if match:
            val_str, from_u, to_u = match.groups()
            try:
                numeric_val = float(val_str)
                return numeric_val, from_u, to_u, None
            except ValueError:
                return None, None, None, f"Invalid numeric value: '{val_str}'."

        return None, None, None, f"Malformed input: unable to parse conversion expression from '{target_str}'."

    def execute(self, task: Task) -> Result:
        """
        Execute unit conversion on the provided task input.
        """
        value, from_u_raw, to_u_raw, error_msg = self._parse_input(task.input_data, task.description)

        if error_msg:
            return Result(
                success=False,
                output=None,
                error=error_msg,
                agent_id=self.id,
            )

        assert value is not None and from_u_raw is not None and to_u_raw is not None

        norm_from = self._normalize_unit(from_u_raw)
        norm_to = self._normalize_unit(to_u_raw)

        if not norm_from or not norm_to:
            return Result(
                success=False,
                output=None,
                error=f"Unsupported unit(s): '{from_u_raw}' to '{to_u_raw}'. Supported units are km, m, cm.",
                agent_id=self.id,
            )

        if (norm_from, norm_to) not in self.SUPPORTED_PAIRS and norm_from != norm_to:
            return Result(
                success=False,
                output=None,
                error=f"Unsupported conversion pair: '{norm_from}' to '{norm_to}'.",
                agent_id=self.id,
            )

        # Convert to base (meters) then to target unit
        meters = value * self.UNIT_TO_METERS[norm_from]
        converted = meters / self.UNIT_TO_METERS[norm_to]

        # Format integer output cleanly if whole number
        if converted.is_integer():
            final_output: Union[int, float] = int(converted)
        else:
            final_output = round(converted, 6)

        return Result(
            success=True,
            output=final_output,
            agent_id=self.id,
            metadata={
                "from_value": value,
                "from_unit": norm_from,
                "to_unit": norm_to,
                "converted_value": final_output,
            },
        )
