import osmnx as ox
import networkx as nx
import random

from .network_generator import LogisticsNetwork
from .logger import get_logger

logger = get_logger(__name__)

class SpatialDataMapper:

    @staticmethod
    def from_place(place_name, target_nodes=50, center_point=None, seed=42):
        """Builds a LogisticsNetwork from a place name.

        center_point: optional (lat, lon) tuple to centre on a specified neighbourhood.
        seed: seeds the random start-node choice (used only with center_point.)
        """
        graph = ox.graph_from_place(place_name, network_type='drive')
        logger.info(f'downloaded map for {place_name}.')
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)
        graph = ox.convert.to_digraph(graph)

        #Generate a sub-graph
        if center_point is not None:
            lat, lon = center_point
            start_node = ox.distance.nearest_nodes(graph, X=lon, Y=lat)
        else:
            start_node = random.Random(seed).choice(list(graph.nodes))
        logger.info(f"BFS sample start_node={start_node}, center_point={center_point}, seed={seed}")
        nodes = list(nx.bfs_tree(graph, start_node, depth_limit=10).nodes())[:target_nodes*2]
        sub_G = graph.subgraph(nodes).copy()

        sccs = list(nx.strongly_connected_components(sub_G))
        largest_scc = max(sccs, key=len)
        
        final_G = sub_G.subgraph(largest_scc).copy()

        return LogisticsNetwork(final_G)
