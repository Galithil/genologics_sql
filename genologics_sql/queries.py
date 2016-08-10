from genologics_sql.tables import *

from sqlalchemy import text

def get_last_modified_projects(session, interval="2 hours"):
    """gets the project objects last modified in the last <interval>

    :query: select * from project where age(lastmodifieddate)< '1 hour'::interval;

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records

    """
    txt="age(now(),lastmodifieddate)< '{int}'::interval".format(int=interval)
    return session.query(Project).filter(text(txt)).all()

def get_last_modified_project_udfs(session, interval="2 hours"):
    """gets the project objects that have a udf last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records

    """
    query="select pj.* from project pj \
           inner join entityudfstorage eus on pj.projectid = eus.attachtoid \
           where eus.attachtoclassid = 83 and age(now(), eus.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()


def get_last_modified_project_sample_udfs(session, interval="2 hours"):
    """gets the project objects that have sample udfs last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner  join processudfstorage pus on sa.processid=pus.processid \
            where age(now(), pus.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()

def get_last_modified_project_artifacts(session, interval="2 hours"):
    """gets the project objects that have artifacts last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner join artifact_sample_map asm on sa.processid=asm.processid \
            inner join artifact art on asm.artifactid=art.artifactid \
            where age(now(), art.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()

def get_last_modified_project_artifact_udfs(session, interval="2 hours"):
    """gets the project objects that have artifact udfs last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner join artifact_sample_map asm on sa.processid=asm.processid \
            inner join artifactudfstorage aus on asm.artifactid=aus.artifactid \
            where age(now(), aus.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()

def get_last_modified_project_containers(session, interval="2 hours"):
    """gets the project objects that have containers last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner join artifact_sample_map asm on sa.processid=asm.processid \
            inner join containerplacement cpl on asm.artifactid=cpl.processartifactid \
            inner join container ct on cpl.containerid=ct.containerid \
            where age(ct.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()

def get_last_modified_project_processes(session, interval="2 hours"):
    """gets the project objects that have containers last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner join artifact_sample_map asm on sa.processid=asm.processid \
            inner join processiotracker pit on asm.artifactid=pit.inputartifactid \
            inner join process pro on pit.processid=pro.processid \
            where age(now(), pro.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()

def get_last_modified_project_process_udfs(session, interval="2 hours"):
    """gets the project objects that have containers last modified in the last <interval>

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    query= "select distinct pj.* from project pj \
            inner join sample sa on sa.projectid=pj.projectid \
            inner join artifact_sample_map asm on sa.processid=asm.processid \
            inner join processiotracker pit on asm.artifactid=pit.inputartifactid \
            inner join process pro on pit.processid=pro.processid \
            inner join processudfstorage pus on pro.processid=pus.processid \
            where age(now(), pus.lastmodifieddate) < '{int}'::interval;".format(int=interval)
    return session.query(Project).from_statement(text(query)).all()


def get_last_modified_projectids(session, interval="2 hours"):
    """gets all the projectids for which any part has been modified in the last interval

    :param session: the current SQLAlchemy session to the database
    :param interval: str Postgres-compliant time string
    :returns: List of Project records
    """
    projectids=set()
    for project in get_last_modified_projects(session, interval):
        projectids.add(project.luid)

    for project in get_last_modified_project_udfs(session, interval):
        projectids.add(project.luid)

    for project in get_last_modified_project_sample_udfs(session, interval):
        projectids.add(project.luid)

    for project in get_last_modified_project_containers(session, interval):
        projectids.add(project.luid)

    for project in get_last_modified_project_processes(session, interval):
        projectids.add(project.luid)

    for project in get_last_modified_project_process_udfs(session, interval):
        projectids.add(project.luid)

    return projectids


def get_last_modified_processes(session, ptypes, interval="24 hours"):
    """gets all the processes of the given <type> that have been modified
    or have a udf modified in the last <interval>

    :param session: the current SQLAlchemy session to the db
    :param ptypes: the LIST of process type ids to be returned
    :param interval: the postgres compliant interval of time to search processes in.

    """
    query= "select distinct pro.* from process pro \
            inner join processudfstorage pus on pro.processid=pus.processid \
            where (pro.typeid in ({typelist}) \
            and age(now(), pus.lastmodifieddate) < '{int}'::interval) \
            or \
            (age(now(), pro.lastmodifieddate) < '{int}'::interval \
            and pro.typeid in ({typelist}));".format(int=interval, typelist=",".join([str(x) for x in ptypes]))
    return session.query(Process).from_statement(text(query)).all()

def get_processes_in_history(session, parent_process, ptypes):
    """returns wll the processes that are found in the history of parent_process 
    AND are of type ptypes

    :param session: the current SQLAlchemy session to the db
    :param parent_process: the id of the parent_process
    :param ptypes: the LIST of process type ids to be returned

    """

    query="select distinct pro.* from process pro \
            inner join processiotracker pio on pio.processid=pro.processid \
            inner join outputmapping om on om.trackerid=pio.trackerid \
            inner join artifact_ancestor_map aam on pio.inputartifactid=aam.ancestorartifactid\
            inner join processiotracker pio2 on pio2.inputartifactid=aam.artifactid \
            inner join process pro2 on pro2.processid=pio2.processid \
            where pro2.processid={parent} and pro.typeid in ({typelist});".format(parent=parent_process, typelist=",".join([str(x) for x in ptypes]))

    return session.query(Process).from_statement(text(query)).all()

def get_children_processes(session, parent_process, ptypes):
    """returns wll the processes that are found in the children of parent_process 
    AND are of type ptypes

    :param session: the current SQLAlchemy session to the db
    :param parent_process: the id of the parent_process
    :param ptypes: the LIST of process type ids to be returned

    """

    query="select distinct pro.* from process pro \
            inner join processiotracker pio on pio.processid=pro.processid \
            inner join outputmapping om on om.trackerid=pio.trackerid \
            inner join artifact_ancestor_map aam on om.outputartifactid=aam.artifactid\
            inner join processiotracker pio2 on pio2.inputartifactid=aam.ancestorartifactid \
            inner join process pro2 on pro2.processid=pio2.processid \
            where pro2.processid={parent} and pro.typeid in ({typelist});".format(parent=parent_process, typelist=",".join([str(x) for x in ptypes]))

    return session.query(Process).from_statement(text(query)).all()
