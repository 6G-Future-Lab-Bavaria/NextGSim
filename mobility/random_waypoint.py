# @Author:  Anna Prado
# @Date: 2020-11-15
# @Email:  anna.prado@tum.de
# @Last modified by: Alba Jano

import numpy as np


def get_next_user_position(num_tti, x_max, y_max, x0, y0):
    x_max -= 50
    y_max -= 50
    # Set initial coordinates
    # x0 = np.random.uniform(0, x_max)
    # y0 = np.random.uniform(0, y_max)
    x0 = float(x0)
    y0 = float(y0)
    # Set current coordinates
    x_curr = x0
    y_curr = y0

    # Initialize array of coordinates history
    x_ac = [x0]
    y_ac = [y0]

    # Initialize destination coordinates
    xd = x0
    yd = y0

    # Set number and index of steps
    n_steps =num_tti # 700 / (MeasurementParams.update_ue_position_gap / 1000) / 2  # / 2.5
    step_i = 0

    # Set waiting parameters
    waiting = True
    n_waiting = 0  # no waiting
    wait_i = 0

    while len(x_ac) < num_tti:
        if not waiting:
            if step_i < n_steps:
                # Update current coordinates in our way to the destination
                x_curr = x0 + (xd-x0)*step_i/n_steps
                y_curr = y0 + (yd-y0)*step_i/n_steps
                step_i += 1
            else:
                # Set current coordinates to destination and wait
                x_curr = xd
                y_curr = yd
                step_i = 0
                waiting = True
            # Accumulate coordinates
            x_ac.append(x_curr)
            y_ac.append(y_curr)
        else:
            if wait_i <= n_waiting:
                wait_i += 1
            else:
                wait_i = 0

                # Update initial and destination coordinates
                x0 = xd
                y0 = yd
                xd = np.random.uniform(0, x_max)
                yd = np.random.uniform(0, y_max)
                waiting = False
    return x_ac, y_ac