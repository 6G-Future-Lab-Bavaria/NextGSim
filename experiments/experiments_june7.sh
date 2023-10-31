#!/bin/bash

nums_of_instances=(10 11 12 13 14 15 16 17 18 19 20)

for num_of_instance in "${nums_of_instances[@]}"; do
  python3 SimulationBash.py "$num_of_instance"
done

exit

