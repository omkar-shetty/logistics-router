import osmnx as ox
import networkx as nx
import random 

from .network_generator import LogisticsNetwork

#from src.network_generator import LogisticsNetwork

class SpatialDataMapper:

    @staticmethod
    def from_place(place_name, target_nodes=30):
        graph = ox.graph_from_place(place_name, network_type='drive')
        print(f'downloaded map for {place_name}.')
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)
        graph = ox.convert.to_digraph(graph)

        #Generate a sub-graph
        start_node = random.choice(list(graph.nodes))
        nodes = list(nx.bfs_tree(graph, start_node, depth_limit=10).nodes())[:target_nodes*2]
        sub_G = graph.subgraph(nodes).copy()

        sccs = list(nx.strongly_connected_components(sub_G))
        largest_scc = max(sccs, key=len)
        
        final_G = sub_G.subgraph(largest_scc).copy()

        return LogisticsNetwork(final_G)
