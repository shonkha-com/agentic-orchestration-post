import json
import logging
from datetime import datetime
from pathlib import Path
from smolagents.memory import ActionStep, TaskStep


class SessionLogger:
    """Logs every smolagents session step to a timestamped file."""

    def __init__(self, log_dir: str = "logs"):
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(log_dir) / f"session_{timestamp}.log"

        self._logger = logging.getLogger(f"smolagents.session.{timestamp}")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s"))
        self._logger.addHandler(handler)

        self.log_path = log_path
        self._logger.info(f"Session started — log: {log_path}")

    def on_task(self, step: TaskStep) -> None:
        self._logger.info(f"[TASK] {step.task.strip()}")

    def on_action(self, step: ActionStep) -> None:
        parts = [f"[STEP {step.step_number}]"]

        if step.model_output:
            parts.append(f"thoughts: {step.model_output.strip()}")

        if hasattr(step, "code_action") and step.code_action:
            parts.append(f"code:\n{step.code_action.strip()}")
        elif hasattr(step, "tool_calls") and step.tool_calls:
            parts.append(f"tool_calls: {step.tool_calls}")

        if step.observations:
            parts.append(f"observations: {step.observations.strip()}")

        if step.error:
            parts.append(f"error: {step.error}")

        if step.token_usage:
            parts.append(
                f"tokens: in={step.token_usage.input_tokens} out={step.token_usage.output_tokens}"
            )

        if step.is_final_answer:
            parts.append(f"FINAL ANSWER: {json.dumps(step.action_output, default=str)}")

        level = logging.ERROR if step.error else logging.INFO
        self._logger.log(level, "\n  ".join(parts))

    @property
    def callbacks(self) -> dict:
        """Pass this to CodeAgent(step_callbacks=logger.callbacks)."""
        return {
            TaskStep: self.on_task,
            ActionStep: self.on_action,
        }

    def close(self) -> None:
        self._logger.info("Session ended.")
        for h in self._logger.handlers[:]:
            h.close()
            self._logger.removeHandler(h)
