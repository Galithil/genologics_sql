import genologics_sql.utils
from genologics_sql.tables import *

def test_connection():
    session=genologics_sql.utils.get_session()
    assert(session is not None)

def test_project_query():
    session=genologics_sql.utils.get_session()
    pj=session.query(Project).limit(1)
    assert(pj is not None)

