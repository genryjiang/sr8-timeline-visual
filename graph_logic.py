import networkx as nx
import pygraphviz as pgv
import pandas as pd
from io import StringIO
import os
from difflib import get_close_matches
from IPython.display import display
import time

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
    "EXT - Siltrax",
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
# display(df)
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
 #   print ("Starting Loop")
    assembly = row["Assembly"].strip()
    # Create node
    # print("Looking at: " + assembly)
    G.add_node(assembly, label=assembly)

    # Populate with partners first
    if assembly in possible_matches:
        G.add_edge('Source', assembly, label='INF')
        if G.has_edge('Source', assembly):
            print("================ Source --> PARTNER EDGE ADDED SUCCESSFULLY ===================")
        else:
            print("unable to find source to partner edge")

    # Populate internal links now
    # if NaN partners + preds, then we are a start of a branch
    if not pd.isna(row["Partners"]):
        if pd.isna(row["Partners"]) and pd.isna(row["Predecessor"]):
            G.add_edge('Source', assembly)
        # if NaN Successors, we are the end of a branch
        if (pd.isna(row["Successor"])):
            G.add_edge(assembly, "Sink")
        # Populate links (to Successors)
      #  print("Total Successor list: " + str(row["Successor"]).strip())
        for succ in str(row["Successor"]).strip().split(", "):
           # print("Successor value: " + succ)
            if succ not in ('N/A', 'nan'):
              #  print('======== Adding Successor:' + succ)
                G.add_edge(assembly, succ, label=row["EdgeWeight"], weight=row['EdgeWeight'])
               # print('Done adding Successor')

        # Populate Links (to partners)
        for part in str(row['Partners']).strip().split(', '):
          #  print("Attemping to add partner: " + part)
            if part not in ('nan', 'N/A'):
                partAdd = 'EXT - ' + part
                G.add_edge(partAdd, assembly, label=row["PartnerWeight"], weight=row['PartnerWeight'])
               # print("Done adding partner")


#print("All edges:")
#print(G.edges())

print("Finshed graph setup - print")

print("Hello from layout")
# make it left→right, with more separation, and also 90 degree lines
G.graph_attr.update(rankdir="LR")

G.write("sr8_timeline.dot")
print(".dot written")
svg_bytes = G.draw(format="svg", prog="dot")
with open("interactive_dag.svg", "wb") as f:
    f.write(svg_bytes)

print("Wrote interactive_dag.svg")
