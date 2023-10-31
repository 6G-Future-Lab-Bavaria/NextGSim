#!/bin/bash

nums_of_users=(50 100 150 200 250 300 350 400 450 500)


for num_of_user in "${nums_of_users[@]}"; do
  python3 SimulationBash.py "$num_of_user"
done


