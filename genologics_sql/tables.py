from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Boolean, Integer, String, TIMESTAMP

Base = declarative_base()

class Project(Base):
    __tablename__ = 'project'
    projectid =         Column(Integer, primary_key=True)
    name =              Column(String)    
    opendate =          Column(TIMESTAMP) 
    closedate =         Column(TIMESTAMP)
    invoicedate =       Column(TIMESTAMP)
    luid =              Column(String)   
    maximumsampleid =   Column(String)
    ownerid =           Column(Integer) 
    datastoreid =       Column(Integer) 
    isglobal =          Column(Boolean)   
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer) 
    researcherid =      Column(Integer) 
    priority =          Column(Integer)

    def __repr__(self):
        return "<Project(id={}, name={})>".format(self.projectid, self.name)


class Sample(Base):
    __tablename__ = 'sample'
    processid =         Column(Integer, ForeignKey('process.processid'), primary_key=True)
    sampleid =          Column(Integer)    
    name =              Column(String)    
    datereceived =      Column(TIMESTAMP) 
    datecompleted =     Column(TIMESTAMP) 
    maximumanalyteid =  Column(Integer)
    uniqueid =          Column(Integer)
    bisourceid =        Column(Integer)
    projectid =         Column(Integer, ForeignKey('project.projectid'))
    controltypeid =     Column(Integer)

    project = relationship(Project, backref='samples')

    def __repr__(self):
        return "<Sample(id={}, name={})>".format(self.sampleid, self.name)


class ProcessType(Base):
    __tablename__ = 'processtype'
    typeid =            Column(Integer, primary_key=True)
    displayname =       Column(String)
    typename=           Column(String)
    isenabled =         Column(Boolean)
    contextcode =       Column(String)
    isvisible =         Column(Boolean)
    style   =           Column(Integer)
    showinexplorer =    Column(Boolean)
    showinbuttonbar =   Column(Boolean)
    openpostprocess =   Column(Boolean)
    iconconstant =      Column(String)
    outputcontextcode = Column(String)
    useprotocol =       Column(Boolean)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    behaviourname =     Column(String)
    metadata =          Column(String)
    canedit =           Column(Boolean)
    modulename =        Column(String)
    expertname =        Column(String)

    def __repr__(self):
        return "<ProcessType(id={}, name={})>".format(self.typeid, self.typename)

class Process(Base):
    __tablename__ = 'process'
    processid =         Column(Integer, primary_key=True)
    daterun =           Column(TIMESTAMP)    
    luid =              Column(String)    
    isprotocol =        Column(Boolean)    
    protocolnameused =  Column(String)
    programstarted =    Column(Boolean)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    ownerid =           Column(Integer)
    createddate =       Column(TIMESTAMP)    
    lastmodifieddate =  Column(TIMESTAMP)    
    lastmodifiedby =    Column(Integer)
    installationid =    Column(Integer)
    techid =            Column(Integer)
    typeid =            Column(Integer, ForeignKey('processid.typeid'))
    stringparameterid = Column(Integer)
    fileparameterid =   Column(Integer)
    protocolstepid =    Column(Integer)
    workstatus =        Column(String)
    reagentcategoryid = Column(Integer)
    signedbyid =        Column(Integer)
    signedbydate =      Column(TIMESTAMP)
    nextstepslocked =   Column(Boolean)

    type = relationship(ProcessType, backref='processes')

    def __repr__(self):
        return "<Process(id={}, type={})>".format(self.processid, self.typeid)
