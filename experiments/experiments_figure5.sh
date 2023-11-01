#!/bin/bash

export PYTHONPATH=../

radio_algorithms=("Max_Rate")
edge_algorithms=("Radio-Aware" "FCFS")
nums_of_users=(150)
seeds=(1 2 3 4 5 6 7 8 9 10)

for num_of_user in "${nums_of_users[@]}"; do
  for radio_algorithm in "${radio_algorithms[@]}"; do
    for edge_algorithm in "${edge_algorithms[@]}"; do
      for seed in "${seeds[@]}"; do
          python3 ../runtime/Simulations_Figure5.py "$num_of_user" "$radio_algorithm" "$edge_algorithm" "$seed"
        done
      done
  done
done