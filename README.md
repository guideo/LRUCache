# Geo Distributed LRU Cache with Time Expiration

## Requirements

Python version 3 (developed using 3.7.3)

## Installation

I've tried my best to use only Python basic libraries, and as far as I know I've achieved it on a Windows Installation, so there is no need to '*pip install*' anything at this moment.  

Simply clone the repo and run the desired solution.

## Usage

We have separated modules for each Cache element:
1. **Master:** The master is responsible for accessing the DB, retrieving a value from it and sending it over to the nodes. At least one master should receive the requests from a node.  
To start a master, run the following code in a terminal:
```bash
LRU_master.py address port
```
* **address**: The address which the master will listen to;
* **port**: The port which the master will listen to.  

As an example, we can call it like `LRU_master.py localhost 8740`

2. **Node:** The node is responsible for receiving requests from clients, and redirecting it to a Master. In a production environment, we should use **Load Balancers** for directing a Node to the best Master, but in this case, I am passing the selected master info as parameters:
```bash
LRU_node.py address port master_address master_port
```
* **address**: The address which the Node will listen to;
* **port**: The port which the Node will listen to;
* **master_address**: The address of the MASTER which this node will contact;
* **master_port**: The port of the MASTER which this node will contact.  

As an example, using the previous started MASTER, we can call it like  
`LRU_node.py localhost 8730 localhost 8740`  
**Important Note**: A Node might use two ports (the second one is incremented by 1) if the **replicate** value is set to True on the *LRU.config* file (explained below).

3. **Client:** The client should only be concerned about requesting data and receiving an answer. Due to this, the client code is really simple, and we can call a client test execution as:
```bash
send_data.py
```
This client is hard-coded to connect to localhost:8730 (the previously created node).  
For a general use-case, there is the class **LRU_client.py**. We can easily use this for integration with python scripts doing:
```python
from LRU_client import CacheClient
client = CacheClient('localhost', 8730)
client.request('Pam')
```
The return of `client.request` is a list containing the found values  
Example: `[(5, 'Pam', 'pampam@email.com', '999-9999')]`  
Again, in a production environment, we should have **Load Balancers** between Clients and Nodes.


## Additional informations regarding the Cache implementation
There is a config file (*LRU.config*) responsible for a set of parameters for the Cache. They are:
```json
{
    "max_size_of_cache": 3,
    "max_size_of_data": 1024,
    "cache_expiration_time_seconds": 60,
    "db": "ormuco_db.sqlite",
    "hard_expire": false,
    "replicate": true
}
```
Some parameters are self explanatory, but others are not:
* **db**: The database which the MASTER will access must be in the same place as the code;
* **hard_expire**: This configuration sets if we should invalidate the data after the expiration time, even if the Cache had this data requested recently. This helps with issues regarding Distributed Cache Invalidation.
* **replicate**: **VERY IMPORTANT** - I've implemented the Caches in a way where all data in all nodes will be the same (which seemed to be harder). This means that when a Node is hit, it will tell the MASTER to update **ALL** other nodes to reflect the same info. If this is the desired behavior, set this to **TRUE**, otherwise set to **FALSE** and the Nodes will operate fully separated. If set to True, each Node will have an additional port being used to listen to updates from the MASTER.

A full explanation of all classes is outside the scope of this README, but one last point that I would like to mention is that the solution uses both a *Dict* and a *DoubleLinkedList* so that each operation on the Cache will have **O(1)** time complexity.

### Missing Features

* Replication of the Cache between MASTERs. If the **replicate** option is set to True, we should have the same Cache available on all Nodes and Masters, but at this moment, Masters are not updating each other. 
