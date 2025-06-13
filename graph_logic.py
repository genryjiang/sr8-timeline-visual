import networkx as nx
import pygraphviz as pgv
import pandas as pd
from io import StringIO
import os
from difflib import get_close_matches
from IPython.display import display

# python script to visualise sr8 timeline as a flow network
# Written by: HENRY JIANG
# This could've definitely been written better :/ (first time coding since this time last year lol)

# add input header to function


# get current path to directory
fileName = 'data_input.csv'
curr_directory =os.getcwd()
csvPath =  os.path.join(curr_directory, fileName)
df = pd.read_csv(csvPath, encoding='latin1')
possible_matches = [
    "EXT - Unknown",
    "EXT - Swagelok",
    "EXT - M10",
    "EXT - Stilrax",
    "EXT - External Supplier (TBA)",
    "EXT - Bosch",
    "EXT - Corning",
    "EXT - Sundrive",
    "EXT - REOO",
    "EXT - Adlink",
    "EXT - Ricardo",
    "EXT - Bride Racing",
    "EXT - Beswick",
    "EXT - Coregas",
    "EXT - Colan",
    "EXT - Scott Bader",
    "EXT - Calm Aluminium",
    "EXT - McConaghy",
    "EXT - Espresso Conversation",
    "EXT - Stallibus",
    "EXT - Chevalier",
    "EXT - Espresso",
    "EXT - PWR",
    "EXT - Autofrost",
    "EXT - Divergent",
    "EXT - Sunswift"
]


# Sanity check on dataframe imported correctly
display(df)
# Export DataFrame to an HTML file
df.to_html('output.html', index=False)
print("DataFrame exported to output.html")

# Create graph and import convert dataFrame into graph
# METHODOLOGY:
# - Row by Row, generate nodes
# Create ext nodes first, not connected to anything

G = pgv.AGraph(strict=False, directed=True)
G.add_node('Source', label='Source')
G.add_node('Sink', label='Sink')

for _, row in df.iterrows():
    print ("Starting Loop")
    assembly = row["Assembly"].strip()
    # Create node
    print("Looking at: " + assembly)
    G.add_node(assembly, label=assembly)

    # Populate with partners first
    for partners in str(row["Partners"]).strip().split(", "):
        p = partners.strip()
        # if P is N/A or NaN, ignore (these are not partner starting nodes)
        if p.upper() == ("N/A", "NaN"):
            # Add it to best guess partner match, once we confirm that we are a partner node
            best_match = get_close_matches(p, possible_matches, n=1, cutoff=0.65)
            G.add_edge(best_match, assembly, label=row["PartnerWeight"], weight=row["PartnerWeight"])
            # Add to source
            G.add_edge('Source', best_match)

    # Populate internal links now
    # if NaN partners + preds, then we are a start of a branch
    if not pd.isna(row["Partners"]):
        if pd.isna(row["Partners"]) and pd.isna(row["Predecessor"]):
            G.add_edge('Source', assembly)
        # if NaN Successors, we are the end of a branch
        if (pd.isna(row["Successor"])):
            G.add_edge(assembly, "Sink")
        # Populate links (to Successors)
        print("Total Successor list: " + str(row["Successor"]).strip())
        for succ in str(row["Successor"]).strip().split(", "):
            print("Successor value: " + succ)
            if not (succ == 'NaN' or 'N/A'):
                print('Adding Successor')
                G.add_edge(assembly, succ, label=row["EdgeWeight"], weight=row['EdgeWeight'])
                print('Done adding Successor')
        # Populate Links (to partners)
        for part in str(row['Partners']).strip().split(', '):
            print("Attemping to add partner: " + part)
            G.add_edge(part, assembly, label=row["PartnerWeight"], weight=row['PartnerWeight'])
            print("Done adding partner")

# make it left→right, with more separation
G.graph_attr.update({
    "rankdir":   "LR",       # left-to-right instead of top-down
    "nodesep":   "0.5",      # minimum space between nodes
    "ranksep":   "0.75",     # minimum space between ranks (layers)
    "splines":   "ortho",    # right-angle edges
    "overlap":   "false",    # auto-resolve node overlaps
    "fontsize":  "10"        # smaller default font
})
# optionally, force edge labels to sit in the middle
G.edge_attr.update({
    "labeldistance": "2.0",
    "labelfontsize": "8"
})

G.layout(prog="dot")
dot_source = G.string()
# 4. Embed into an HTML template that pulls in Viz.js
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Interactive DAG</title>
<!-- Viz.js bundle -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
<style>
    body {{ margin: 0; padding: 0; }}
    #graph {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div id="graph"></div>
<script>
    const dot = `{dot_source}`;
    const viz = new Viz();
    viz.renderSVGElement(dot)
    .then(svg => {{
        document.getElementById("graph").appendChild(svg);
    }})
    .catch(err => console.error(err));
</script>
</body>
</html>
"""
# 5. Write out to a file
with open("interactive_dag.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Output done - in directory")
