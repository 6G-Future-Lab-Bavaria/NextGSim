#!/bin/bash

algorithms=("Round_Robin" "Proportional_Fair" "Random" "Max_Rate")
replacement_algorithms=("autoscaling" "None")
nums_of_users=(10 20 30 40 50)

for replacement_algo in "${replacement_algorithms[@]}"; do
  python3 SimulationBash.py 200 "Round_Robin" "$replacement_algo"
done