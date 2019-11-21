import psycopg2
import structlog
from queue import Queue


log = structlog.getLogger(__name__)


def db_connection():
    """Connects to the specific database."""
    # conn_string = 'postgres://yashkelkar@localhost:5432/amazing_co'
    conn_string = '<conn_string>'
    conn = psycopg2.connect(conn_string)
    return conn


def update_descendant_height(parent_id, height, cur):
    query = "select descendant from relationship where ancestor='{0}'".format(parent_id)
    log.info("Executing query: " + query)
    cur.execute(query)
    descendant_ids = cur.fetchall()
    for each_descendant in descendant_ids:
        query = "update employee set height={0} where id='{1}'".format(height+1, each_descendant['descendant'])
        log.info("Executing query: " + query)
        cur.execute(query)
        update_descendant_height(each_descendant['descendant'], height+1, cur)


def root_update(employee, employee_id, new_parent, new_parent_id, cur):
    # set parent to NULL for new parent and height to 0 in employee table
    query = "update employee set parent=NULL, height=0 where id='{0}'".format(new_parent_id)
    log.info("Executing query: " + query)
    cur.execute(query)

    # update relationship table. New parent cannot be a descendant
    query = "delete from relationship where descendant='{0}'".format(new_parent_id)
    log.info("Executing query: " + query)
    cur.execute(query)

    # make old root child of new root
    query = "insert into relationship (ancestor, descendant) values ('{0}', '{1}')".format(new_parent_id, employee_id)
    log.info("Executing query: " + query)
    cur.execute(query)
    query = "update employee set parent='{0}' where id='{1}'"\
        .format(new_parent, employee_id)
    log.info("Executing query: " + query)
    cur.execute(query)

    # Update all rows with new root
    query = "update employee set root='{0}'".format(new_parent)
    log.info("Executing query: " + query)
    cur.execute(query)

    # Update heights of the rest of the tree
    update_descendant_height(parent_id=new_parent_id, height=0, cur=cur)


def normal_update(employee, employee_id, new_parent, new_parent_id, cur):
    # check if new parent is a child of employee
    q = Queue()
    q.put(employee_id)
    is_descendant = False
    while not q.empty():
        query = "select id from employee where id in (select descendant from relationship where ancestor='{0}')" \
            .format(q.get())
        log.info("Executing query: " + query)
        cur.execute(query)
        new_results = cur.fetchall()
        for descendant_id in new_results:
            if descendant_id['id'] == new_parent_id:
                is_descendant = True
                break
            q.put(descendant_id['id'])

    if is_descendant:
        # new parent is descendant of employee. Hence blindly changing relationship will create a loop
        # We can avoid this by bringing up the new parent and moving down the employee

        # get employee parent id
        query = "select * from employee where id=(select ancestor from relationship where descendant='{0}')"\
            .format(employee_id)
        log.info("Executing query: " + query)
        cur.execute(query)
        employee_parent = cur.fetchall()[0]

        # update employee table
        query = "update employee set parent='{0}', height='{1}' where id='{2}'"\
            .format(employee_parent['name'], employee_parent['height']+1, new_parent_id)
        log.info("Executing query: " + query)
        cur.execute(query)

        query = "update employee set parent='{0}' where id='{1}'"\
            .format(new_parent, employee_id)
        log.info("Executing query: " + query)
        cur.execute(query)

        # update relationship table
        query = "update relationship set ancestor='{0}' where descendant='{1}'"\
            .format(employee_parent['id'], new_parent_id)
        log.info("Executing query: " + query)
        cur.execute(query)

        query = "update relationship set ancestor='{0}' where descendant='{1}'" \
            .format(new_parent_id, employee_id)
        log.info("Executing query: " + query)
        cur.execute(query)

        # update height of rest of subtree
        update_descendant_height(parent_id=employee_parent['id'], height=employee_parent['height'], cur=cur)
    else:
        # get height of new parent
        query = "select height from employee where id='{0}'".format(new_parent_id)
        log.info("Executing query: " + query)
        cur.execute(query)
        new_parent_height = cur.fetchall()[0]['height']

        # alter relationship table, employee to new parent
        query = "update employee set parent='{0}', height='{1}' where id='{2}'"\
            .format(new_parent, new_parent_height+1, employee_id)
        log.info("Executing query: " + query)
        cur.execute(query)
        query = "update relationship set ancestor='{0}' where descendant='{1}'".format(new_parent_id, employee_id)
        log.info("Executing query: " + query)
        cur.execute(query)

        # update height of rest of the sub tree
        update_descendant_height(parent_id=employee_id, height=new_parent_height+1, cur=cur)



