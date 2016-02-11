from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP, LargeBinary

#Module used to map the tables from Genologics's Postgres instance

Base = declarative_base()


#Junction tables

artifact_sample_map = Table('artifact_sample_map', Base.metadata,
            Column('artifactid', Integer, ForeignKey('artifact.artifactid')),
                Column('processid', Integer, ForeignKey('sample.processid')))
"""Junction table between artifact and sample"""

artifact_ancestor_map = Table('artifact_ancestor_map', Base.metadata,
            Column('artifactid', Integer, ForeignKey('artifact.artifactid')),
                Column('ancestorartifactid', Integer, ForeignKey('artifact.artifactid')))
"""Junction table between artifact and artifact (as an ancestor)"""


artifact_label_map = Table('artifact_label_map', Base.metadata, 
                    Column('artifactid', Integer, ForeignKey('artifact.artifactid')),
                    Column('labelid', Integer, ForeignKey('reagentlabel.labelid')))
"""Junction table between artifact and reagentlabel)"""

#Standard tables

#udf view has to be before project 
class EntityUdfView(Base):
    """Table used to access project and container udfs

    :arg INTEGER attachtoid: the ID of the entity to attach the row to.
    :arg INTEGER attachtoclassid: the ID of the class of the entity to attach the row to.
    :arg STRING udtname: the name of the User Defined Type.
    :arg STRING udfname: the name of the User Defined Field.
    :arg STRING udttype: the type of the User Defined Type.
    :arg STRING udfvalue: the value of the User Defined Field.
    :arg STRING udfunitlabel: the type of the User Defined Field if preset.


    All of these are mapped as primary keys.
    """
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
    """Table stroting project objects

    :arg INTEGER projectid: the _internal_ project ID. **Primary key.** 
    :arg STRING name: the project name. 
    :arg TIMESTAMP opendate: the opening date of the project as a timestamp. 
    :arg TIMESTAMP closedate: the closing date of the project as a timestamp. 
    :arg TIMESTAMP invoicedate: the invoicing date of the project as a timestamp. 
    :arg STRING luid: the external project id. 
    :arg STRING maximumsampleid: the id of the last sample. usually, nb of samples-1, as it's 0 indexed. 
    :arg INTEGER ownerid: researcherID of the project owner. 
    :arg INTEGER datastoreid: probably used to map the udfs
    :arg INTEGER isglobal: *unkown*
    :arg TIMESTAMP createddate: the creation date of the project as a timestamp. 
    :arg TIMESTAMP lastmodifieddate: the last modification date of the project as a timestamp. 
    :arg INTEGER lastmodifiedby: the id of the last modifier of the project. 
    :arg INTEGER researcherid: the id of the researcher associated to the project. 
    :arg INTEGER priority: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg UDFS udfs: list of project udf rows for the given projectid
    :arg RESEARCHER researcher: direct researcher mapping

    """
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
    researcherid =      Column(Integer, ForeignKey('researcher.researcherid')) 
    priority =          Column(Integer)

    #this is the reason why udfview was declared before project
    udfs = relationship("EntityUdfView", foreign_keys=projectid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Project.projectid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==83)")

    researcher = relationship("Researcher", uselist=False)

    def __repr__(self):
        return "<Project(id={}, name={})>".format(self.projectid, self.name)


class Sample(Base):
    """
    Table mapping the samples

    :arg INTEGER processid: The ID of the process that spawned the sample. Primary key.
    :arg INTEGER sampleid: Internal sample ID.
    :arg STRING name: the sample name.
    :arg TIMESTAMP datereceived: timestamp of the sample import.
    :arg TIMESTAMP datecompleted: timestamp of the project closure / sample completion.
    :arg INTEGER maximumanalyteid: *unknown*
    :arg INTEGER uniqueid: *unknown*. Not unique. 
    :arg INTEGER bisourceid: *unknown*. 
    :arg INTEGER projectid:  projet ID associated to the sample.
    :arg INTEGER controltypeid: *unknown*.

    The following attributes are *not* found in the table, but are available through mapping

    :arg Project project: project object associated to the sample through the projectid foreign key.

    """
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
    """Table mapping the Process Types

    :arg INTEGER typeid: The Process Type ID. Primary Key
    :arg STRING displayname: The name of the process type as shown everywhere.
    :arg STRING typename: The name of the _category_ of the process type.
    :arg BOOLEAN isenabled: Probably related to the tickbox in the Operations interface
    :arg STRING contextcode: The short code (usually 3 letters) that represents the type
    :arg BOOLEAN isvisible: *unknown*
    :arg INTEGER style: *unknown* 
    :arg BOOLEANshowinexplorer: *unknown* 
    :arg BOOLEAN showinbuttonbar *unknown*
    :arg BOOLEAN openpostprocess: *unknown* 
    :arg STRING iconconstant: *unknown*
    :arg STRING outputcontextcode: *unknown*. Apparently, a two-letter code.
    :arg BOOLEAN useprotocol: *unknown* 
    :arg INTEGER ownerid: Researcher ID of the owner of the type. Should correlate to the Researcher table.
    :arg INTEGER datastoreid: likely related to the udf storage 
    :arg BOOLEAN isglobal: *unknown* 
    :arg TIMESTAMP createddate: creation date
    :arg TIMESTAMP lastmodifieddate: timestamp of the last modification 
    :arg INTEGER lastmodifiedby: ID of the last modifier 
    :arg STRING behaviourname: *unknown*
    :arg STRING pmetadata: html string likely containing display data. The actual column name is metadata, but that causes namespace conflicts.
    :arg BOOLEAN canedit: is that type editable
    :arg STRING  modulename: Java module tied to this type 
    :arg STRING  expertname: Java class tied to this type



    """
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

    udfs = relationship("EntityUdfView", foreign_keys=containerid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Container.containerid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==27)")

    def __repr__(self):
        return "<Container(id={}, name={})>".format(self.containerid, self.name)

class ReagentLabel(Base):
    __tablename__ = 'reagentlabel'
    labelid=            Column(Integer, primary_key=True)     
    name =              Column(String)     
    ownerid =           Column(Integer)     
    datastoreid =       Column(Integer)     
    isglobal =          Column(Boolean)     
    createddate =       Column(TIMESTAMP) 
    lastmodifieddate =  Column(TIMESTAMP) 
    lastmodifiedby =    Column(Integer) 

    artifacts = relationship("Artifact", secondary = artifact_label_map, 
                backref='reagentlabels')

    def __repr__(self):
        return "<ReagentLabel(id={}, name={})>".format(self.labelid, self.name)



class Analyte(Base):
    __tablename__ = 'analyte'
    artifactid =        Column(Integer, ForeignKey('artifact.artifactid'), primary_key=True)     
    analyteid =         Column(Integer)
    iscalibrant =       Column(Boolean)
    sequencenumber =    Column(Integer)
    isvisible =         Column(Boolean)

    artifact=relationship("Artifact", uselist=False)

    def __repr__(self):
        return "<Analyte(id={})>".format(self.artifactid)

class ResultFile(Base):
    __tablename__ = 'resultfile'
    artifactid =        Column(Integer, ForeignKey('artifact.artifactid'), primary_key=True)     
    fileid =            Column(Integer)
    type =              Column(String)
    parsestatus =       Column(Integer)
    status =            Column(Integer)
    commandid =         Column(String)
    glsfileid =         Column(Integer)

    artifact=relationship("Artifact", uselist=False)

    def __repr__(self):
        return "<ResultFile(id={})>".format(self.artifactid)

class GlsFile(Base):
    __tablename__ = 'glsfile'
    fileid =            Column(Integer, ForeignKey('resultfile.glsfileid'), primary_key=True)
    server =            Column(String)
    contenturi =        Column(String)
    luid =              Column(String)
    originallocation =  Column(String)
    type =              Column(String)

    file=relationship("ResultFile",uselist=False, backref="glsfile")
    
    def __repr__(self):
        return "<GlsFile(id={})>".format(self.fileid)

class Researcher(Base):
    __tablename__ = 'researcher'
    researcherid =      Column(Integer, primary_key=True)
    roleid =            Column(Integer)
    firstname =         Column(String)
    lastname =          Column(String)
    title =             Column(String)
    initials =          Column(String)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Integer)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    phone =             Column(String)
    email =             Column(String)
    fax =               Column(String)
    addressid =         Column(Integer)
    labid =             Column(Integer) 
    supervisorid =      Column(Integer) 
    isapproved =        Column(Boolean) 
    requestedsupervisorfirstname =  Column(String) 
    requestedsupervisorlastname =   Column(String) 
    requestedusername = Column(String) 
    requestedpassword = Column(String) 
    requestedlabname =  Column(String) 
    avatar =            Column(LargeBinary) 
    avatarcontenttype = Column(String) 

    def __repr__(self):
        return "<Researcher(id={}, name={} {}, initials={})>".format(self.researcherid, self.firstname, self.lastname, self.initials)

class EscalationEvent(Base):
    __tablename__ = 'escalationevent'
    eventid =           Column(Integer, primary_key=True)
    processid =         Column(Integer, ForeignKey('process.processid'))
    originatorid =      Column(Integer)
    reviewerid =        Column(Integer)
    escalationdate  =   Column(TIMESTAMP)
    reviewdate  =       Column(TIMESTAMP)
    escalationcomment = Column(String)
    reviewcomment =     Column(String)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    ownerid =           Column(Integer)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby  =   Column(Integer)

    process=relationship("Process", uselist=False)
    def __repr__(self):
        return "<EscalationEvent(id={}, process={})>".format(self.eventid, self.processid)


class EscalatedSample(Base):
    __tablename__ = 'escalatedsample'
    escalatedsampleid = Column(Integer, primary_key=True)
    escalationeventid = Column(Integer, ForeignKey('escalationevent.eventid'))
    artifactid =        Column(Integer, ForeignKey('artifact.artifactid'))
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby  =   Column(Integer)

    event=relationship("EscalationEvent", backref="escalatedsamples")
    

    def __repr__(self):
        return "<EscalatedSample(id={}, artifact={})>".format(self.escalatedsampleid, self.artifactid)
