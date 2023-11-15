#!/bin/bash

export PYTHONPATH=../

radio_algorithms=("Round_Robin")
edge_algorithms=("Radio-Aware" "FCFS")
nums_of_users=(50 150)
seeds=(1 2 3 4 5 6 7 8 9 10)
num_of_instances=(5 6 7 8 9 10 11 12 13 14 15)

for num_of_user in "${nums_of_users[@]}"; do
  for radio_algorithm in "${radio_algorithms[@]}"; do
    for edge_algorithm in "${edge_algorithms[@]}"; do
      for seed in "${seeds[@]}"; do
        for num_instance in "${num_of_instances[@]}"; do
            python3 ../runtime/Simulations_Figure6.py "$num_of_user" "$radio_algorithm" "$edge_algorithm" "$seed" "$num_instance"
            done
        done
      done
  done
done