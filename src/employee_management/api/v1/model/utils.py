import psycopg2
import structlog
from psycopg2.extras import RealDictCursor

log = structlog.getLogger(__name__)


def db_connection():
    """Connects to the specific database."""
    # conn_string = 'postgres://yashkelkar@localhost:5432/amazing_co'
    conn_string = '<conn_string>'
    conn = psycopg2.connect(conn_string)
    return conn


def update_descendant_height(parent_id, height, cur):
    query = "select descendant from relationship where ancestor='{0}'".format(parent_id)
    cur.execute(query)
    descendant_ids = cur.fetchall()
    print(str(descendant_ids))
    for each_descendant in descendant_ids:
        query = "update employee set height={0} where id='{1}'".format(height+1, each_descendant['descendant'])
        print(query)
        cur.execute(query)
        update_descendant_height(each_descendant['descendant'], height+1, cur)
