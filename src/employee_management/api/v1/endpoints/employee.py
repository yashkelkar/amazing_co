import structlog
from queue import Queue
import contextlib
from psycopg2.extras import RealDictCursor
from flask_restplus import Resource
from employee_management.api.restplus import api
from employee_management.api.v1.model.utils import db_connection, update_descendant_height, root_update, normal_update

log = structlog.getLogger(__name__)

ns = api.namespace('employees', description='Employee related operations')


@contextlib.contextmanager
def use_psql_connection():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    yield cur
    conn.commit()
    conn.close()


@ns.route('/<string:name>')
class EmployeeGetByName(Resource):
    @api.doc(params={'name': 'Employee name'})
    @api.response('Direct descendants of given employee(s)', 201)
    @api.response('No such employee exists', 404)
    def get(self, name):
        """
        Returns the direct descendants of the given employee(s)
        """
        with use_psql_connection() as cur:
            # check if employee name is unique or not
            query = "select id from employee where name='{0}'".format(name)
            log.info("Executing query: " + query)
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                return {"Error": "No such employee exists"}, 404

            # Possible to have more than one employee with same name
            descendants = []
            for single in results:
                query = "select * from employee where id in (select descendant from relationship where ancestor='{0}')" \
                    .format(single['id'])
                log.info("Executing query: " + query)
                cur.execute(query)
                new_results = cur.fetchall()
                descendants.append(new_results)
        return descendants, 201


@ns.route("/<string:name>/all")
class EmployeeGetAllByName(Resource):
    @api.doc(params={'name': 'Employee name'})
    @api.response('All descendants of given employee(s)', 201)
    @api.response('No such employee exists', 404)
    def get(self, name):
        """
        Returns all the employees under the given employee(s)
        """

        with use_psql_connection() as cur:
            # check if employee name is exists or not
            query = "select id from employee where name='{0}'".format(name)
            log.info("Executing query: " + query)
            cur.execute(query)
            results = cur.fetchall()

            if len(results) == 0:
                return {"Error": "No such employee exists"}, 404
            descendants = []

            # BFS approach to traverse all descendants
            q = Queue()
            [q.put(i['id']) for i in results]
            while not q.empty():
                query = "select * from employee where id in (select descendant from relationship where ancestor='{0}')" \
                    .format(q.get())
                log.info("Executing query: " + query)
                cur.execute(query)
                new_results = cur.fetchall()
                if len(new_results) > 0:
                    descendants.append(new_results)
                [q.put(i['id']) for i in new_results]
        return descendants, 201


@ns.route("/<string:name>/<string:new_parent>/")
class EmployeeUpdateParent(Resource):
    @api.doc(params={'name': 'Employee name'})
    @api.doc(params={'new_parent': 'New parent employee name'})
    @api.response('Employee relationship updated', 204)
    @api.response('Either employee or new parent not found', 404)
    @api.response('More than one employee or new parent with the same name found', 409)
    def put(self, name, new_parent):
        """
        Updates the employee structure by moving employee and descendants under the new parent
        """
        with use_psql_connection() as cur:
            # check if employee and new parent exist
            query = "select id from employee where name='{0}'".format(name)
            log.info("Executing query: " + query)
            cur.execute(query)
            employee_id = cur.fetchall()
            query = "select id from employee where name='{0}'".format(new_parent)
            log.info("Executing query: " + query)
            cur.execute(query)
            new_parent_id = cur.fetchall()

            if len(employee_id) == 0 or len(new_parent_id) == 0:
                return {"Error": "Either employee or new parent not found"}, 404

            # Possible to have employees with same name. Ideally we should have an API call that can address this
            if len(employee_id) > 1 or len(new_parent_id) > 1:
                return {"Error": "More than one employee or new parent with the same name found"}, 409

            employee_id = employee_id[0]['id']
            new_parent_id = new_parent_id[0]['id']

            # Check if employee is root
            print(str(employee_id))
            query = "select * from relationship where descendant='{0}'".format(employee_id)
            log.info("Executing query: " + query)
            cur.execute(query)
            employee_parent = cur.fetchall()
            if len(employee_parent) == 0:
                root_update(employee=name, employee_id=employee_id, new_parent=new_parent,
                            new_parent_id=new_parent_id, cur=cur)
            else:
                log.info(employee_id)
                normal_update(employee=name, employee_id=employee_id, new_parent=new_parent,
                              new_parent_id=new_parent_id, cur=cur)

        return 204


"""    
Assuming that if the node changes parent, all the descendants of that node also move
"""
