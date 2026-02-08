# Logistics Router

A tool for optimizing delivery routes in urban environments by simulating real-world traffic conditions.

This project helps figure out the best routes for delivering packages around an urban location (for example, Brooklyn) by taking into account how traffic changes throughout the day. It uses actual street maps and can simulate what happens during rush hour versus quiet times like midnight.

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

The first time you run it, it will download Brooklyn's street network (this takes a moment). After that, it saves the data so future runs are much faster.


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
