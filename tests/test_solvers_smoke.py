import networkx as nx
import pytest

from src.network.network_generator import LogisticsNetwork
from src.solvers.greedy_solver import GreedySolver
from src.solvers.or_solver import ORSolver

HUB = "hub"
CUSTOMERS = ["c1", "c2", "c3", "c4", "c5"]
DEMANDS = {"c1": 10, "c2": 10, "c3": 10, "c4": 10, "c5": 10}
VEHICLE_COUNT = 2
CAPACITY = 30


def build_test_network():
    g = nx.DiGraph()
    g.add_node(HUB, type="warehouse", x=0, y=0, demand=0, urgency=0)
    positions = {"c1": 1, "c2": 2, "c3": 3, "c4": 4, "c5": 5}
    for node, x in positions.items():
        g.add_node(node, type="customer", x=x, y=0, demand=DEMANDS[node], urgency=1)

    nodes = [HUB] + CUSTOMERS
    for u in nodes:
        for v in nodes:
            if u == v:
                continue
            dist = abs(positions.get(u, 0) - positions.get(v, 0))
            g.add_edge(u, v, length=max(dist, 1), speed_kph=30)

    return LogisticsNetwork(input_graph=g)


@pytest.fixture
def net_graph():
    return build_test_network()


def assert_valid_solution(solution):
    all_customers = set(CUSTOMERS)
    assert solution.served | solution.skipped == all_customers
    assert solution.served & solution.skipped == set()

    assert len(solution.routes) == VEHICLE_COUNT
    assert len(solution.travel_times) == VEHICLE_COUNT

    for t in solution.travel_times:
        assert t >= 0
        assert t != float("inf")

    for route in solution.routes:
        assert route[0] == HUB
        load = sum(DEMANDS[node] for node in route[1:])
        assert load <= CAPACITY


def test_greedy_solver_returns_valid_solution(net_graph):
    solution = GreedySolver().solve(
        HUB, CUSTOMERS, vehicle_count=VEHICLE_COUNT,
        capacity=CAPACITY, net_graph=net_graph, demands=DEMANDS,
    )
    assert solution.solver_name == "greedy"
    assert_valid_solution(solution)


def test_or_solver_returns_valid_solution(net_graph):
    solution = ORSolver().solve(
        HUB, CUSTOMERS, vehicle_count=VEHICLE_COUNT,
        capacity=CAPACITY, net_graph=net_graph, demands=DEMANDS,
    )
    assert solution.solver_name == "or_tools"
    assert_valid_solution(solution)
