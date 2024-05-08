import pandas as pd
import csv
import os, sys
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD, SOSA, SSN
'''
# RML mapping of System Data Input to the SENSE Ontology
The input for the workflow is an Excelfile containing the following sheets with their respective columns:
- PlatformTypes (PlatformType, subClassOf_PlatformType)
- SensorTypes (SensorType, subClassOf_SensorType)
- Platforms (Platform, PlatformType, hostedBy_Platform)
- Sensors (Sensor, SensorType, hostedBy_Platform, observes_ObservableProperty)
- StateTypes (StateType, SensorType_possible)
- StateTypeCausality (StateType_cause, causalityType, temporalRelation, PlatformRequirements, StateType_effect)
'''

# Define Data Source
dataSource = sys.argv[1]

csvPath = "./data/"+dataSource + "/SystemDataInput"

if not os.path.exists("./data/"+dataSource+"/RDFdata"):
    os.makedirs("./data/"+dataSource +"/RDFdata")

ttlPath = "./data/"+dataSource +"/RDFdata"

 
def excel_to_csv(source):
    if not os.path.exists("./data/"+source+"/SystemDataInput.xlsx"):
        print("XLSX input file does not exist, please provide an input file to the system folder.")
        return
    # create folder if it does not exist yet
    if not os.path.exists("./data/"+source +"/SystemDataInput"):
        os.makedirs("./data/"+source +"/SystemDataInput")

    # Read the Excel file
    with pd.ExcelFile("./data/"+source+"/SystemDataInput.xlsx") as xls:  
    # Loop through each sheet in the Excel file
        for sheet_name in xls.sheet_names:
            # Read the sheet into a DataFrame
            df = pd.read_excel("./data/"+source+"/SystemDataInput.xlsx", sheet_name=sheet_name)
            
            # Construct the output file path
            output_file = f"./data/{source}/SystemDataInput/{sheet_name}.csv"
            
            # Write the DataFrame to a CSV file
            df.to_csv(output_file, index=False)

excel_to_csv(dataSource)

# imported namespaces: RDF, RDFS, SKOS, XSD, SOSA, SSN
S = Namespace("http://w3id.org/explainability/sense#")

g = Graph()
g.bind("s", S)
g.bind("sosa", SOSA)
g.bind("rdfs", RDFS)
g.bind("rdf", RDF)

# convert Platform Types to RDF
input_file = csv.DictReader(open(csvPath+"/PlatformTypes.csv"))

for row in input_file:
    row = dict(row)
    g.add((S[row["PlatformType"]], RDFS.subClassOf, S[row["subClassOf_PlatformType"]]))
    g.add((S[row["subClassOf_PlatformType"]], RDFS.subClassOf, SOSA.Platform))

# convert Sensor Types to RDF (only accepting Sensors as a System currently)
input_file = csv.DictReader(open(csvPath+"/SensorTypes.csv"))

for row in input_file:
    row = dict(row)
    g.add((S[row["SensorType"]], RDFS.subClassOf, S[row["subClassOf_SensorType"]]))    
    g.add((S[row["subClassOf_SensorType"]], RDFS.subClassOf, S.SensorType))

#TODO how to define different Sensor Types in the SENSE ontology? is it an instance or a subclass of sensor type?
#TODO if instance, how to define SensorTypes as subtypes of sensors?

# convert State Types to RDF
input_file = csv.DictReader(open(csvPath+"/StateTypes.csv"))

for row in input_file:
    row = dict(row)    
    # check if Sensor Type is defined
    if not (S[row["SensorType_possible"]], None, None) in g:
        print("The Sensor Type", row["SensorType_possible"], "has not been defined as a Sensor Type yet!" )  
    
    id = row["StateType"].replace(" ", "")
    g.add((S[id], RDF.type, S.StateType))
    g.add((S[id], RDFS.label, Literal(row["StateType"])))
    g.add((S[id], S.associatedSensorType, S[row["SensorType_possible"]]))

# convert Platforms to RDF
input_file = csv.DictReader(open(csvPath+"/Platforms.csv"))

for row in input_file:
    row = dict(row)    
    # check if Platform Type is defined
    if not (S[row["PlatformType"]], None, None) in g:
        print("The Platform Type", row["PlatformType"], "has not been defined as a Platform Type yet!" )  
    
    g.add((S[row["Platform"]], RDF.type, S[row["PlatformType"]]))
    g.add((S[row["Platform"]], RDFS.label, Literal(row["Platform"])))
    if row["hostedBy_Platform"] != "":
        g.add((S[row["hostedBy_Platform"]], SOSA.hosts, S[row["Platform"]]))


# convert Sensors to RDF
input_file = csv.DictReader(open(csvPath+"/Sensors.csv"))

for row in input_file:
    row = dict(row) 
    # check if Sensor Type is defined   
    if not (S[row["SensorType"]], None, None) in g:
        print("The Sensor Type", row["SensorType"], "has not been defined as a Sensor Type yet!" )  
    
    g.add((S[row["Sensor"]], RDF.type, SOSA.Sensor))
    g.add((S[row["Sensor"]], S.hasSensorType, S[row["SensorType"]]))

    g.add((S[row["Sensor"]], RDFS.label, Literal(row["Sensor"])))
    g.add((S[row["hostedBy_Platform"]], SOSA.hosts, S[row["Sensor"]]))
    g.add((S[row["Sensor"]], SOSA.observes, S[row["observes_ObservableProperty"]]))

# convert Event-to-State Mapping to RDF
input_file = csv.DictReader(open(csvPath+"/EventStateMapping.csv"))

for row in input_file:
    row = dict(row)   
    
    # define Event Type
    g.add((S[row["EventType"]], RDF.type, S.EventType))
    g.add((S[row["EventType"]], RDFS.label, Literal(row["EventType"])))
    #TODO add associated Sensor Type to the EventType

    # add Mapping relation - check if State Type is defined
    if row["StateType_starts"] != "":
        if not (S[row["StateType_starts"]], None, None) in g:
            print("The State Type", row["StateType_starts"], "has not been defined as a State Type yet!" )      
        g.add((S[row["StateType_starts"]], S.hasStartEventType, S[row["EventType"]]))
    if row["StateType_ends"] != "":
        if not (S[row["StateType_ends"]], None, None) in g:
            print("The State Type", row["StateType_ends"], "has not been defined as a State Type yet!" )  
        g.add((S[row["StateType_ends"]], S.hasEndEventType, S[row["EventType"]]))


# convert State Type Causality to RDF
input_file = csv.DictReader(open(csvPath+"/StateTypeCausality.csv"))
id = 1
for row in input_file:
    row = dict(row) 
    # check if Sensor Type is defined   
    if not (S[row["StateType_cause"].replace(" ", "")], None, None) in g:
        print("The State Type", row["StateType_cause"], "has not been defined as a State Type yet!" )  
    if not (S[row["StateType_effect"].replace(" ", "")], None, None) in g:
        print("The State Type", row["StateType_effect"], "has not been defined as a State Type yet!" ) 

    label = row["StateType_cause"]+" "+row["causalRelation"]+" "+row["StateType_effect"]
    g.add((S["StateTypeCausality"+str(id)], RDF.type,                S.StateTypeCausality))
    g.add((S["StateTypeCausality"+str(id)], RDFS.label,              Literal(label)))
    g.add((S["StateTypeCausality"+str(id)], S.hasCausalRelation,     S[row["causalRelation"]]))
    g.add((S["StateTypeCausality"+str(id)], S.hasTemporalRelation,   S[row["temporalRelation"]]))
    g.add((S["StateTypeCausality"+str(id)], S.hasTopologicalRelation,S[row["topologicalRelation"]]))
    g.add((S["StateTypeCausality"+str(id)], S.cause,                 S[row["StateType_cause"].replace(" ", "")]))
    g.add((S["StateTypeCausality"+str(id)], S.effect,                S[row["StateType_effect"].replace(" ", "")]))

    g.add((S[row["causalRelation"]],      RDF.type,   S.causalRelation))
    g.add((S[row["temporalRelation"]],    RDF.type,   S.temporalRelation))
    g.add((S[row["topologicalRelation"]], RDF.type,   S.topologicalRelation))

    id +=1

g.serialize(destination = f"{ttlPath}/SystemDataInput.ttl", format='ttl')