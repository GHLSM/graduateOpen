import pickle
import os, time
import networkx as nx
import matplotlib.pyplot as plt
from configs.config import DTC_GRAPH_PATH

class DtcGraph(object):
    def __init__(self, car_name) -> None:
        super().__init__()
        self.dtc_graph = nx.DiGraph()
        self.CAR_NAME = car_name

    def _format_node(self, nodes):
        self.dtc_graph.add_nodes_from(nodes)

    def _format_edge(self, row_edges):
        self.dtc_graph.add_edges_from(row_edges)
        
    def add_nodes(self, nodes):
        self.dtc_graph.add_nodes_from(nodes)

    def add_edges(self, edges_to_add):
        self.dtc_graph.add_edges_from(edges_to_add)

    def load_from_man(self, nodes, row_edges):
        # self.dtc_graph.clear()
        self._format_node(nodes)
        self._format_edge(row_edges)
    
    def load_from_graph(self, dtc_graph_file):
        self.dtc_graph.clear()
        file_name = dtc_graph_file.split(".")[0] + ".graph"
        file_dir_path = os.path.join(DTC_GRAPH_PATH, self.CAR_NAME)
        file_path = os.path.join(file_dir_path, file_name)
        with open(file_path.replace("\\", "/").strip(), "rb") as f:
            d = pickle.loads(f.read())
            self.dtc_graph = d

    def _reformat_graph(self, back_dtc):
        """
        shrink graph based on back_dtc
        """

        return self.dtc_graph.subgraph(back_dtc)

    def find_main_dtc(self, back_dtc, notInclude_dtc=False):
        """
        find the main dtc in back dtc data
        The attr which is need_notInclude_dtc means "if some dtc not in nodes, just loss it."， And it is False by defult.
        if you want to maintain the dtc not include in nodes, need_notInclude_dtc=True, and the return value became a tuple
        """
        # print(back_dtc, len(self.dtc_graph.nodes))
        new_back_dtc = []
        no_dtc = []
        for dtc in back_dtc:
            if dtc in self.dtc_graph.nodes:
                new_back_dtc.append(dtc)
            else:
                no_dtc.append(dtc)
        # print(new_back_dtc)
        main_dtc = []
        if back_dtc == None:
            return None

        in_degree_array = self._reformat_graph(new_back_dtc).in_degree()
        # print(in_degree_array)

        for i in in_degree_array:
            dtc, in_degree = i
            if in_degree == 0:
                main_dtc.append(dtc)
        if not notInclude_dtc:
            return main_dtc
        else:
            return main_dtc, no_dtc

    def show_pic(self):
        ax = plt.gca()
        ax.set_axis_off()
        plt.show()

    def save(self):
        file_dir_path = os.path.join(DTC_GRAPH_PATH, self.CAR_NAME)
        file_path = os.path.join(file_dir_path, time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + ".graph")
        with open(file_path.replace("\\", "/").strip(), "wb") as f:
            data = pickle.dumps(self.dtc_graph)
            f.write(data)

    
        