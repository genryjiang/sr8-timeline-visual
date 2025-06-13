import pygraphviz as pgv

# 1. Build your graph
G = pgv.AGraph(strict=False, directed=True)
# explicitly add nodes with labels
for name in ["A","B","C","D"]:
    G.add_node(name, label=name)

# then add edges as before
G.add_edge("A", "B", label="2.5", weight="2.5")
G.add_edge("A", "C", label="1.0", weight="1.0")
G.add_edge("B", "D", label="3.2", weight="3.2")
G.add_edge("C", "D", label="4.1", weight="4.1")
G.add_edge("A", "D", label="Test", weight="2.7")

G.graph_attr.update(rankdir="LR")
G.layout(prog="dot")
dot_source = G.string()

