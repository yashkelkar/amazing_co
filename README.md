## Amazing Co Employee Structure
#### Problem Statement - 
Model Amazing Co's employee structure in a way that it can be 
1. Persistent
2. List of descendants can be fetched easily 
3. Employee structure can be reorganized 

#### Approach and design decisions - 
Employee stucture can be naturally fit into a tree, as the problem suggests. However persisting the data and traversing through the tree everytime to fetch nodes is not ideal. 
Materialized paths was another approach that was considered as it provides good searching capabilities. However it is not an ideal solution for insert/update kind of operations. 

Hence closure tables was chosen as the final approach which provides good read and write capabilities while still persisting the data. 

Postgres was chosen as the backend to store all  the information. The solution relies on two tables. 

```
Employee Table - Id, Name, Parent, Root, Height

Relationship Table - Ancestor, Descendant
```

Employee table mimics the Node mentioned in the problem statement. Id is the unique identifier for an employee as there might be employees  with the exact same name. 
Relationship table links all the nodes together with the ancestor and descendant relationships.


#### API calls
##### 1. GET /employees/{name}
This API call returns all the direct descendants of the given employee. In case there are multiple employees with the same name then a list of descendant will be returned.
##### 2. GET /employees/{name}/all
This returns all the descendants under that particular employee. 
##### 3. PUT /employees/{name}/{new_parent}
Updates the employee structure. This is achieved in three steps - 
* Update the current employee record in employee table
* Update the corresponding relationship in relationships table
* Update the height of all the descendant employees

The API endpoints can be accessed using curl commands or by visiting the swagger page at `localhost:8000/api/v1/`

#### How to run
The app can be instantiated using the command - 
```
<project-folder> $ gunicorn --workers=4 employee_management.app:app --chdir src --log-file=-
```

The app is also dockerized. Check the Dockerfile. That can be instantiated as -
```
<project-folder> $ docker build -t amazing .
<project-folder> $ docker run -p 8000:8000 amazing
```
I was however not able to setup postgres on docker and connect to it from the other container. I used my local postgres instance during development.
Hence to execute this app you will have to have a postgres instance and will also have to modify the connection string in 
```
src/employee_management/api/v1/model/utils.py
``` 

For convenience the `create_data.sql` can be used to populate the tables. 

The input set provided in the above mentioned script is as follows - 

![Alt text](example.png?raw=true "Sample Input")

 

