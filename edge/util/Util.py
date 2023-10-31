import numpy as np
from functools import reduce
import operator as op


def ncr(n, r):
    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer // denom  # or / in Python 2


def random_list_w_fixed_sum(array_size, sum):
    # Create an array of size m where
    # every element is initialized to 0
    arr = [0] * array_size
    factor = np.ceil(array_size / sum)

    # To make the sum of the final list as n
    for i in range(sum):
        # Increment any random element
        # from the array by 1
        arr[np.random.randint(0, sum * factor) % array_size] += 1

    # Print the generated list
    return np.array(arr)


def random_list_w_sum_1(array_size):
    if array_size == 0:
        return []
    else:
        # Create an array where sum of m elements equals 1
        arr = random_list_w_fixed_sum(array_size, 100)
        return arr / 100



def closest_node(candidate_node_arr, node):
    # Get the closest service from candidate nodes to a service (Optimized with einsum implementation)
    candidate_node_arr = np.asarray(candidate_node_arr)
    candidate_node_locations = [candidate_node.location for candidate_node in candidate_node_arr]

    deltas = candidate_node_locations - np.array(node.location)
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)

    return candidate_node_arr[np.argmin(dist_2)]


def get_key_from_value(dictionary, val):
    # Get the key of a corresponding value in a dictionary
    for key, value in dictionary.items():
        if (val == value).all():
            return key

    return "key doesn't exist"
