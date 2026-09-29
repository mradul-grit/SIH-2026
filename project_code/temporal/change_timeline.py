from typing import List, Dict, Any, Optional
import numpy as np

class ChangeTimelineBuilder:
    """
    Constructs semantic change narrative across temporal steps:
    e.g.,
      2019 -> no change
      2020 -> no change
      2021 -> construction detected
      2022 -> expansion
      2023 -> expansion
    """

    def __init__(self, change_threshold_percent: float = 0.5):
        self.change_thresh = change_threshold_percent

    def build_timeline(self, sequence_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        timeline = []
        cumulative_mask = None

        for step in sequence_results:
            pct = step["change_percentage"]
            curr_mask = step["change_mask"]

            if cumulative_mask is None:
                cumulative_mask = curr_mask.copy()
                if pct < self.change_thresh:
                    status = "no_change"
                else:
                    status = "construction_detected"
            else:
                if pct < self.change_thresh:
                    status = "no_change"
                else:
                    # Check if change overlaps or expands
                    overlap = np.sum((curr_mask > 0) & (cumulative_mask > 0))
                    new_pixels = np.sum((curr_mask > 0) & (cumulative_mask == 0))
                    if new_pixels > overlap:
                        status = "expansion"
                    else:
                        status = "modification"
                    cumulative_mask = cumulative_mask | curr_mask

            timeline.append({
                "interval": f"{step['from_timestamp']} -> {step['to_timestamp']}",
                "from_date": step["from_timestamp"],
                "to_date": step["to_timestamp"],
                "status": status,
                "change_percent": pct,
                "change_pixels": step["change_pixels"]
            })

        return timeline


class EarliestChangeDetector:
    """
    Pinpoints the earliest supported observation of a physical change.
    """

    @staticmethod
    def detect_earliest(timeline: List[Dict[str, Any]], min_significance: float = 0.5) -> Optional[Dict[str, Any]]:
        for event in timeline:
            if event["status"] != "no_change" and event["change_percent"] >= min_significance:
                return {
                    "earliest_timestamp": event["to_date"],
                    "interval": event["interval"],
                    "detected_status": event["status"],
                    "initial_change_magnitude": event["change_percent"]
                }
        return None

    @staticmethod
    def bisection_search(
        observations: List[Dict[str, Any]],
        eval_fn,
        change_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        O(log N) Temporal Bisection Search to pinpoint earliest appearance date.
        
        Instead of linearly scanning every chronological scene in O(N),
        this bisects the interval [left, right] over the chronological observation sequence:
        1. Check baseline T_0 against midpoint T_mid.
        2. If change is detected (change_pct >= threshold), the change onset occurred at or before T_mid:
           Search left partition [left, mid - 1].
        3. If no change detected, change onset occurred after T_mid:
           Search right partition [mid + 1, right].
        Runs in ceil(log2(N)) forward passes!
        """
        n = len(observations)
        if n < 2:
            return {"status": "insufficient_data", "steps_evaluated": 0}

        left = 1
        right = n - 1
        earliest_idx = None
        earliest_pct = 0.0
        steps_evaluated = 0
        bisection_trace = []

        base_obs = observations[0]

        while left <= right:
            mid = (left + right) // 2
            mid_obs = observations[mid]
            steps_evaluated += 1

            pct = eval_fn(base_obs["image"], mid_obs["image"])
            has_change = pct >= change_threshold

            bisection_trace.append({
                "step": steps_evaluated,
                "interval_tested": f"{base_obs.get('timestamp', 'T0')} -> {mid_obs.get('timestamp', f'T{mid}')}",
                "midpoint_index": mid,
                "change_percent": round(pct, 2),
                "has_change": has_change
            })

            if has_change:
                earliest_idx = mid
                earliest_pct = pct
                right = mid - 1
            else:
                left = mid + 1

        if earliest_idx is not None:
            found_obs = observations[earliest_idx]
            return {
                "status": "change_detected",
                "earliest_timestamp": found_obs.get("timestamp", f"T{earliest_idx}"),
                "earliest_index": earliest_idx,
                "change_percent": round(earliest_pct, 2),
                "total_sequence_length": n,
                "steps_evaluated": steps_evaluated,
                "theoretical_o_log_n_bound": int(np.ceil(np.log2(n))),
                "bisection_trace": bisection_trace
            }
        else:
            return {
                "status": "no_change_detected",
                "total_sequence_length": n,
                "steps_evaluated": steps_evaluated,
                "theoretical_o_log_n_bound": int(np.ceil(np.log2(n))),
                "bisection_trace": bisection_trace
            }
