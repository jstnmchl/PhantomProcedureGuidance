cmake_minimum_required(VERSION 2.8.9)

project(Phantom Procedure Guidance Procedure Guidance)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/Phantom Procedure Guidance")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Justin Michael (Robarts Research Institute)")
set(EXTENSION_DESCRIPTION "Tools to steamline process of implementing mock brachytherapy procedure into agar phantom. Includes simple assist for segmenting phantom target and registering plan to target based in surface registration.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/Phantom Procedure Guidance.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Phantom Procedure Guidance/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Simple Phantom Segmentation)
add_subdirectory(SimplePhantomSegmentation)
add_subdirectory(treatmentPlanRegistration)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
