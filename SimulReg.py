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
    self.connect_collapsible_button = qt.QPushButton("Connect")
    self.connect_collapsible_button.connect('clicked(bool)', self.toggleConnectLayout)
    self.layout.addWidget(self.connect_collapsible_button)
    self.connect_collapsible_layout = qt.QListView()
    self.connect_form_layout = qt.QFormLayout(self.connect_collapsible_layout)
    self.connect_collapsible_layout.setFixedHeight(125)
    self.layout.addWidget(self.connect_collapsible_layout)
    ########## Collapsible Layout Widgets
    self.server_field = qt.QLineEdit()
    self.server_field.setText('Server')
    self.port_field = qt.QLineEdit()
    self.port_field.setText('Port')
    self.connect_server_button = qt.QPushButton("Connect as Server")
    self.connect_server_button.connect('clicked(bool)', self.addServerConnection)
    self.connect_server_button.toolTip = "Add a networked computer to communicate with."
    self.connect_client_button = qt.QPushButton("Connect as Client")
    self.connect_client_button.connect('clicked(bool)', self.addClientConnection)
    self.connect_client_button.toolTip = "Add a networked computer to communicate with."
    self.connect_form_layout.addWidget(self.server_field)
    self.connect_form_layout.addWidget(self.port_field)
    self.connect_form_layout.addWidget(self.connect_server_button)
    self.connect_form_layout.addWidget(self.connect_client_button)
    
    ##### Add Link Error Message
    self.link_error_window = qt.QMessageBox()
    self.link_error_window.setIcon(3)
    self.link_error_window.setText("Error: Couldn't connect to server")
    self.link_error_window.addButton(0x00000400)
    
    # The Share Volume Section
    ##### Collapsible Layout
    self.share_collapsible_button = qt.QPushButton("Share Volume")
    self.share_collapsible_button.connect('clicked(bool)', self.toggleShareLayout)
    self.layout.addWidget(self.share_collapsible_button)
    self.share_collapsible_button.setEnabled(0)
    self.share_collapsible_layout = qt.QListView()
    self.layout.addWidget(self.share_collapsible_layout)
    self.share_collapsible_layout.setVisible(0)
    self.share_collapsible_layout.setFixedHeight(75)
    self.share_form_layout = qt.QFormLayout(self.share_collapsible_layout)
    #####The 'Share' Form
    ########## 'Share' Button
    self.share_button = qt.QPushButton("Send Volume")
    self.share_button.toolTip = "Send the Volume"
    self.share_form_layout.addWidget(self.share_button)
    self.share_button.connect('clicked(bool)', self.sendVolume)
    ##########get the latest volumes
    self.generateVolumesDropdown()
    self.volume_dropdown.toolTip = "Select a Volume to Send"
    self.share_form_layout.addWidget(self.volume_dropdown)
    ##########Add event trigger to mrmlScene (when new volume gets added)
    self.addCheck = slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent,self.updateNodeList)
    self.removeCheck = slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent,self.updateNodeList)
    
    
  #to toggle the show/hide of the connect layout
  def toggleConnectLayout(self):
    if self.connect_collapsible_layout.height:
      self.connect_collapsible_layout.setFixedHeight(0)
    else:
      self.connect_collapsible_layout.setFixedHeight(125)    
    
  #to toggle the show/hide of the connect layout
  def toggleShareLayout(self):
    if self.share_collapsible_layout.height:
      self.share_collapsible_layout.setFixedHeight(0)
    else:
      self.share_collapsible_layout.setFixedHeight(75)
  
  #to add connection and set up as server
  def addServerConnection(self):
    if self.connection_node.SetTypeServer(int(self.port_field.text)): == 1:
      if self.connection_node.Start() == 1:
        self.finishConnection()
      
  #to add a connection and set up as client
  def addClientConnection(self):
    if self.connection_node.SetTypeClient(self.server_field.text, int(self.port_field.text)) == 1:
      if self.connection_node.Start() == 1:
        self.finishConnection()
      
  #to finish the "Add Connection Routine"
  def finishConnection(self):
    self.receiveCheck = self.connection_node.AddObserver('ReceiveEvent', self.runRegistration)
    #self.receiveCheck = self.connection_node.AddObserver('ModifiedEvent', self.runRegistration)
    self.connect_collapsible_layout.setVisible(0)
    self.connect_collapsible_button.setEnabled(0)
    self.share_collapsible_button.setEnabled(1)
    self.share_collapsible_layout.setVisible(1)
      
  #to run the registration on a client computer when a new node is received
  def runRegistration(self, caller, event):
    #get the latest node
    self.new_node = self.connection_node.GetIncomingMRMLNode(self.next_node)
    #only run if it is a volume node
    if self.new_node is not None:
      #increase the node index
      self.next_node = self.next_node + 1
      if self.new_node.GetNodeTagName() == 'Volume':
        ############################
        ############################
        ##code to run registration##
        ############################
        ############################
        print run
        
  #to send a volume through the connection node:
  def sendVolume(self):
    #get the volume node and register it as an outgoing node
    self.connection_node.RegisterOutgoingMRMLNode(self.volumes_list.GetItemAsObject(self.volume_dropdown.currentIndex))
    self.connection_node.PushNode(self.volumes_list.GetItemAsObject(self.volume_dropdown.currentIndex))
  
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
    #to remove the old widget
    label = self.share_form_layout.labelForField(self.volume_dropdown)
    if label is not None:
        label.deleteLater()
    self.volume_dropdown.deleteLater()
    #add the new widget
    self.generateVolumesDropdown()
    self.share_form_layout.addWidget(self.volume_dropdown)