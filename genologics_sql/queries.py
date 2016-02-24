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

