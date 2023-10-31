#!/bin/bash

algorithms=("radio-aware")
nums_of_users=(400)


for num_of_user in "${nums_of_users[@]}"; do
  for algorithm in "${algorithms[@]}"; do
    python3 SimulationBash.py "$num_of_user" "$algorithm"
  done
done


