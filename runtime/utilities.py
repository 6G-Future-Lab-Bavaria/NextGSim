from random import randint
import os
import sys
import glob
import json
import matplotlib.pyplot as plt
from colorama import Fore


def generate_color_list(n):
    colors = []
    for i in range(n):
        colors.append('#%06X' % randint(0, 0xFFFFFF))
    return colors


def check_if_directory_plots_exists(folder):
    if not os.path.exists(str(folder)):
        os.mkdir(str(folder))


def block_print(disable_print=True):
    if disable_print:
        sys.stdout = open(os.devnull, 'w')


def enable_print():
    sys.stdout = sys.__stdout__


def check_if_directory_with_results_exists(folder):
    if not os.path.exists(f"results/{folder}"):
        os.mkdir(f"results/{folder}")


def delete_from_folder(folder):
    files = glob.glob(f"{folder}/*")
    for f in files:
        if os.path.isdir(f) or 'result' in f:
            continue
        os.remove(f)


def save_results_to_json(results, name):
    check_if_directory_plots_exists("results")
    results_name = f'results/'
    results_name += name
    results_name += '.json'
    with open(results_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)





def drawArrow(A, B, color):
    plt.arrow(A[0], A[1], B[0] - A[0], B[1] - A[1],
              head_width=2, length_includes_head=True, color=color)


def plot_mobility(X, Y, num_users, user_speed_metrics, results_name, with_users=True):
    colors = generate_color_list(num_users+1)
    if with_users:
        for user_id in range(num_users):
            plt.plot(X[user_id], Y[user_id], color=colors[user_id], linewidth=1)
            # plt.scatter(X[user_id], Y[user_id], color=colors[user_id], s=1)
            plt.scatter(X[user_id][0], Y[user_id][0], color=colors[user_id], marker='*')
            # for t in range(len(X) - 1):
            #     drawArrow((X[user_id][t], Y[user_id][t]), (X[user_id][t+1], Y[user_id][t+1]),
            #                         color=colors[user_id])
    # plt.title(f"{num_users} UEs with Vmin = {user_speed_metrics[0]}, Vmax = {user_speed_metrics[1]}, Vmean = {user_speed_metrics[2]} meters "
    #           f"per {MeasurementParams.update_ue_position_gap/10**3} s")
    plt.xlabel("Relative position (m)", fontsize=15)
    plt.ylabel("Relative position (m)", fontsize=15)

    # macro = mpatches.Patch(color='red', label='Macro', marker='*')
    # micro = mpatches.Patch(color='black', label='Micro', marker='*')
    # plt.legend(handles=[macro, micro])

    name = 'mobility' + results_name
    plt.savefig(f'results/{name}.png', dpi=300)


def show_shape(patch):
    ax = plt.gca()
    ax.add_patch(patch)
    plt.axis('scaled')
    # plt.show()


def get_all_files():
    directory = os.listdir()
    files = []
    for file in directory:
        fname, ext = os.path.splitext(file)
        if ext != '.json':
            continue
        if 'result' not in fname:
            continue
        files.append(file)
    return files


def log(filename):
    pass


def print_inter_site_distance(simulation):
    print("ISD")
    for gnb in simulation.gNBs_per_scenario:
        print(gnb.x, gnb.y)


class utility(object):
    @staticmethod
    def format_figure():
        """
        Formatting the figures to be complient with the text size in IEEE documents.
        :return: None
        """
        plt.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]
        #  Options
        params = {'text.usetex': True,
                  'font.size': 11,
                  'font.family': 'lmodern',
                  }
        plt.rcParams.update(params)

    @staticmethod
    def set_path(name="results"):
        """
        Setting the paths for saving the results in result folder.
        :return: The parent directory of our working folder
        """
        result_filename = name
        cdir = os.getcwd()
        pdir = os.path.abspath(os.path.join(cdir, os.pardir))
        print(Fore.GREEN +"[UTILITY]: Parent Directory: ", pdir)
        resultdir = os.path.abspath(os.path.join(pdir, result_filename))
        if not os.path.exists(resultdir):
            os.makedirs(resultdir)
        os.chdir(resultdir)
        print(Fore.GREEN + "[UTILITY]: Working Directory: ", resultdir)
        # print(Fore.BLACK)
        return resultdir