# convert events.csv to ttl, only relevant until event detection module is connected.
import pandas as pd
import csv
import os, sys
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD, SOSA, SSN
from datetime import datetime, timezone, timedelta


# for now: add events from Events.csv

dataSource = sys.argv[1]

if not os.path.exists("./data/"+dataSource+"/RDFdata"):
    os.makedirs("./data/"+dataSource +"/RDFdata")

ttlPath = "./data/"+dataSource +"/RDFdata"

def convert_dateTime(datetime_str):

    # Parse the datetime string into a datetime object
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S%z')

    # # Convert the datetime object to UTC timezone
    # dt_utc = dt.astimezone(timezone.utc)

    # Format the datetime object in ISO 8601 format
    iso_datetime_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return iso_datetime_str

# imported namespaces: RDF, RDFS, SKOS, XSD, SOSA, SSN
S = Namespace("http://w3id.org/explainability/sense#")

g = Graph()
g.bind("s", S)
g.bind("sosa", SOSA)
g.bind("rdfs", RDFS)
g.bind("rdf", RDF)

# convert Platform Types to RDF
input_file = csv.DictReader(open(f"./data/{dataSource}/States.csv"))

for row in input_file:
    row = dict(row)
    # add observation of the start event
    StateID = row["StateID"].replace(" ","")

    g.add((S[row["Sensor"]], SOSA.madeObservation, S[StateID+"_obs"]))    

    g.add((S[StateID+"_obs"], RDF.type, SOSA.Observation))
    g.add((S[StateID+"_obs"], SOSA.usedProcedure, S.EventToStateConversion))
    g.add((S[StateID+"_obs"], SOSA.hasResult, S[StateID]))
    g.add((S[StateID+"_obs"], S.startTime, Literal(convert_dateTime(row["StartDate"]),datatype=XSD.dateTime)))
    g.add((S[StateID+"_obs"], S.endTime  , Literal(convert_dateTime(row["EndDate"])  ,datatype=XSD.dateTime)))

    
    g.add((S[StateID], RDF.type, S.State))
    g.add((S[StateID], S.hasStateType, S[row["StateType"].replace(" ","")]))
    g.add((S[StateID], S.hasStartEvent, S[StateID+"_start"]))
    g.add((S[StateID], S.hasEndEvent, S[StateID+"_end"]))

#TODO is it possible to add phenomenonTime somewhere, where it is more convenient than in the observation?

    
g.serialize(destination = f"{ttlPath}/States.ttl", format='ttl')