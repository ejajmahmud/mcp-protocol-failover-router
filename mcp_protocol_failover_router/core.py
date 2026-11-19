"""Core Protocol Failover Router."""
from typing import Dict, List, Optional, Callable, Any
import enum
import time

class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class UpstreamEndpoint:
    def __init__(self, endpoint_id: str, invoke_fn: Callable[[Dict[str, Any]], Any], failure_threshold: int = 3, cooldown_seconds: float = 5.0):
        self.endpoint_id = endpoint_id
        self.invoke_fn = invoke_fn
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time = 0.0

    def record_success(self):
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def is_available(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True # Half-open allows trial

class ProtocolFailoverRouter:
    def __init__(self):
        self.endpoints: List[UpstreamEndpoint] = []

    def add_endpoint(self, endpoint: UpstreamEndpoint):
        self.endpoints.append(endpoint)

    def route(self, arguments: Dict[str, Any]) -> Any:
        errors = []
        for ep in self.endpoints:
            if ep.is_available():
                try:
                    result = ep.invoke_fn(arguments)
                    ep.record_success()
                    return result
                except Exception as e:
                    ep.record_failure()
                    errors.append(f"{ep.endpoint_id}: {e}")
        raise RuntimeError(f"All upstream endpoints failed: {', '.join(errors)}")
