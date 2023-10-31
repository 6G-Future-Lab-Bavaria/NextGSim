#!/bin/bash

algorithms=("radio-aware", None)
nums_of_users=(10 20 30 40 50 60 70 80 90 100 110 120)

for algorithm in "${algorithms[@]}"; do
  for num_of_user in "${nums_of_users[@]}"; do
    python3 SimulationBash.py "$num_of_user" "$algorithm"
  done
done