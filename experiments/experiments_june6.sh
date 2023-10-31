#!/bin/bash

algorithms=("radio-aware" None)
nums_of_users=(350)
sch_algos=("Proportional_Fair" "Max_Rate" "Round_Robin" "Random")


for num_of_user in "${nums_of_users[@]}"; do
  for algorithm in "${algorithms[@]}"; do
      for scheduling_algorithm in "${sch_algos[@]}"; do
        python3 SimulationBash.py "$num_of_user" "$algorithm" "$scheduling_algorithm"
      done
  done
done

exit

