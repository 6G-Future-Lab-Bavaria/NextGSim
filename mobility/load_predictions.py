import pickle as pkl
import numpy as np

filename_test_pred = 'results_clean/results_tgap1_speed1_hurst0.9_seq2seq_gpu/models/test_pred.pkl'
filename_pred_simulator = 'test_pred_short.csv'

def print_stats_of_file(filename, test_pred):
    print(f"File {filename} has shape {test_pred.shape}")  # Why 3???
    num_samples = len(test_pred[0])
    look_ahead = len(test_pred[0][0])
    num_features = len(test_pred[0][0][0])
    print(f"Number of samples = {num_samples}, look ahead = {look_ahead}, number of features {num_features}")


def read_model_pred_output(filename):
    with open(filename,'rb') as file_pi:
        test_pred = pkl.load(file_pi)
    test_pred = np.array(test_pred)
    print_stats_of_file(filename, test_pred)
    test_pred_short = test_pred[0,:,1,:]
    print(f"New shape is {test_pred_short.shape}")
    return test_pred_short


def write_model_pred_output(test_pred_short, filename):
    np.savetxt(filename, test_pred_short, delimiter=",")


def read_csv_into_np(filename):
    from numpy import genfromtxt
    my_data = genfromtxt(filename, delimiter=',')
    print(f"Data shape {my_data.shape}")
    return my_data


test_pred_short = read_model_pred_output(filename_test_pred)
write_model_pred_output(test_pred_short, filename_test_pred)
# my_data = read_csv_into_np(filename_pred_simulator)