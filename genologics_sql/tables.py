from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP, LargeBinary, sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

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
    """Table storing project objects

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
    #the entityid of the Projects is 83
    udfs = relationship("EntityUdfView", foreign_keys=projectid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Project.projectid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==83)")

    researcher = relationship("Researcher", uselist=False)

    @hybrid_property
    def udf_dict(self):
        udf_dict={}
        for udfrow in self.udfs:
            if udfrow.udfvalue:
                if udfrow.udftype == "Numeric":
                    udf_dict[udfrow.udfname]=float(udfrow.udfvalue)
                elif udfrow.udftype == "Boolean":
                    udf_dict[udfrow.udfname]=(udfrow.udfvalue=="True")
                else:
                    udf_dict[udfrow.udfname]=udfrow.udfvalue

        return udf_dict

    def __repr__(self):
        return "<Project(id={}, name={})>".format(self.projectid, self.name)

class SampleUdfView(Base):
    """Table used to access project and container udfs

    :arg INTEGER sampleid: the ID of the sample to attach the row to.
    :arg STRING udtname: the name of the User Defined Type.
    :arg STRING udfname: the name of the User Defined Field.
    :arg STRING udttype: the type of the User Defined Type.
    :arg STRING udfvalue: the value of the User Defined Field.
    :arg STRING udfunitlabel: the type of the User Defined Field if preset.


    All of these are mapped as primary keys.
    """
    __tablename__ = 'sample_udf_view'
    sampleid =          Column(Integer, ForeignKey('sample.sampleid'), primary_key=True)     
    udtname =           Column(String, primary_key=True)
    udfname =           Column(String, primary_key=True) 
    udftype =           Column(String, primary_key=True)
    udfvalue =          Column(String, primary_key=True)
    udfunitlabel =      Column(String, primary_key=True)


    def __repr__(self):
        return "<SampleUdf(id={}, key={}, value={})>".format(self.sampleid, self.udfname, self.udfvalue)

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
    udfs = relationship('SampleUdfView')
    submitter = relationship("Researcher",
            secondary="join(Process, Principals, Process.techid==Principals.principalid)",
            primaryjoin="Sample.processid==Process.processid",
            secondaryjoin="Researcher.researcherid==Principals.researcherid",
            uselist=False)
    artifact = relationship('Artifact',
            secondary=artifact_sample_map,
            secondaryjoin="and_(artifact_sample_map.c.artifactid == Artifact.artifactid, Artifact.isoriginal==True)",
            uselist=False
            )

    @hybrid_property
    def udf_dict(self):
        udf_dict={}
        for udfrow in self.udfs:
            if udfrow.udfvalue:
                if udfrow.udftype == "Numeric":
                    udf_dict[udfrow.udfname]=float(udfrow.udfvalue)
                elif udfrow.udftype == "Boolean":
                    udf_dict[udfrow.udfname]=(udfrow.udfvalue=="True")
                else:
                    udf_dict[udfrow.udfname]=udfrow.udfvalue
                
        return udf_dict

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
    :arg BOOLEAN showinbuttonbar: *unknown*
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
    :arg STRING modulename: Java module tied to this type 
    :arg STRING expertname: Java class tied to this type

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
    """Table mapping process objects

    :arg INTEGER processid: the (short) process ID. **Primary key.** 
    :arg TIMESTAMP daterun: date where the process was closed 
    :arg STRING luid: the (long) process id
    :arg BOOLEAN isprotocol: *unknown*
    :arg STRING protocolnameused: *unknown* 
    :arg BOOLEAN programstarted: probably stores EPP status
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg INTEGER ownerid: researcher id of the process creator
    :arg TIMESTAMP createddate: date of creation of the process
    :arg TIMESTAMP lastmodifieddate: date of last modification
    :arg INTEGER lastmodifiedby: researcher id of the last modifier
    :arg INTEGER installationid: *unknown*
    :arg INTEGER techid: *unknown*
    :arg INTEGER typeid: id of the process type associated
    :arg INTEGER stringparameterid: parameterid from processparameter. Contains information about EPPs.
    :arg INTEGER fileparameterid: *unknown* often empty
    :arg INTEGER protocolstepid: id of the associated protocol step
    :arg STRING workstatus: status of the process. values :  COMPLETE, RECORD_DETAILS, STARTED, UNDER_REVIEW, MOVE_SAMPLES_ON
    :arg INTEGER reagentcategoryid: id of the assocated reagent category
    :arg INTEGER signedbyid: *unknown*
    :arg TIMESTAMP signeddate: *unknown*
    :arg BOOLEAN nextstepslocked: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg ProcessType type: ProcessType row associated with the Process row.
    :arg ProcessUdfView udfs: ProcessUdfView row associated with the Process row.

    """
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
    techid =            Column(Integer, ForeignKey('principals.principalid'))
    typeid =            Column(Integer, ForeignKey('processtype.typeid'))
    stringparameterid = Column(Integer)
    fileparameterid =   Column(Integer)
    protocolstepid =    Column(Integer)
    workstatus =        Column(String)
    reagentcategoryid = Column(Integer)
    signedbyid =        Column(Integer)
    signeddate =        Column(TIMESTAMP)
    nextstepslocked =   Column(Boolean)

    type = relationship("ProcessType", backref='processes')
    udfs = relationship("ProcessUdfView")
    technician = relationship("Principals")

    def __repr__(self):
        return "<Process(id={}, type={})>".format(self.processid, self.typeid)

    @hybrid_property
    def udf_dict(self):
        udf_dict={}
        for udfrow in self.udfs:
            if udfrow.udfvalue:
                if udfrow.udftype == "Numeric":
                    udf_dict[udfrow.udfname]=float(udfrow.udfvalue)
                elif udfrow.udftype == "Boolean":
                    udf_dict[udfrow.udfname]=(udfrow.udfvalue=="True")
                else:
                    udf_dict[udfrow.udfname]=udfrow.udfvalue
                
        return udf_dict

class Artifact(Base):
    """Table mapping artifact objects

    :arg INTEGER artifactid: the (short) artifact ID. **Primary key.** 
    :arg STRING name: the artifact given name
    :arg STRING luid: the (long) artifact id
    :arg FLOAT concentration: *unknown*
    :arg FLOAT origvolume: *unknown*
    :arg FLOAT origconcentration: *unknown*
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isworking: API working flag
    :arg BOOLEAN isoriginal: *unknown*
    :arg BOOLEAN isglobal: *unknown*
    :arg BOOLEAN isgenealogyartifact: *unknown*
    :arg INTEGER ownerid: researcher id of the artifact creator
    :arg TIMESTAMP createddate: date of creation of the artifact
    :arg TIMESTAMP lastmodifieddate: date of last modification
    :arg INTEGER lastmodifiedby: researcher id of the last modifier
    :arg INTEGER artifacttypeid: *unknown*
    :arg INTEGER processoutputid: *unknown*
    :arg INTEGER currentstateid: *unknown*
    :arg INTEGER originalstateid: *unknown*
    :arg INTEGER compoundartifactid: *unknown*
    :arg INTEGER outputindex: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact ancestors: Artifact rows associated with this row through artifact_ancestor_map.
    :arg ContainerPlacement containerplacement: ContainerPlacement row associated the Artifact row.
    :arg String qc_flag: API string of the latest qc_flag of the artifact.
    :arg ReagentLabel reagentlabels: reagentlabel rows associated with the Artifact row.
    :arg Sample samples: Sample rows associated with the Artifact row.
    :arg ArtifactState states: ArtifactState rows associated with the Artifact row.
    :arg ArtifactUdfView udfs: ArtifactUdfView row associated the Artifact row.
    :arg dict udf_dict: A dictionnary of udfs with correct types (Strings, Floats and Booleans).

    """
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
    isoriginal =        Column(Boolean)
    isglobal =          Column(Boolean)
    isgenealogyartifact=Column(Boolean)
    ownerid =           Column(Integer)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    artifacttypeid =    Column(Integer)
    processoutputtypeid=Column(Integer)
    currentstateid =    Column(Integer)
    originalstateid =   Column(Integer)
    compoundartifactid= Column(Integer)
    outputindex =       Column(Integer)

    samples = relationship("Sample", secondary = artifact_sample_map, backref="artifacts")
    ancestors = relationship("Artifact", secondary = artifact_ancestor_map, 
                primaryjoin=artifactid==artifact_ancestor_map.c.artifactid, 
                secondaryjoin=artifactid==artifact_ancestor_map.c.ancestorartifactid)
    udfs = relationship("ArtifactUdfView")
    states = relationship("ArtifactState", backref='artifact')
    containerplacement = relationship('ContainerPlacement', uselist=False, backref='artifact')

    @hybrid_property
    def udf_dict(self):
        udf_dict={}
        for udfrow in self.udfs:
            if udfrow.udfvalue:
                if udfrow.udftype == "Numeric":
                    udf_dict[udfrow.udfname]=float(udfrow.udfvalue)
                elif udfrow.udftype == "Boolean":
                    udf_dict[udfrow.udfname]=(udfrow.udfvalue=="True")
                else:
                    udf_dict[udfrow.udfname]=udfrow.udfvalue
                
        return udf_dict

    @hybrid_property
    def qc_flag(self):
        latest_state=sorted(self.states, key=lambda x:x.lastmodifieddate)[-1]
        if latest_state.qcflag==0:
            return 'UNKNOWN'
        elif latest_state.qcflag==1:
            return 'PASSED'
        elif latest_state.qcflag==2:
            return 'FAILED'
        else:
            return 'ERROR'


    def __repr__(self):
        return "<Artifact(id={}, name={})>".format(self.artifactid, self.name)

class ArtifactUdfView(Base):
    """
    View mapping udfs with artifacts through the datastores.

    :arg INTEGER artifactid: the (short) artifact id
    :arg STRING udtname: name of the user defined type
    :arg STRING udfname: name of the user defined field
    :arg STRING udftype: type of the user defined field
    :arg STRING udfvalue: value of the user defined field
    :arg STRING udfunitlabel: unit of the user defined field

    """
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
    """
    View mapping udfs with processes through the datastores.

    :arg INTEGER processid: the (short) process id
    :arg INTEGER typeid: the process type id
    :arg STRING udtname: name of the user defined type
    :arg STRING udfname: name of the user defined field
    :arg STRING udftype: type of the user defined field
    :arg STRING udfvalue: value of the user defined field
    :arg STRING udfunitlabel: unit of the user defined field

    """
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
    """
    Table mapping sample placement in the containers

    :arg INTEGER placementid: internal placement ID. Primary key.
    :arg INTEGER containerid: the associated container id
    :arg INTEGER wellxposition: the horizontal position in the container of the sample
    :arg INTEGER wellyposition: the vertical position in the container of the sample
    :arg TIMESTAMP dateplaced: timestamp of the placement creation
    :arg INTEGER ownerid: researcherid of the user who made the placement
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unkown*
    :arg TIMESTAMP createddate: timestamp of the placement creation
    :arg TIMESTAMP lastmodifieddate: timestamp of the last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER reagentid: Reagent ID used in that placement
    :arg INTEGER processartifactid: artifact id of the artifact involved in that placement

    The following attributes are *not* found in the table, but are available through mapping

    :arg Container container: Container row associated with the ContainerPlacement row.
    :arg STRING api_string: string reporting the position in the same fashion as the API does.

    """
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

    def get_x_position(self):
        """Get the X position of the placement according to Container type"""
        ctype=self.container.type
        start=0
        if ctype.isxalpha:
            start=65
        start+=ctype.xindexstartsat
        value=start+self.wellxposition
        if ctype.isxalpha:
            return chr(value)
        return value

    def get_y_position(self):
        """Get the Y position of the placement according to Container type"""
        ctype=self.container.type
        start=0
        if ctype.isyalpha:
            start=65
        start+=ctype.yindexstartsat
        value=start+self.wellyposition
        if ctype.isyalpha:
            return chr(value)
        return value

    @hybrid_property
    def api_string(self):
        return "{0}:{1}".format(self.get_y_position(), self.get_x_position())

    def __repr__(self):
        return "<ContainerPlacement(id={}, pos={}:{}, cont={}, art={})>".format(self.placementid, self.wellxposition, self.wellyposition, self.containerid, self.processartifactid)


class Container(Base):
    """Table mapping containers

    :arg INTEGER containerid: The (short) container id. Primary Key.
    :arg STRING subtype: The container type
    :arg STRING luid: The (long) container id
    :arg BOOLEAN isvisible: *unkown*
    :arg STRING name: The container name
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER stateid: placeholders for empty, populated, depleted, discarded
    :arg INTEGER typeid: container type id from containertype (not mapped)
    :arg STRING lotnumber: *unknown*
    :arg TIMESTAMP expirydate: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg EntityUdfView udfs: EntityUdfView row associated with the Container row.
    :arg ContainerType type: ContainerType row associated with the Container row.

    """
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
    typeid =            Column(Integer, ForeignKey('containertype.typeid'))     
    lotnumber =         Column(String)
    expirydate =        Column(TIMESTAMP)

    #the entity id of Containers is 27
    udfs = relationship("EntityUdfView", foreign_keys=containerid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Container.containerid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==27)")
    type=relationship("ContainerType", uselist=False)

    def __repr__(self):
        return "<Container(id={}, name={})>".format(self.containerid, self.name)

class ContainerType(Base):
    """Table mapping containertype

    :arg INTEGER typeid: internal container type id
    :arg STRING name: container type name
    :arg INTEGER sequencenumber: *unknown*
    :arg BOOLEAN isvisible: *unknown*
    :arg INTEGER numxpositions: number of valid x positions in the container
    :arg BOOLEAN isxalpha: true if the x axis is coded by letter
    :arg INTEGER numypositions: number of valid y positions in the container
    :arg BOOLEAN isyalpha: true if the x axis is coded by letter
    :arg INTEGER xindexstartsat: first value of the x axis
    :arg INTEGER yindexstartsat: first value of the y axis
    :arg INTEGER iconsetconstant: *unknown*
    :arg INTEGER ownerid: researcherid of the owner of the container type
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: date of creation of the type
    :arg TIMESTAMP lastmodifieddate: date of last modification
    :arg INTEGER lastmodifiedby: researcher id of the last modifier
    :arg STRING subtype: *unknown*
    :arg STRING vendoruniqueid: *unknown*
    :arg BOOLEAN istube: true if the container is a tube

    """
    __tablename__ = 'containertype'
    typeid =            Column(Integer, primary_key=True)
    name =              Column(String)
    sequencenumber =    Column(Integer)
    isvisible =         Column(Boolean)
    numxpositions =     Column(Integer)
    isxalpha =          Column(Boolean)
    numypositions =     Column(Integer)
    isyalpha =          Column(Boolean)
    xindexstartsat =    Column(Integer)
    yindexstartsat =    Column(Integer)
    iconsetconstant =   Column(Integer)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    subtype =           Column(String)
    vendoruniqueid =    Column(String)
    istube =            Column(Boolean)

    def __repr__(self):
        return "<ContainerType(id={}, name={})>".format(self.typeid, self.name)


class ReagentLabel(Base):
    """Table mapping reagent labels

    :arg INTEGER labelid: The reagent label id. Primary Key.
    :arg STRING name: The reagent label name
    :arg INTEGER ownerid: Researcher ID of the reagent label creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact artifacts: list of artifacts linked through the artifact_label junction table.

    """
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
    """ Table mapping Analytes

    :arg INTEGER artifactid: artifact id of the analyte. Primary key
    :arg INTEGER analyteid: internal analyte id
    :arg BOOLEAN iscalibrant: *unknown*
    :arg INTEGER sequencenumber: *unknown*
    :arg BOOLEAN isvisible: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact artifact: artifact row corresponding to the analyte row.

    """
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
    """ Table mapping ResultFiles

    :arg INTEGER artifactid: artifact id of the ResultFile. Primary key
    :arg INTEGER fileid: internal file id
    :arg STRING typeid: *unknown*
    :arg INTEGER parsestatus: *unknown*
    :arg INTEGER status: *unknown*
    :arg INTEGER commandid: *unknown*
    :arg BOOLEAN glsfileid: id of the corresponding row in glsfile

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact artifact: artifact row corresponding to the ResultFile row.
    :arg GlsFile glsfile: glsfile row corresponding to the ResultFile row.

    """
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
    """ Table mapping  Glsfiles

    :arg INTEGER fileid: internal file id of corresponding ResultFile. Primary key.
    :arg STRING server: ftp location
    :arg STRING contenturi: URI to the file
    :arg STRING luid: long file id
    :arg STRING originallocation: original path of the file on the uploader's computer.
    :arg BOOLEAN ispublished: *unknown* 
    :arg INTEGER ownerid: Researcher ID of the file creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER attachtoid: *unknown*
    :arg INTEGER attachtoclassid: *unknown*

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact artifact: artifact row corresponding to the ResultFile row.
    :arg GlsFile glsfile: glsfile row corresponding to the ResultFile row.

    """
    __tablename__ = 'glsfile'
    fileid =            Column(Integer, ForeignKey('resultfile.glsfileid'), primary_key=True)
    server =            Column(String)
    contenturi =        Column(String)
    luid =              Column(String)
    originallocation =  Column(String)
    ispublished =       Column(Boolean)
    ownerid =           Column(Integer)     
    datastoreid =       Column(Integer)     
    isglobal =          Column(Boolean)     
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    attachtoid =        Column(Integer)
    attachtoclassid =   Column(Integer)

    file=relationship("ResultFile",uselist=False, backref="glsfile")
    
    def __repr__(self):
        return "<GlsFile(id={})>".format(self.fileid)

class Researcher(Base):
    """ Table mapping Researchers

    :arg INTEGER researcherid: internal researcher id. Primary key.
    :arg INTEGER roleid: internal role id 
    :arg STRING firstname: First name of the researcher
    :arg STRING lastname: Last name of the researcher
    :arg STRING title: researcher's title, if any
    :arg STRING initials: researcher's initials
    :arg INTEGER ownerid: id of the row creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg STRING phone: researcher's phone number
    :arg STRING email: researcher's email address
    :arg STRING fax: researcher's fax number
    :arg INTEGER addressid: id of the associated Address row. (Not mapped)
    :arg INTEGER labid: id of the associated Lab row. (Not mapped)
    :arg INTEGER supervisorid: researcher id of the researcher's supervisor
    :arg BOOLEAN isapproved: has been validated as a user
    :arg STRING requestedsupervisorfirstname: *unknown* 
    :arg STRING requestedsupervsodlastname: *unknown*
    :arg STRING requestedusername: *unknown*
    :arg STRING requestedpassword: *unknown*
    :arg STRING requestedlabname: *unknown*
    :arg LARGEBINARY avatar: base64 encoding of the avatar image
    :arg STRING avatarcontenttype: mime type of the avatar image

    """
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
    labid =             Column(Integer, ForeignKey('lab.labid')) 
    supervisorid =      Column(Integer) 
    isapproved =        Column(Boolean) 
    requestedsupervisorfirstname =  Column(String) 
    requestedsupervisorlastname =   Column(String) 
    requestedusername = Column(String) 
    requestedpassword = Column(String) 
    requestedlabname =  Column(String) 
    avatar =            Column(LargeBinary) 
    avatarcontenttype = Column(String) 

    lab=relationship("Lab",uselist=False)

    def __repr__(self):
        return "<Researcher(id={}, name={} {}, initials={})>".format(self.researcherid, self.firstname, self.lastname, self.initials)

class EscalationEvent(Base):
    """ Table mapping Escalation events
    
    :arg INTEGER eventid: escalation event internal id. Primary Key.
    :arg INTEGER processid: process ID where the escalation took place
    :arg INTEGER originarorid: researcher id of the user requesting a review
    :arg INTEGER reviewerid: researcher id of the user having to perform the review
    :arg TIMESTAMP escalationdate: timestamp of the review request
    :arg TIMESTAMP reviewdate: timestamp of the review completion
    :arg STRING escalationcomment: comment of the review request
    :arg STRING reviewcomment: comment of the review completion
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier

    """
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
    """ Table mapping the escalated samples

    :arg INTEGER escalatedsampleid: the escalated sample internal id. Primary key.
    :arg INTEGER escalationeventid: the associated escalation event id
    :arg INTEGER artifactid: the associated artifact id.
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier

    """
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

class ProcessIOTracker(Base):
    """Table mapping the input/outputs of processes

    :arg INTEGER trackerid: internal tracker id. Primary key
    :arg FLOAT inputvolume: *unknown*
    :arg FLOAT inputconcentration: *unknown*
    :arg INTEGER inputstatepreid: *unknown*
    :arg INTEGER inputstatuspostid:*unknown*
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER inputartifactid: id of the associated input artifact
    :arg INTEGER processid: id of the associated process

    The following attributes are *not* found in the table, but are available through mapping

    :arg Artifact artifact: artifact row corresponding to the ResultFile row.
    
    """
    __tablename__ = 'processiotracker'
    trackerid =          Column(Integer, primary_key=True)
    inputvolume =        Column(Float) 
    inputconcentration = Column(Float)
    inputstatepreid =    Column(Integer)
    inputstatepostid =   Column(Integer)
    ownerid =            Column(Integer)
    datastoreid =        Column(Integer)
    isglobal =           Column(Boolean)
    createddate =        Column(TIMESTAMP)
    lastmodifieddate =   Column(TIMESTAMP)
    lastmodifiedby =     Column(Integer)
    inputartifactid =    Column(Integer, ForeignKey('artifact.artifactid'))
    processid =          Column(Integer, ForeignKey('process.processid'))

    def __repr__(self):
        return "<ProcessIOTracker(id={}, processid={}, inputartifactid={})>".format(self.trackerid, self.processid, self.inputartifactid)


class ArtifactState(Base):
    """Table mapping artifac states and QC

    :arg INTEGER stateid: the internal state id. Primary key.
    :arg INTEGER qcflag: 0: UNKNOWN, 1: PASSED, 2: FAILED
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER artifactid: id of the associated artifact

    """
    __tablename__ = 'artifactstate'
    stateid =           Column(Integer, primary_key=True)
    qcflag =            Column(Integer)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    artifactid =        Column(Integer, ForeignKey('artifact.artifactid'))

    def __repr__(self):
        return "<ArtifactState(id={}, artifactid={})>".format(self.stateid, self.artifactid)


class OutputMapping(Base):
    """Table mapping the process outputs 

    :arg INTEGER mappingid: the internal mapping id
    :arg FLOAT outputvolume: *unknown*
    :arg FLOAT outputconcentration: *unknown*
    :arg INTEGER ownerid: Researcher ID of the container creator
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: The date of creation
    :arg TIMESTAMP lastmodifieddate: The date of last modification
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER trackerid: trackerid of the associated processiotracker 
    :arg INTEGER outputartifactid: artifactid of the associated artifact

    """
    __tablename__ = 'outputmapping'
    mappingid =             Column(Integer, primary_key=True)
    outputvolume =          Column(Float)
    outputconcentration =   Column(Float)
    ownerid =               Column(Integer)
    datastoreid =           Column(Integer)
    isglobal =              Column(Boolean)
    createddate =           Column(TIMESTAMP)
    lastmodifieddate =      Column(TIMESTAMP)
    lastmodifiedby =        Column(Integer)
    trackerid =             Column(Integer, ForeignKey('processiotracker.trackerid'))
    outputartifactid =      Column(Integer, ForeignKey('artifact.artifactid')) 

    tracker=relationship('ProcessIOTracker', backref='output')

    def __repr__(self):
        return "<OutputMapping(mappingid={}, trackerid={}, outputartifactid={})>".format(self.mappingid, self.trackerid, self.outputartifactid)

class Principals(Base):
    """Table mapping user information

    :arg INTEGER principalid: internal principal id, primary key
    :arg STRING username: username associated with that row
    :arg STRING password: hashed password 
    :arg BOOLEAN isvisible: *unknown*
    :arg BOOLEAN isloggedin: flag checking is the user is currently within the system
    :arg INTEGER datastoreid: id of the associated datastore
    :arg INTEGER ownerid: id of the creator of that row
    :arg BOOLEAN isglobal:  *unknown*
    :arg TIMESTAMP createddate: row creation date
    :arg TIMESTAMP lastmodifieddate: row last modification date
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg STRING ldapdn: *unknown*
    :arg STRING ldapuuid: *unknown* 
    :arg BOOLEAN accountlocked : *unknown* 
    :arg INTEGER researcherid: id of the associated researcher row 
    :arg BOOLEAN locked: *unknown*

    """
    __tablename__ = 'principals'
    principalid =       Column(Integer, primary_key=True)
    username =          Column(String)
    password =          Column(String)
    isvisible =         Column(Boolean)
    isloggedin =        Column(Boolean)
    datastoreid =       Column(Integer)
    ownerid =           Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    ldapdn =            Column(String)
    ldapuuid =          Column(String)
    accountlocked =     Column(Boolean)
    researcherid =      Column(Integer, ForeignKey('researcher.researcherid'))
    locked =            Column(Boolean)

    researcher=relationship("Researcher")

    def __repr__(self):
        return "<Principals(principalid={}, username={}, researcherid={})>".format(self.principalid, self.username, self.researcherid)

class Lab(Base):
    """Table mapping Lab entities

    :arg INTEGER labid: internal lab id. Primary key.
    :arg STRING name: Lab name
    :arg STRING website: URL to the lab's website
    :arg INTEGER ownerid: id of the creator of that row
    :arg INTEGER datastoreid: id of the associated datastore
    :arg BOOLEAN isglobal:  *unknown*
    :arg TIMESTAMP createddate: row creation date
    :arg TIMESTAMP lastmodifieddate: row last modification date
    :arg INTEGER lastmodifiedby: researcherid of the last modifier
    :arg INTEGER billingadressid: ID of the associated billing address
    :arg INTEGER shippingaddressid: ID of the associated shipping address
    
    """

    __tablename__ = "lab"
    labid =             Column(Integer, primary_key=True)
    name =              Column(String)
    website =           Column(String)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP)
    lastmodifiedby =    Column(Integer)
    billingaddressid =  Column(Integer)
    shippingaddressid = Column(Integer)


    #the entity id of Lab is 17
    udfs = relationship("EntityUdfView", foreign_keys=labid, remote_side=EntityUdfView.attachtoid, uselist=True,
            primaryjoin="and_(Lab.labid==EntityUdfView.attachtoid, EntityUdfView.attachtoclassid==17)")

    @hybrid_property
    def udf_dict(self):
        udf_dict={}
        for udfrow in self.udfs:
            if udfrow.udfvalue:
                if udfrow.udftype == "Numeric":
                    udf_dict[udfrow.udfname]=float(udfrow.udfvalue)
                elif udfrow.udftype == "Boolean":
                    udf_dict[udfrow.udfname]=(udfrow.udfvalue=="True")
                else:
                    udf_dict[udfrow.udfname]=udfrow.udfvalue
                
        return udf_dict

    def __repr__(self):
        return "<Lab(labid={}, name={})>".format(self.labid, self.name)

class ReagentType(Base):
    """Table mapping the reagenttype table

    :arg INTEGER reagenttypeid: internal reagent type id
    :arg STRING name: name of the reagent type
    :arg STRING meta_data: *unknown*
    :arg STRING specialtype: *unknown*
    :arg INTEGER ownerid: principal ID of the owner
    :arg INTEGER datastoreid: *unknown*
    :arg BOOLEAN isglobal: *unknown*
    :arg TIMESTAMP createddate: date of creation
    :arg TIMESTAMP lastmodifieddate: date of last modification
    :arg INTEGER lastmodifiedby: principal id of the last modifier
    :arg BOOLEAN isvisible: *unknown*
    :arg INTEGER reagentcategoryid: the associated reagentcategory id

    """
    __tablename__ = 'reagenttype'
    reagenttypeid =     Column(Integer, primary_key=True)
    name =              Column(String)
    meta_data =         Column('metadata', String)
    specialtype =       Column(String)
    ownerid =           Column(Integer)
    datastoreid =       Column(Integer)
    isglobal =          Column(Boolean)
    createddate =       Column(TIMESTAMP)
    lastmodifieddate =  Column(TIMESTAMP) 
    lastmodifiedby =    Column(Integer)
    isvisible =         Column(Boolean)
    reagentcategoryid = Column(Integer)

    def __repr__(self):
        return "<ReagentType(reagenttypeid={}, name={})>".format(self.reagenttypeid, self.name)
