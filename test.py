import networkx as nx
from cairosvg import svg2png

nodes = [0, (1, {"label": "aaaaaaaa"}), 2, (3, {"color": "red", "fontcolor": "red"}), 4]
edges = [
    (0, 1), (1, 2), (2, 3,{"penwidth":"5.0"}), (3, 4), (4, 0),
    (0, 0), (0, 0),
    (1, 2), (1, 2), (1, 3), (1, 4, {"penwidth":"8.0"}),
    (3, 1), (4, 1, {"len":"5.0", "label": "A", "fontcolor": "blue", "color": "0.000 1.000 1.000","penwidth":"3.0"})
    ]

g = nx.MultiDiGraph() #  グラフの種類

g.add_nodes_from(nodes) #  グラフにノード追加
g.add_edges_from(edges) #  グラフにエッジ追加

agraph = nx.nx_agraph.to_agraph(g)
agraph.node_attr["shape"] = "circle" #  表示方法変更
agraph.draw( "./sample.svg", prog="fdp", format="svg")
# SVGをPNGに変換
svg2png(url="./sample.svg", write_to="./sample.png")