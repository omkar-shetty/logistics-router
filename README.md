# Logistics Router: Fleet Delivery Route Optimizer

---
## Executive Summary
A tool for optimizing delivery routes in urban environments by simulating real-world traffic conditions.

Many routing demonstrations rely on synthetic grids or toy graphs, which understate the irregularity of real street networks and the variability of urban traffic. This project builds a fleet dispatch system on an actual street network pulled from OpenStreetMap (a subgraph of Brooklyn, NY). Also, delivery stops are assigned by urgency, clustered geographically, and routed per vehicle under capacity constraints.

This project aims to compare the performance for a greedy algorithm vs. an OR based optimizer and a Reinforcement Learning algorithm.

## Key Features and Architecture

* **Network**: SpatialDataMapper downloads a subgraph of Brooklyn's street network via OSMnx, centered on a configurable point (currently DUMBO,NYC , chosen for its irregular street layout).

* **Node roles**. Once the graph is built, LogisticsNetwork.assign_roles() designates warehouse, hubs, and the remaining nodes as customers. Customer nodes are assigned an urgency level (0/1/2, weighted 60/30/10) and a demand value between 5 and 25 units.

* **Edge cost**. Routing uses a composite cost function rather than raw travel time: 0.7 × normalized_travel_time + 0.3 × normalized_distance. Weights are configurable in normalize_edge_attributes().

* **Traffic**. simulate_traffic(intensity) perturbs edge weights using Gaussian noise, with higher variance applied to lower-capacity roads and lower variance on arterials.

* **Dispatch**. In multi-vehicle mode, high-urgency customer nodes are clustered using KMeans (one cluster per vehicle), and each vehicle executes a greedy nearest-neighbor route within its assigned cluster, subject to a capacity constraint.

## Getting Started

1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

2. Run the main program:
   ```
   python main.py
   ```

The first run downloads and caches the street network to data/brooklyn_net.json; subsequent runs load from cache. Delete this file to regenerate the network from source.

To switch between single and multi-vehicle mode, set `RUN_TYPE` in `main.py`:
```python
RUN_TYPE = 'single'   # single vehicle, greedy NN
RUN_TYPE = 'multi'    # 3-vehicle fleet with KMeans dispatch
```
VEHICLE_CAPACITY and VEHICLE_COUNT are also configured in main.py.

## Project Structure

```
logistics-router/
├── main.py                     # entry point
├── src/
│   ├── spatial_data_mapper.py  # OSMnx download and subgraph sampling
│   ├── network_generator.py    # LogisticsNetwork: roles, costs, traffic, visualization
│   ├── vehicle_router.py       # Vehicle class and routing logic
│   └── logger.py
├── poc/
│   └── network_definition.py   # poc for hub-and-spoke topology
├── results/                    # generated visualizations
├── data/                       # cached network JSON
└── requirements.txt
```

## Current Capabilities

* Real street network ingestion via OSMnx, cached locally after initial download
* Warehouse/hub/customer node hierarchy with urgency and demand attributes
* Composite edge cost function (time and distance)
* Greedy routing implementation for single vehicle and multi vehicle fleets (with K means grouping)

## Results

Output for a multi-vehicle run - three vehicles, capacity of 150 units each:

=== Fleet Summary ===
Vehicles deployed: 3
Total fleet travel time: 27.0 mins
Stops served: 25/28
  V0: 9 stops, 7.1 mins, load=139.69
  V1: 13 stops, 13.0 mins, load=146.04
  V2: 3 stops, 6.9 mins, load=27.11

Key takeaways:
* 25 out of 28 urgent stops were served with the current capacity setting. 
* The routes for all three vehicles are imbalanced (3 stops vs. 9 stops vs. 13 stops). This reflects the impact of the Kmeans partition for this run.

### Street Network with routes overlaid

![alt text](brooklyn_street_network.png)

### Network Topology Schematic

![alt text](fleet_dispatch_schematic.png)

## Known Limitations:
* Greedy routing generates a non optimal path.
* Capacity handling is simplified, resulting in missed stops.
* Traffic modeling is approximate.

## Roadmap

* Implementation of a OR based solver.
* Proper handling of the capacity-skip limitations by enabling a return to hub.
* RL based implementation.


## License

MIT