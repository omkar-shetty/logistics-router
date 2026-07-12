from dataclasses import dataclass, field


@dataclass
class FleetSolution:
    """Result of running a RoutingSolver over a fleet."""
    routes: list
    travel_times: list
    served: set
    skipped: set
    solver_name: str
