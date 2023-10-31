# import matplotlib.pyplot as plt
# import numpy as np
#
# # use ggplot style for more sophisticated visuals
# plt.style.use('ggplot')
#
#
# class RealTimeGraphs:
#     def live_plotter(x_vec, y1_data, line1, identifier='', pause_time=0.1):
#         if line1 == []:
#             # this is the call to matplotlib that allows dynamic plotting
#             plt.ion()
#             fig = plt.figure(figsize=(13, 6))
#             ax = fig.add_subplot(111)
#             # create a variable for the line so we can later update it
#             line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
#             # update plot label/title
#             plt.ylabel('Y Label')
#             plt.title('Title: {}'.format(identifier))
#             plt.show()
#
#         # after the figure, axis, and line are created, we only need to update the y-data
#         line1.set_ydata(y1_data)
#         # adjust limits if new data goes beyond bounds
#         # if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
#         #    plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])
#         # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
#         plt.pause(pause_time)
#
#         # return line so we can update it again in the next iteration
#         return line1
# """
# size = 100
# x_vec = np.linspace(0,1,size+1)[0:-1]
# y_vec = np.random.randn(len(x_vec))
# line1 = []
# while True:
#     rand_val = np.random.randn(1)
#     y_vec[-1] = rand_val
#     line1 = live_plotter(x_vec,y_vec,line1)
#     y_vec = np.append(y_vec[1:],0.0)
# """

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import string

width, height = 200, 200

# set up matplotlib figure & axis configuration
fig = plt.figure()
fx = max(3.0 / 2.0 * 1.25 * 10/ fig.dpi, 8.0)
fy = max(1.25 * 10 / fig.dpi, 5.0)
plt.close()
fig = plt.figure(figsize=(fx, fy))
gs = fig.add_gridspec(
    ncols=2,
    nrows=3,
    width_ratios=(4, 2),
    height_ratios=(2, 3, 3),
    hspace=0.45,
    wspace=0.2,
    top=0.95,
    bottom=0.15,
    left=0.025,
    right=0.955,
)

sim_ax = fig.add_subplot(gs[:, 0])
dash_ax = fig.add_subplot(gs[0, 1])
qoe_ax = fig.add_subplot(gs[1, 1])
conn_ax = fig.add_subplot(
    gs[2, 1],
)


# align plots' y-axis labels
fig.align_ylabels((qoe_ax, conn_ax))
canvas = FigureCanvas(fig)
canvas.draw()
plt.show()




def render_simulation(ax) -> None:
    colormap = cm.get_cmap("RdYlGn")
    # define normalization for unscaled utilities
    unorm = plt.Normalize(self.utility.lower, self.utility.upper)

    for ue, utility in self.utilities.items():
        # plot UE by its (unscaled) utility
        utility = self.utility.unscale(utility)
        color = colormap(unorm(utility))

        ax.scatter(
            ue.point.x,
            ue.point.y,
            s=200,
            zorder=2,
            color=color,
            marker="o",
        )
        ax.annotate(
            ue.ue_id, xy=(ue.point.x, ue.point.y), ha="center", va="center"
        )

    for bs in self.stations.values():
        # plot BS symbol and annonate by its BS ID
        ax.plot(
            bs.point.x,
            bs.point.y,
            marker="*",
            markersize=30,
            markeredgewidth=0.1,
            color="black",
        )
        bs_id = string.ascii_uppercase[bs.bs_id]
        ax.annotate(
            bs_id,
            xy=(bs.point.x, bs.point.y),
            xytext=(0, -25),
            ha="center",
            va="bottom",
            textcoords="offset points",
        )

        # plot BS ranges where UEs may connect or can receive at most 1MB/s
        ax.scatter(*self.conn_isolines[bs], color="gray", s=3)
        ax.scatter(*self.mb_isolines[bs], color="black", s=3)

    for bs in self.stations.values():
        for ue in self.connections[bs]:
            # color is connection's contribution to the UE's total utility
            share = self.datarates[(bs, ue)] / self.macro[ue]
            share = share * self.utility.unscale(self.utilities[ue])
            color = colormap(unorm(share))

            # add black background/borders for lines for visibility
            ax.plot(
                [ue.point.x, bs.point.x],
                [ue.point.y, bs.point.y],
                color=color,
                path_effects=[
                    pe.SimpleLineShadow(shadow_color="black"),
                    pe.Normal(),
                ],
                linewidth=3,
                zorder=-1,
            )

    # remove ran_simulation axis's ticks and spines
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.set_xlim([0, width])
    ax.set_ylim([0, height])

render_simulation(sim_ax)