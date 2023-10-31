#!/bin/bash

algorithms=("radio-aware" None)
nums_of_users=(25 50 75 100 125 150 175 200 225 250 275 300)
sch_algos=("Proportional_Fair" "Max_Rate" "Round_Robin" "Random")


for num_of_user in "${nums_of_users[@]}"; do
  for algorithm in "${algorithms[@]}"; do
      for scheduling_algorithm in "${sch_algos[@]}"; do
        python3 SimulationBash.py "$num_of_user" "$algorithm" "$scheduling_algorithm"
      done
  done
done

exit

