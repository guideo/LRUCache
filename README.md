# guilherme_deo_ormuco

This is a collection of solutions to the Ormuco challenges:
1. **Question A:** Finding if lines intersect;
1. **Question B:** Checking one version string against another;
1. **Question C:** Geo Distributed LRU cache with time expiration;

## Installation

I've tried my best to use only Python basic libraries, and as far as I know I've achieved it on a Windows Installation, so there is no need to '*pip install*' anything at this moment.  

Simply clone the repo and run the desired solution.

## Usage

### Question A
In order to run Question A, simply call it in the prompt as:

```bash
guilherme_deo_question_a.py line1_start line1_end line2_start line2_end
```
* **line1_start**: Integer for the X position where line 1 starts
* **line1_end**: Integer for the X position where line 1 ends
* **line2_start**: Integer for the X position where line 2 starts
* **line2_end**: Integer for the X position where line 2 ends

The **output** will be either **True** (if lines overlap) or **False** (if they do not).

### Question B
In order to run Question B, simply call it in the prompt as:

```bash
guilherme_deo_question_b.py version_1 version_2
```
* **version_1**: String representing first version to compare
* **version_2**: String representing second version to compare

The **output** will be a string stating if version_1 is either **Greater**, **Smaller** or **Equal** to version_2.  

**Note:** *This function is considering the same rules as Python for checking if bigger or small, which means that small case letters are bigger than upper case, and that numbers are smaller than letters.*  
```python
'z' > 'a' > 'Z' > 'A' > '1' - 0-9<A-Z<a-z
```
*Also, the characters `. , - _` are considered as version separators*

### Question C
For question C, we have separated modules for each Cache element:
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
* **replicate**: **VERY IMPORTANT** - I might have misunderstood the requirements for this question, and implemented the Caches in a way where all data in all nodes will be the same (which seemed to be harder). This means that when a Node is hit, it will tell the MASTER to update **ALL** other nodes to reflect the same info. If this is the desired behavior, set this to **TRUE**, otherwise set to **FALSE** and the Nodes will operate fully separated. If set to True, each Node will have an additional port being used to listen to updates from the MASTER.

*I plan to add a video showcasing the solution, which should be done soon (tomorrow).*  

A full explanation of all classes is outside the scope of this README, but one last point that I would like to mention is that the solution uses both a *Dict* and a *DoubleLinkedList* so that each operation on the Cache will have **O(1)** time complexity.
