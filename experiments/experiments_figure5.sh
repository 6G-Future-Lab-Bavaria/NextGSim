#!/bin/bash

export PYTHONPATH=../

radio_algorithms=("Round_Robin" "Proportional_Fair" "Random" "Max_Rate")
edge_algorithms=("FCFS" "Radio-Aware")
nums_of_users=(50)

for num_of_user in "${nums_of_users[@]}"; do
  for radio_algorithm in "${radio_algorithms[@]}"; do
    for edge_algorithm in "${edge_algorithms[@]}"; do
        python3 ../runtime/Simulations_Figure5.py "$num_of_user" "$radio_algorithm" "$edge_algorithm"
      done
  done
done