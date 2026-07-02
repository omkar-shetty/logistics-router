# Logistics Router

A tool for optimizing delivery routes in urban environments by simulating real-world traffic conditions.

Naive shortest-path routing ignores vehicle capacity, demand urgency, and dynamic traffic conditions. This project implements and benchmarks fleet strategies on a real urban street graph (Brooklyn, NY) to quantify routing tradeoffs under realistic constraints.

## Key Features

- **Builds street networks** - It downloads real street data for any location (it currently uses Brooklyn as an example)
- **Simulates traffic** - Model how traffic intensity affects travel times
- **Route planning** - Compare travel times under different traffic conditions
- **Visualize routes** - See the streets and networks on a map

## Getting Started

1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

2. Run the main program:
   ```
   python main.py
   ```

The first run downloads Brooklyn's street network and caches it to `data/brooklyn_net.json`. Subsequent runs load from cache.

To switch between single and multi-vehicle mode, set `RUN_TYPE` in `main.py`:
```python
RUN_TYPE = 'single'   # single vehicle, greedy NN
RUN_TYPE = 'multi'    # 3-vehicle fleet with KMeans dispatch
```

## Project Structure

- **main.py** - The entry point; runs the whole simulation
- **src/network_generator.py** - Creates and manages the street network
- **src/spatial_data_mapper.py** - Downloads and processes real map data
- **src/vehicle_router.py** - Plans delivery routes and vehicle movements
- **data/** - Stores the downloaded network data

## What's Next?

This is a foundation for building smarter delivery optimization. Future improvements will include multiple vehicle routing and scheduling and a reinformcement learning based algorithm.


## License

See LICENSE file for details.
