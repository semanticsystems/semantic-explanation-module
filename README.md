## Explanation Engine, Version 2024-04

The Explanation Engine encapsules the full workflow from System Data Input to outputting explanations for the user.

### Configuration to provide

1. add a file called ``auth.json`` to the root folder to define access to GraphDB instance, which has the following format:
````
{
    "repo" : "repositoryURL" ,
    "user" : "username", 
    "password" : "password"
}
````
1. specify the System you want to analyse in ``config.json``. This setup defines the folder, where System Data is taken from.
2. Create a folder for the system you plan to work with in ``./data/`` and add the ``SystemDataInput.xlsx`` file as specified in [A1].
3. run ``main.py --loadData`` to set up the system. It converts the data provided in the ``data`` folder to turtle files and loads the data to the GraphDB instances specified in ``auth.json``
   1. for any additional run, you can also run the file without ``--loadData``, so not all data is re-loaded a second time.


### Data Sources
In the folder ``data``, all the data sources are available for the engine to work.
- ``SENSE.ttl``: This file is the current version of the SENSE Ontology as developed in SENSE 4.2.
- ``SystemName``: For any system, running SENSE, a folder should be created containing the following files: (SeeHub is the example system for showing the workflow)
  - ``SystemDataInput.xlsx``: An Excel File, containing the topology of the system, Event Types and their causality. Format of the File -see [A1] 
  - ``States.csv``: Currently, States are derived from a csv-file of states, but this will be replared by the event detection module (T3.4) in the future.


### Workflow as implemented in main.py
1. define System and input data from the config file (``config.json``) and user data for GraphDB in the auth file (``auth.json``)
2. Convert System Data to RDF data (``/semanticizing/XLSXtoTTL.py``)
3. convert events to states (for now, just convert Events.csv to RDF)
4. upload turtle files to the GraphDB repository
5. for a new state in the system, check for type causality and add the relation to the causal graph.
6. Explanation: input a state for which you seek an explanation. An explanation is then generated and a visual representation of the explanation is stored in ``/graphs/``.

## Appendix

[A1] ``SystemDataInput.xlsx`` Format

Domain-specific Data:
- **PlatformTypes**: Contains all Platform Types contained in the System.
  - PlatformType: Type of Platform
  - subClassOf_PlatformType: the upper class, this Platform Type is part of.
- **SensorTypes**: Contains all Sensor Types contained in the System.
  - SensorType: Type of Sensor
  - subClassOf_SensorType: the upper class, this Sensor Type is part of.
- **StateTypes**: Contains all State Types in the System that are relevant for explanations, trcking the progression of an event.
  - StateType: Type of State possible in the System 
  - SensorType_possible: Sensor Type, where the Type of State can occur.

Instantiation-specific Data:
- **Platforms**: All instances of Platforms in the System.
  - Platform: Name, ID of the Platform
  - PlatformType: Type of the Platform
  - hostedBy_Platform: The Parent-Platform by which the Platform is hosted
- **Sensors** All instances of Sensors in the System.
  - Sensor: Name, ID of the Sensor
  - SensorType: Type of the Sensor
  - hostedBy_Platform: The Platform the Sensor is hosted by. Each Sensor needs to be hosted by a Platform.
  - observes_ObservableProperty: The Observable Property that is observed by the Sensor.Each Sensor observes an observable Property.
- **StateTypeCausality**: Causal relations between State Types in the System.
  - StateType_cause: State Type on the cause-side of the relation
  - StateType_effect: State Type on the effect-side of the relation
  - causalRelation: type of causal relation (possible types are: causes, enables, prevents)
  - temporalRelation: temporal relation between the states, where the relation can occur (possible relations are: before, overlaps, contains, ...)
  - topologicalRelation: topological relation between the states, where the relation can occur (possible relations are: samePlatform, parentPlatform, siblingPlatform)