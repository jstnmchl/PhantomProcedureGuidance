import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# treatmentPlanRegistration
#

class treatmentPlanRegistration(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "treatmentPlanRegistration" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# treatmentPlanRegistrationWidget
#

class treatmentPlanRegistrationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Fixed model selector
    #
    self.fixedModelSelector = slicer.qMRMLNodeComboBox()
    self.fixedModelSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.fixedModelSelector.selectNodeUponCreation = True
    self.fixedModelSelector.addEnabled = False
    self.fixedModelSelector.removeEnabled = False
    self.fixedModelSelector.noneEnabled = False
    self.fixedModelSelector.showHidden = False
    self.fixedModelSelector.showChildNodeTypes = False
    self.fixedModelSelector.setMRMLScene( slicer.mrmlScene )
    self.fixedModelSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Fixed Model: ", self.fixedModelSelector)

    #
    # Moving model selector
    #
    self.movingModelSelector = slicer.qMRMLNodeComboBox()
    self.movingModelSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.movingModelSelector.selectNodeUponCreation = True
    self.movingModelSelector.addEnabled = False
    self.movingModelSelector.removeEnabled = False
    self.movingModelSelector.noneEnabled = False
    self.movingModelSelector.showHidden = False
    self.movingModelSelector.showChildNodeTypes = False
    self.movingModelSelector.setMRMLScene( slicer.mrmlScene )
    self.movingModelSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Moving Model: ", self.movingModelSelector)

    #
    # initialisation transform selector
    #
    self.initialTransformSelector = slicer.qMRMLNodeComboBox()
    self.initialTransformSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.initialTransformSelector.selectNodeUponCreation = True
    self.initialTransformSelector.addEnabled = True
    self.initialTransformSelector.removeEnabled = True
    self.initialTransformSelector.noneEnabled = True
    self.initialTransformSelector.showHidden = False
    self.initialTransformSelector.showChildNodeTypes = False
    self.initialTransformSelector.setMRMLScene(slicer.mrmlScene)
    self.initialTransformSelector.setToolTip("Pick the output to the algorithm.")
    parametersFormLayout.addRow("Initialisation Transform: ", self.initialTransformSelector)

    #
    # output transform selector
    #
    self.outputTransformSelector = slicer.qMRMLNodeComboBox()
    self.outputTransformSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.outputTransformSelector.selectNodeUponCreation = True
    self.outputTransformSelector.addEnabled = True
    self.outputTransformSelector.removeEnabled = True
    self.outputTransformSelector.noneEnabled = True
    self.outputTransformSelector.showHidden = False
    self.outputTransformSelector.showChildNodeTypes = False
    self.outputTransformSelector.setMRMLScene( slicer.mrmlScene )
    self.outputTransformSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Transform: ", self.outputTransformSelector)

    #
    # threshold value
    #
    """
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)
    """


    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.fixedModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.movingModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputTransformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.initialTransformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.fixedModelSelector.currentNode() and self.movingModelSelector.currentNode() and self.outputTransformSelector.currentNode() and self.initialTransformSelector.currentNode()

  def onApplyButton(self):
    logic = treatmentPlanRegistrationLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    logic.run(self.fixedModelSelector.currentNode(), self.movingModelSelector.currentNode(), self.initialTransformSelector.currentNode(), self.outputTransformSelector.currentNode(), enableScreenshotsFlag)

#
# treatmentPlanRegistrationLogic
#

class treatmentPlanRegistrationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputModels(self, fixedModelNode, movingModelNode):
    """Validates if the fixed model is not the same as the moving model
    """
    if not fixedModelNode:
      logging.debug('isValidInputOutputData failed: no fixed model node defined')
      return False
    if not movingModelNode:
      logging.debug('isValidInputOutputData failed: no moving model node defined')
      return False
    if fixedModelNode.GetID()==movingModelNode.GetID():
      logging.debug('isValidInputOutputData failed: fixed and moving models are the same.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, fixedModel, movingModel, initialTransform, outputTransform, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputModels(fixedModel, movingModel):
      slicer.util.errorDisplay('Fixed model is the same as moving model. Choose different models.')
      return False

    logging.info('Processing started')

    #Get poly data of moving model
    movingPolyData = movingModel.GetPolyData()

    # Transform poly data of moving model with initialisation transform
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(movingPolyData)
    transformFilter.SetTransform(initialTransform.GetTransformToParent())
    transformFilter.Update()

    #Appply ICP registration to transformed poly data and fixed model poly data as per IGT module: https://github.com/SlicerIGT/SlicerIGT/blob/master/ModelRegistration/ModelRegistration.py#L166
    icpTransform = vtk.vtkIterativeClosestPointTransform()
    icpTransform.SetSource(transformFilter.GetOutput()) #moving
    icpTransform.SetTarget(fixedModel.GetPolyData())  #fixed
    icpTransform.GetLandmarkTransform().SetModeToRigidBody()
    icpTransform.SetMaximumNumberOfIterations(100)
    icpTransform.Modified()
    icpTransform.Update()

    #Assign output transform to linear transform node - current output neglects initialisation (CHANGE THIS)
    outputTransform.SetMatrixTransformToParent(icpTransform.GetMatrix())

    #Transform moving model in scene to be aligned with fixed model (DO THIS)



    logging.info('Processing completed')

    return True


class treatmentPlanRegistrationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_treatmentPlanRegistration1()

  def test_treatmentPlanRegistration1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = treatmentPlanRegistrationLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')