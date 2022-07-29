import networkx as nx
from cairosvg import svg2png

nodes = [i for i in range(15)]
edges = [(0,1),(1,0),(0,4),(1,2),(1,5),(2,3),(2,6),(3,7),(4,5),(4,8),(5,6),(5,9),(6,7),(6,10),(7,11),(8,9),(8,12),(9,10),(9,13),(10,11),(10,14),(11,15),(12,13),(13,14),(14,15)]

g = nx.MultiDiGraph() #  グラフの種類

g.add_nodes_from(nodes) #  グラフにノード追加
g.add_edges_from(edges) #  グラフにエッジ追加

agraph = nx.nx_agraph.to_agraph(g)
agraph.node_attr["shape"] = "circle" #  表示方法変更
agraph.draw( "./sample.svg", prog="fdp", format="svg")
# SVGをPNGに変換
svg2png(url="./sample.svg", write_to="./sample.png")