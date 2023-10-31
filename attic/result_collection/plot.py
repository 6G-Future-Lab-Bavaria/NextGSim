import time
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from edge.entities.Entity import get_entity_by_id


class LatencyPlot:
    """
    Plot that shows E2E latency of an application.
    """

    # Suppose we know the y range
    min_y = 0
    max_y = 60
    INIT_GRAPH = False
    rects = None

    def __init__(self):
        # plt.ion()
        # matplotlib.use("TKAgg")
        # Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], 'o')
        label_x = self.ax.set_xlabel('Application \n Name', fontsize=12)
        self.ax.xaxis.set_label_coords(1.07, 0)
        label_y = self.ax.set_ylabel('E2E Latencies (ms)', fontsize=12)
        plt.title("E2E Latency of Application")
        # Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(False)
        matplotlib.pyplot.subplots_adjust(bottom=0.238)

    def on_running(self, xdata, ydata):
        # Update data (with the new _and_ the old points)
        self.ax.set_ylim(self.min_y, self.max_y)
        if self.INIT_GRAPH is False:
            self.rects = self.ax.bar(xdata, ydata)
            self.INIT_GRAPH = True
        else:
            for rect, h in zip(self.rects, ydata):
                rect.set_height(h)

        plt.xticks(rotation=90)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        time.sleep(0.01)

    def __call__(self, xdata, ydata):
        self.on_running(xdata, ydata)
