import structlog
from queue import Queue
import contextlib
from psycopg2.extras import RealDictCursor
from flask_restplus import Resource
from employee_management.api.restplus import api
from employee_management.api.v1.model.utils import db_connection, update_descendant_height

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
            cur.execute(query)
            log.info("Executed query: " + query)
            results = cur.fetchall()
            if len(results) == 0:
                return {"Error": "No such employee exists"}, 404

            # Possible to have more than one employee with same name
            descendants = []
            for single in results:
                query = "select * from employee where id in (select descendant from relationship where ancestor='{0}')" \
                    .format(single['id'])
                cur.execute(query)
                log.info("Executed query: " + query)
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
            cur.execute(query)
            log.info("Executed query: " + query)
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
                cur.execute(query)
                log.info("Executed query: " + query)
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
            cur.execute(query)
            log.info("Executed query: " + query)
            employee_id = cur.fetchall()
            query = "select id from employee where name='{0}'".format(new_parent)
            cur.execute(query)
            log.info("Executed query: " + query)
            new_parent_id = cur.fetchall()

            if len(employee_id) == 0 or len(new_parent_id) == 0:
                return {"Error": "Either employee or new parent not found"}, 404

            # Possible to have employees with same name. Ideally we should have an API call that can address this
            if len(employee_id) > 1 or len(new_parent_id) > 1:
                return {"Error": "More than one employee or new parent with the same name found"}, 409

            # Update the relationship table
            query = "update relationship set ancestor='{0}' where descendant='{1}'".format(new_parent_id[0]['id'],
                                                                                           employee_id[0]['id'])
            cur.execute(query)
            log.info("Executed query: " + query)

            # Update employee table
            query = "select height from employee where name='{0}'".format(new_parent)
            cur.execute(query)
            log.info("Executed query: " + query)
            new_parent_height = cur.fetchall()[0]['height']
            query = "update employee set height={0}, parent='{1}' where name='{2}'".format(new_parent_height+1,
                                                                                           new_parent, name)
            cur.execute(query)
            log.info("Executed query: " + query)
            update_descendant_height(parent_id=employee_id[0]['id'], height=new_parent_height+1, cur=cur)
        return 204


"""    
Assuming that if the node changes parent, all the descendants of that node also move
"""
