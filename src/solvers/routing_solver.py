from abc import ABC, abstractmethod

from src.solvers.solution import FleetSolution


class RoutingSolver(ABC):
    """Common interface for fleet routing algorithms."""

    @abstractmethod
    def solve(self, hub_node, customer_nodes, vehicle_count, capacity,
              net_graph, demands=None) -> FleetSolution:
        """Compute routes for a fleet of vehicles serving customer_nodes."""
        raise NotImplementedError
