import re
from SPARQLWrapper import SPARQLWrapper, POST, BASIC, JSON, XML
import networkx as nx
import matplotlib.pyplot as plt

def ccToLines(label):
    label = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r'\n\1', label)
    return label

def run_select_query( StateToExplain, fig_path, auth):
    query = f"""
    PREFIX sense:  <http://w3id.org/explainability/sense#>

    SELECT ?cause ?effect 
    WHERE {{
    ?cause sense:causes ?effect .
    ?effect (sense:causes)* sense:{StateToExplain} .
    }}
    """
    endpoint = f"{auth['repo']}"
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setCredentials(auth["user"],auth["password"])
    sparql.setHTTPAuth(BASIC)
    sparql.setReturnFormat(JSON)

    results = sparql.queryAndConvert()
    
    G = nx.DiGraph()
    for result in results["results"]["bindings"]:
        cause = ccToLines(result["cause"]["value"].split("#")[1])
        effect = ccToLines(result["effect"]["value"].split("#")[1])
        print(result["cause"]["value"], "caused", result["effect"]["value"])
        G.add_node(cause, label = cause)
        G.add_node(effect, label = effect)
        G.add_edge(cause, effect)
    
    color_map = []
    for node in G:
        if node == ccToLines(StateToExplain):
            color_map.append('orange')
        else: 
            color_map.append('green')   

    nx.draw(G, with_labels = True, node_size = 5000, node_color = color_map, font_size = 10 )
    plt.savefig(fig_path, format="PNG")
    print(f"A visual graph of the explanation was stored at {fig_path}")
    return results
