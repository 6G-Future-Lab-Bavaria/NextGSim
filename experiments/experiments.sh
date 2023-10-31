#!/bin/bash

cycles_per_bit=(11250 45000)
algorithms=("Round_Robin" "Proportional_Fair" "Random" "Max_Rate")
nums_of_users=(110 120 130 140 150)

for num_of_user in "${nums_of_users[@]}"; do
  for algorithm in "${algorithms[@]}"; do
    for cycle_per_bit in "${cycles_per_bit[@]}"; do
        python3 SimulationBash.py "$num_of_user" "$algorithm" "$cycle_per_bit"
    done
  done
done