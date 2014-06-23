from __main__ import vtk, qt, ctk, slicer

#
# SimulReg
#

class SimulReg:
  def __init__(self, parent):
    parent.title = "Simul Reg"
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = ["Brian Ninni (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Used to run registration on two computers simulateously
    """
    parent.acknowledgementText = """  """ # replace with organization, grant and thanks.
    self.parent = parent

#
# qSimulRegWidget
#

class SimulRegWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    
    #initialize some variables and settings
    self.connection_node = slicer.vtkMRMLIGTLConnectorNode()
    slicer.mrmlScene.AddNode(self.connection_node)
    self.next_node = 0
    
  def setup(self):
    # The Link Section
    ##### Collapsible Layout
    self.connect_collapsible_button = ctk.ctkCollapsibleButton()
    self.connect_collapsible_button.text = 'Connect'
    self.layout.addWidget(self.connect_collapsible_button)
    self.connect_form_layout = qt.QGridLayout(self.connect_collapsible_button)
    self.connect_form_layout.setColumnStretch(0,1)
    self.connect_form_layout.setColumnStretch(1,1)
    ########## Collapsible Layout Widgets
    self.port_field = qt.QLineEdit()
    self.port_field.setText('18944')
    self.port_label = qt.QLabel('Port: ')
    self.port_label.alignment = 'AlignRight'
    self.connect_server_button = qt.QPushButton("Connect as Server")
    self.connect_server_button.connect('clicked(bool)', self.addServerConnection)
    self.connect_server_button.toolTip = "Add a networked computer to communicate with."
    self.connect_client_button = qt.QPushButton("Connect as Client")
    self.connect_client_button.connect('clicked(bool)', self.addClientConnection)
    self.connect_client_button.toolTip = "Add a networked computer to communicate with."
    self.connect_form_layout.addWidget(self.port_label,0,0)
    self.connect_form_layout.addWidget(self.port_field,0,1)
    self.connect_form_layout.addWidget(self.connect_server_button,1,0)
    self.connect_form_layout.addWidget(self.connect_client_button,1,1)
    
    # The Share Volume Section
    ##### Collapsible Layout
    self.share_collapsible_button = ctk.ctkCollapsibleButton()
    self.share_collapsible_button.text = 'Send Volume'
    self.layout.addWidget(self.share_collapsible_button)
    self.share_form_layout = qt.QGridLayout(self.share_collapsible_button)
    self.connect_form_layout.setColumnStretch(0,1)
    self.connect_form_layout.setColumnStretch(1,1)
    self.share_collapsible_button.setEnabled(0)
    self.share_collapsible_button.collapsed = 1;
    #####The 'Share' Form
    ########## 'Share' Button
    self.share_button = qt.QPushButton("Send Volume")
    self.share_button.toolTip = "Send the Volume"
    self.share_form_layout.addWidget(self.share_button,0,1)
    self.share_button.connect('clicked(bool)', self.sendVolume)
    ##########get the latest volumes
    self.generateVolumesDropdown()
    self.volume_dropdown.toolTip = "Select a Volume to Send"
    self.share_form_layout.addWidget(self.volume_dropdown,0,0)
    ##########Add event trigger to mrmlScene (when new volume gets added)
    self.addCheck = slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent,self.updateNodeList)
    self.removeCheck = slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent,self.updateNodeList)
    
    # The Status Indicator
    self.status_button = qt.QPushButton("Status: Not Connected")
    self.status_button.setStyleSheet("border-radius:5px;border:2px solid black;color:black;background-color:red;height:40px;width:10px;font-size:16px;margin-left:10%;margin-right:10%")
    self.layout.addWidget(self.status_button)
    self.receiveCheck = self.connection_node.AddObserver('ReceiveEvent', self.updateStatus)
    
    # Add vertical spacer
    self.layout.addStretch(1)
  
  #to add connection and set up as server
  def addServerConnection(self):
    if self.connection_node.SetTypeServer(int(self.port_field.text)) == 1:
      if self.connection_node.Start() == 1:
        self.connect_collapsible_button.setEnabled(0)
        self.connect_collapsible_button.collapsed = 1;
        self.share_collapsible_button.setEnabled(1)
        self.share_collapsible_button.collapsed = 0;
        
  #to add a connection and set up as client
  def addClientConnection(self):
    if self.connection_node.SetTypeClient('192.168.10.1', int(self.port_field.text)) == 1:
      if self.connection_node.Start() == 1:
        self.receiveCheck = self.connection_node.AddObserver('ReceiveEvent', self.runRegistration)
        self.connect_collapsible_button.setEnabled(0)
        self.connect_collapsible_button.collapsed = 1;
        
  #to run the registration on a client computer when a new node is received
  def runRegistration(self, caller, event):
    #get the latest node
    self.new_node = self.connection_node.GetIncomingMRMLNode(self.next_node)
    #only run if it is a volume node
    if self.new_node is not None:
      if hasattr(slicer.modules,'IGITRegWidget'):
        #increase the node index
        self.next_node = self.next_node + 1
        if self.new_node.GetNodeTagName() == 'Volume':
          slicer.modules.IGITRegWidget.stageRegistration(slicer.modules.IGITRegWidget.inputSelector.currentNode(),self.new_node)
          slicer.modules.IGITRegWidget.doRegistration(slicer.modules.IGITRegWidget.inputSelector.currentNode(),self.new_node)
          slicer.modules.IGITRegWidget.onReadRegButton()
        
  #to send a volume through the connection node:
  def sendVolume(self):
    #get the volume node and register it as an outgoing node (if the status is "Connected"
    if self.connection_node.GetState() == 2:
      self.connection_node.RegisterOutgoingMRMLNode(self.volumes_list.GetItemAsObject(self.volume_dropdown.currentIndex))
      self.connection_node.PushNode(self.volumes_list.GetItemAsObject(self.volume_dropdown.currentIndex))
  
  #to update the state
  def updateStatus(self, caller, event):
    #if it a connector node, make sure IGITReg is initialized
    if self.connection_node.GetType() == 2 and hasattr(slicer.modules,'IGITRegWidget') is False:
        self.status_button.text = "Status: IGITReg Not Initialized"
        self.status_button.setStyleSheet("border-radius:5px;border:2px solid black;color:black;background-color:red;height:40px;width:10px;font-size:16px;margin-left:10%;margin-right:10%")
    else:
      if self.connection_node.GetState() == 0:
        self.status_button.text = "Status: Not Connected"
        self.status_button.setStyleSheet("border-radius:5px;border:2px solid black;color:black;background-color:red;height:40px;width:10px;font-size:16px;margin-left:10%;margin-right:10%")
      elif self.connection_node.GetState()  == 1:
        self.status_button.text = "Status: Waiting..."
        self.status_button.setStyleSheet("border-radius:5px;border:2px solid black;color:black;background-color:yellow;height:40px;width:10px;font-size:16px;margin-left:10%;margin-right:10%")
      elif self.connection_node.GetState() == 2:
        self.status_button.text = "Status: Connected"
        self.status_button.setStyleSheet("border-radius:5px;border:2px solid black;color:black;background-color:green;height:40px;width:10px;font-size:16px;margin-left:10%;margin-right:10%")
          
  #to update the list of volumes in this scene
  def generateVolumesDropdown(self):
    self.volume_dropdown = qt.QComboBox()
    self.volumes_list = slicer.mrmlScene.GetNodesByClass('vtkMRMLVolumeNode')
    if self.volumes_list.GetNumberOfItems() == 0:
      self.share_button.setEnabled(0)
      self.volume_dropdown.setEnabled(0)
      self.volume_dropdown.addItem('No Volumes Exist!')
    else:
      self.share_button.setEnabled(1)
      self.volume_dropdown.setEnabled(1)
      for i in range(self.volumes_list.GetNumberOfItems()):
        self.volume_dropdown.addItem(self.volumes_list.GetItemAsObject(i).GetID())

  #to see if we need to add a volume to this scene
  def updateNodeList(self, caller, event):
    self.volume_dropdown.deleteLater()
    #add the new widget
    self.generateVolumesDropdown()
    self.share_form_layout.addWidget(self.volume_dropdown,0,0)