#!/bin/bash

algorithms=("radio-aware")
nums_of_users=(300 350)
sch_algos=("Proportional_Fair" "Max_Rate" "Round_Robin")
seeds=(1 2 3 4 5 6 7 8 9 10)

for num_of_user in "${nums_of_users[@]}"; do
  for algorithm in "${algorithms[@]}"; do
      for scheduling_algorithm in "${sch_algos[@]}"; do
        for seed in "${seeds[@]}"; do
          python3 SimulationBash.py "$num_of_user" "$algorithm" "$scheduling_algorithm" "$seed"
        done
      done
  done
done

exit

