import yaml
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from genologics_sql.tables import Base

def get_configuration():
    for fn in [os.path.expanduser('~/.genosqlrc.yaml'), '.genosqlrc.yaml']:
        if os.path.exists(fn):
            with open(fn) as f :
                return yaml.load(f)
    raise Exception("Cannot find a valid configuration file. Please read the README.md.")

def get_engine():
    uri=None
    try:
        uri="postgresql://{user}:{passw}@{url}/{db}".format(user=CONF['username'], passw=CONF.get('password', ''), url=CONF['url'], db=CONF['db'])
    except KeyError as e:
        raise Exception("The configuration file seems to be missing a required parameter. Please read the README.md. Missing key : {}".format(e.message))
    return create_engine(uri)

def get_session():
    engine=get_engine()
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


CONF=get_configuration()
