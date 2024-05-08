import subprocess
import json

import requests
from requests.auth import HTTPBasicAuth
from SPARQLWrapper import SPARQLWrapper, POST, BASIC

def load_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

def create_ttl_of_system_data(systemName):
    try:
        subprocess.check_call(['python', './semanticizing/XLSXtoTTL.py', systemName])
        print("System data semanticized successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the Input data to TTL conversion: {e}")

def create_ttl_of_event_data(systemName):
    try:
        subprocess.check_call(['python', './semanticizing/StatesToTTL.py', systemName])
        print("States data semanticized successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the Event to ttl conversion: {e}")

def upload_ttl_to_named_graph(path, named_graph, auth):
    url = f"{auth["repo"]}/rdf-graphs/service?graph={named_graph}"

    with open(path, 'rb') as file:
        headers = {
            'Content-Type': 'application/x-turtle', 
        }
        ## change with your credentials
        auth = HTTPBasicAuth(auth["user"], auth["password"])
        response = requests.post(url, data=file, headers=headers, auth=auth)
    if response.ok:
        print(f"{path.split("/")[-1]} successfully uploaded to named graph {named_graph}")

def run_update_query(query_path, auth):
    with open(query_path, "r") as file:
        query = file.read()
    
    sparql_endpoint = f"{auth['repo']}/statements"
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setMethod(POST)
    sparql.setQuery(query)
    sparql.setCredentials(auth["user"],auth["password"])
    sparql.setHTTPAuth(BASIC)
    
    try:
        sparql.query()
        print("Query executed successfully.")
    except Exception as e:
        print("An error occurred:", e)
