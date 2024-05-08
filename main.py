from helper import *
import argparse
from explanationqueries.causal_path_identification import run_select_query

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--loadData', action='store_true')
    args = parser.parse_args()
    
    config = load_config("config.json")
    auth = load_config("auth.json")

    if args.loadData == True:
        create_ttl_of_system_data(config["systemName"])
        create_ttl_of_event_data(config["systemName"])
        
        upload_ttl_to_named_graph("./data/SENSE v1.0.ttl", "http://w3id.org/explainability/sense/Ontology", auth)
        upload_ttl_to_named_graph(f"./data/{config["systemName"]}/RDFdata/SystemDataInput.ttl", f"http://w3id.org/explainability/sense/{config["systemName"]}Topology", auth)
        upload_ttl_to_named_graph(f"./data/{config["systemName"]}/RDFdata/States.ttl", f"http://w3id.org/explainability/sense/{config["systemName"]}States", auth)
            
        # for new states, query for causal connections to other states
        run_update_query("./explanationqueries/actual_causality_query.rq", auth)

    StateToExplain = input("Enter the name of the state you want to have explained: ")

    run_select_query( StateToExplain, f"graphs/{StateToExplain}.png", auth)



