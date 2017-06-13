import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import SimpleITK as sitk
import sitkUtils

#
# SimplePhantomSegmentation
#

class SimplePhantomSegmentation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SimplePhantomSegmentation" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Justin Michael (Robarts Research Institute)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# SimplePhantomSegmentationWidget
#

class SimplePhantomSegmentationWidget(ScriptedLoadableModuleWidget):
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
    # input volume selector (volume to be segmented)
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    #self.inputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # DEBUG input volume selector (volume to be segmented)
    #
    """
    self.DEBUGinputSelector = slicer.qMRMLNodeComboBox()
    self.DEBUGinputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.DEBUGinputSelector.selectNodeUponCreation = True
    self.DEBUGinputSelector.addEnabled = False
    self.DEBUGinputSelector.removeEnabled = False
    self.DEBUGinputSelector.noneEnabled = False
    self.DEBUGinputSelector.showHidden = False
    self.DEBUGinputSelector.showChildNodeTypes = False
    self.DEBUGinputSelector.setMRMLScene(slicer.mrmlScene)
    self.DEBUGinputSelector.setToolTip("Pick the input to the algorithm.")
    parametersFormLayout.addRow("Input Volume: ", self.DEBUGinputSelector)
    """

    #
    # input seed selector (seed for connected threshold)
    #
    self.inputSeedSelector = slicer.qMRMLNodeComboBox()
    self.inputSeedSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.inputSeedSelector.selectNodeUponCreation = True
    self.inputSeedSelector.addEnabled = False
    self.inputSeedSelector.removeEnabled = False
    self.inputSeedSelector.noneEnabled = False
    self.inputSeedSelector.showHidden = False
    self.inputSeedSelector.showChildNodeTypes = False
    self.inputSeedSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSeedSelector.setToolTip( "Pick the seed point to the connected segmentation." )
    parametersFormLayout.addRow("Input Seed(s): ", self.inputSeedSelector)

    #
    # output label map selector
    #
    self.outputLabelMapSelector = slicer.qMRMLNodeComboBox()
    self.outputLabelMapSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    #self.outputLabelMapSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputLabelMapSelector.selectNodeUponCreation = True
    self.outputLabelMapSelector.addEnabled = True
    self.outputLabelMapSelector.removeEnabled = True
    self.outputLabelMapSelector.noneEnabled = True
    self.outputLabelMapSelector.showHidden = False
    self.outputLabelMapSelector.showChildNodeTypes = False
    self.outputLabelMapSelector.setMRMLScene( slicer.mrmlScene )
    self.outputLabelMapSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Label Map: ", self.outputLabelMapSelector)

    #
    # output model selector
    #
    self.outputModelSelector = slicer.qMRMLNodeComboBox()
    self.outputModelSelector.nodeTypes = ["vtkMRMLModelHierarchyNode"]
    self.outputModelSelector.selectNodeUponCreation = True
    self.outputModelSelector.addEnabled = True
    self.outputModelSelector.removeEnabled = True
    self.outputModelSelector.noneEnabled = True
    self.outputModelSelector.showHidden = False
    self.outputModelSelector.showChildNodeTypes = False
    self.outputModelSelector.setMRMLScene(slicer.mrmlScene)
    self.outputModelSelector.setToolTip("Pick the output to the algorithm.")
    parametersFormLayout.addRow("Output Model Hierarchy: ", self.outputModelSelector)

    #
    # threshold value
    #
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 1
    self.imageThresholdSliderWidget.minimum = 0
    self.imageThresholdSliderWidget.maximum = 500
    self.imageThresholdSliderWidget.value = 100
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

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
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputLabelMapSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputLabelMapSelector.currentNode()

  def onApplyButton(self):
    logic = SimplePhantomSegmentationLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.inputSeedSelector.currentNode(), self.outputLabelMapSelector.currentNode(), self.outputModelSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# SimplePhantomSegmentationLogic
#

class SimplePhantomSegmentationLogic(ScriptedLoadableModuleLogic):
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

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
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

  def run(self, inputVolume, inputSeeds, outputLabelMap, outputModel, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """



    if not self.isValidInputOutputData(inputVolume, outputLabelMap):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')
    """
    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputLabelMap.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    """
    #Segment image using Connected Threshold Image Filter
    import SimpleITK as sitk
    import sitkUtils

    inputImage = sitkUtils.PullFromSlicer(inputVolume.GetName())
    segmentationFilter = sitk.ConnectedThresholdImageFilter()
    segmentationFilter.SetLower(0)
    segmentationFilter.SetUpper(imageThreshold)
    segmentationFilter.SetReplaceValue(1)

    #Add fiducial points as seeds
    numSeeds = inputSeeds.GetNumberOfFiducials()
    print('Adding seeds...')
    mat = vtk.vtkMatrix4x4()
    inputVolume.GetRASToIJKMatrix(mat)
    for i in range(numSeeds):
      seedPoint_ras = [0.0,0.0,0.0]
      inputSeeds.GetNthFiducialPosition(i,seedPoint_ras)
      print(seedPoint_ras)
      seedPoint_ras.append(1)
      seedPoint_ijk = mat.MultiplyPoint(seedPoint_ras)
      seedPoint_ijk = [int(x) for x in seedPoint_ijk[0:3]]
      segmentationFilter.AddSeed(seedPoint_ijk)
      #print("Adding seed at: ", seedPoint_ijk, " with intensity: ", inputImage.GetPixel(*seedPoint_ijk))

    #Run segmentation filter
    intermediateSegmentation = segmentationFilter.Execute(inputImage)
    #print(outputImage)


    #Fill holes of segmentation
    fillHoleFilter = sitk.BinaryFillholeImageFilter()
    fillHoleFilter.SetForegroundValue(1)
    outputImage = fillHoleFilter.Execute(intermediateSegmentation)
    print("The class type of outputImage is: "+ str(type(outputImage)))
    outputImageName = outputLabelMap.GetName()#'outputImageFirstTry'
    print(outputImageName)
    sitkUtils.PushToSlicer(outputImage, outputImageName,2,True) #2=label image, True = overwrite is true

    """
    #Convert output of filter from scalar volume node to label map
    volumesLogic = slicer.modules.volumes.logic()
    #volumesLogic.CreateLabelVolumeFromVolume(slicer.mrmlScene, outputLabelMap, slicer.util.getNode(outputImageName) )
    volumesLogic.CreateLabelVolumeFromVolume(slicer.mrmlScene, outputLabelMap, slicer.util.getNode(outputImageName))

    #Remove previously created scalar volume node
    nodeToRemove=slicer.util.getNode(outputImageName)
    slicer.mrmlScene.RemoveNode(nodeToRemove)
    """

    #Convert label map volume to model using Model Maker CLI module
    modelMakerParams = {}
    modelMakerParams['Name'] = outputModel.GetName()
    modelMakerParams['InputVolume'] = slicer.util.getNode(outputLabelMap.GetName()).GetID()
    modelMakerParams['FilterType'] = 'Sinc'
    modelMakerParams['StartLabel'] = -1
    modelMakerParams['EndLabel'] = -1
    modelMakerParams['GenerateAll'] = True
    modelMakerParams['JointSmoothing'] = False
    modelMakerParams['SplitNormals'] = True
    modelMakerParams['PointNormals'] = True
    modelMakerParams['SkipUnNamed'] = True
    modelMakerParams['Decimate'] = 0.25
    modelMakerParams['Smooth'] = 10
    modelMakerParams['ModelSceneFile'] = outputModel

    modelMaker = slicer.modules.modelmaker

    cliModelMakerNode = slicer.cli.run(modelMaker, None, modelMakerParams )

    """
    labelmapVolumeNode = slicer.util.getNode(outputLabelMap.GetName())
    seg = slicer.vtkMRMLSegmentationNode()
    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
    #seg.CreateClosedSurfaceRepresentation()
    slicer.mrmlScene.AddNode(seg)
    slicer.mrmlScene.RemoveNode(labelmapVolumeNode)
    """

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('SimplePhantomSegmentationTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class SimplePhantomSegmentationTest(ScriptedLoadableModuleTest):
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
    self.test_SimplePhantomSegmentation1()

  def test_SimplePhantomSegmentation1(self):
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
    logic = SimplePhantomSegmentationLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
