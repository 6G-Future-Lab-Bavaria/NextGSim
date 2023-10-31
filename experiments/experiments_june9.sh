#!/bin/bash

algorithms=("radio-aware")
num_instances=(5 6 7 8 9 10 11 12 13 14 15)
seeds=(1 2 3 4 5 6 7 8 9 10)

for algorithm in "${algorithms[@]}"; do
  for seed in "${seeds[@]}"; do
    for num_instance in "${num_instances[@]}"; do
      python3 SimulationBash.py 150 "$algorithm" "Round_Robin" "$seed" "$num_instance"
    done
  done
done


exit

