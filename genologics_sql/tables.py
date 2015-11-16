from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP

Base = declarative_base()

#Junction tables first

artifact_sample_map = Table('artifact_sample_map', Base.metadata,
            Column('artifactid', Integer, ForeignKey('artifact.artifactid')),
                Column('processid', Integer, ForeignKey('sample.processid')))

artifact_ancestor_map = Table('artifact_ancestor_map', Base.metadata,
            Column('artifactid', Integer, ForeignKey('artifact.artifactid')),
                Column('ancestorartifactid', Integer, ForeignKey('artifact.artifactid')))


#real tables next

#udf view has to be before project for reasons
class EntityUdfView(Base):
    __tablename__ = 'entity_udf_view'
    attachtoid =        Column(Integer, primary_key=True)     
    attachtoclassid =   Column(Integer, primary_key=True)
    udtname =           Column(String, primary_key=True)
    udfname =           Column(String, primary_key=True) 
    udftype =           Column(String, primary_key=True)
    udfvalue =          Column(String, primary_key=True)
    udfunitlabel =      Column(String, primary_key=True)


    def __repr__(self):
        return "<EntityUdf(id={}, class={}, key={}, value={})>".format(self.attachtoid, self.attachtoclassid, self.udfname, self.udfvalue)

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

    #this is the reason why udfview was declared before project
    udfs = relationship("EntityUdfView", foreign_keys=projectid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Project.projectid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==83)")

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
    pmetadata =         Column('metadata', String)
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
    typeid =            Column(Integer, ForeignKey('processtype.typeid'))
    stringparameterid = Column(Integer)
    fileparameterid =   Column(Integer)
    protocolstepid =    Column(Integer)
    workstatus =        Column(String)
    reagentcategoryid = Column(Integer)
    signedbyid =        Column(Integer)
    signeddate =        Column(TIMESTAMP)
    nextstepslocked =   Column(Boolean)

    type = relationship(ProcessType, backref='processes')
    udfs = relationship("ProcessUdfView")

    def __repr__(self):
        return "<Process(id={}, type={})>".format(self.processid, self.typeid)


class Artifact(Base):
    __tablename__ = 'artifact'
    artifactid =        Column(Integer, primary_key=True)
    name =              Column(String)
    luid  =             Column(String)
    volume =            Column(Float)
    concentration =     Column(Float)
    origvolume =        Column(Float)
    origconcentration = Column(Float)
    datastoreid =       Column(Integer)
    isworking =         Column(Boolean)
    isoriginal =        Column(String)
    isglobal =          Column(String)
    isgenealogyartifact=Column(String)
    ownerid =           Column(String)
    createddate =       Column(String)
    lastmodifieddate =  Column(String)
    lastmodifiedby =    Column(String)
    artifacttypeid =    Column(String)
    processoutputtypeid=Column(String)
    currentstateid =    Column(String)
    originalstateid =   Column(String)
    compoundartifactid= Column(String)
    outputindex =       Column(String)

    samples = relationship("Sample", secondary = artifact_sample_map, backref="artifacts")
    ancestors = relationship("Artifact", secondary = artifact_ancestor_map, 
                primaryjoin=artifactid==artifact_ancestor_map.c.artifactid, 
                secondaryjoin=artifactid==artifact_ancestor_map.c.ancestorartifactid)
    udfs = relationship("ArtifactUdfView")
    containerplacement = relationship('ContainerPlacement', uselist=False, backref='artifact')
    def __repr__(self):
        return "<Artifact(id={}, name={})>".format(self.artifactid, self.name)

class ArtifactUdfView(Base):
    __tablename__ = 'artifact_udf_view'
    artifactid =        Column(Integer, ForeignKey('artifact.artifactid') , primary_key=True)     
    udtname =           Column(String, primary_key=True)
    udfname =           Column(String, primary_key=True) 
    udftype =           Column(String, primary_key=True)
    udfvalue =          Column(String, primary_key=True)
    udfunitlabel =      Column(String, primary_key=True)
    def __repr__(self):
        return "<ArtifactUdf(id={}, key={}, value={})>".format(self.artifactid, self.udfname, self.udfvalue)

class ProcessUdfView(Base):
    __tablename__ = 'process_udf_view'
    processid =         Column(Integer, ForeignKey('process.processid') , primary_key=True)     
    typeid =            Column(Integer, ForeignKey('processtype.typeid'), primary_key=True)
    udtname =           Column(String, primary_key=True)
    udfname =           Column(String, primary_key=True) 
    udftype =           Column(String, primary_key=True)
    udfvalue =          Column(String, primary_key=True)
    udfunitlabel =      Column(String, primary_key=True)
    def __repr__(self):
        return "<ProcessUdf(id={}, key={}, value={})>".format(self.processid, self.udfname, self.udfvalue)


class ContainerPlacement(Base):
    __tablename__ = 'containerplacement'
    placementid =       Column(Integer, primary_key=True)     
    containerid =       Column(Integer, ForeignKey('container.containerid'), primary_key=True)
    wellxposition =     Column(Integer)
    wellyposition =     Column(Integer)
    dateplaced =        Column(TIMESTAMP)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    reagentid =         Column(Integer)
    processartifactid = Column(Integer, ForeignKey('artifact.artifactid'))

    container=relationship('Container', uselist=False)

    def __repr__(self):
        return "<ContainerPlacement(id={}, pos={}:{}, cont={}, art={})>".format(self.placementid, self.wellxposition, self.wellyposition, self.containerid, self.processartifactid)


class Container(Base):
    __tablename__ = 'container'
    containerid =       Column(Integer, primary_key=True)     
    subtype =           Column(String)     
    luid =              Column(String)     
    isvisible =         Column(Boolean)     
    name =              Column(String)     
    ownerid =           Column(Integer)     
    datastoreid =       Column(Integer)     
    isglobal =          Column(Boolean)     
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    stateid =           Column(Integer)     
    typeid =            Column(Integer)     
    lotnumber =         Column(String)
    expirydate =        Column(TIMESTAMP)



    def __repr__(self):
        return "<Container(id={}, name={})>".format(self.containerid, self.name)
