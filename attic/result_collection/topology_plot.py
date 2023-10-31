import time

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import threading
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from edge.entities.Entity import get_entity_by_id, get_entity_list
from edge.network.Link import get_link_list
from selenium import webdriver


class WebDriver(threading.Thread):
    def __init__(self):
        print('Initializing Web Driver')
        self.driver = None
        self.url = '127.0.0.1:8050'
        self.refresh_rate = 10gitlab
        threading.Thread.__init__(self)

    def run(self):
        self.driver = webdriver.Safari()
        self.driver.get("http://" + self.url)
        while True:
            time.sleep(1)
            self.driver.refresh()


class TopologyPlot(threading.Thread):
    def __init__(self, topology):
        print('Initializing T')
        self.topology = topology
        threading.Thread.__init__(self)

    def run(self):
        app = Dash(__name__)
        cytoscape_json_elements = self.parse_cytoscape_data()
        app.layout = html.Div(
            html.Div([
                cyto.Cytoscape(id='cytoscape',
                               layout={'name': 'preset'},
                               style={'width': '50%', 'height': '500px'},
                               elements=cytoscape_json_elements),
                dcc.Interval(id='interval-component', interval=100000, disabled=False, n_intervals=0)
            ])
        )


        @app.callback(Output('cytoscape', 'elements'),
                      Input('interval-component', 'interval'))
        def update_elements(interval):
            new_elements = self.parse_cytoscape_data()
            print('Updating elements')
            return new_elements

        app.run_server(debug=False)

    def parse_cytoscape_data(self):
        cytoscape_json = []
        for entity_id in self.topology.plainG.nodes:
            entry = {'data': {'id': str(entity_id), 'label': str(entity_id)},
                     'position': {'x': get_entity_by_id(entity_id).location[0],
                                  'y': get_entity_by_id(entity_id).location[1]}}
            cytoscape_json.append(entry)
        for link in self.topology.plainG.edges():
            entry = {'data': {'source': str(link[0]), 'target': str(link[1])}}
            cytoscape_json.append(entry)

        return cytoscape_json
