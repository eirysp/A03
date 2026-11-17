# trace generated using paraview version 6.1.1
#import paraview
#paraview.compatibility.major = 6
#paraview.compatibility.minor = 1

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Open FOAM Reader'
stokes_wavefoam = OpenFOAMReader(registrationName='stokes_wave.foam', FileName='/home/eproselkov/openfoam/A03/A03/runs/original/stokes_wave/stokes_wave.foam')

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

renderView1.ResetActiveCameraToPositiveY()

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# set active source
SetActiveSource(stokes_wavefoam)

# show data in view
stokes_wavefoamDisplay = Show(stokes_wavefoam, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
stokes_wavefoamDisplay.Representation = 'Surface'

# show color bar/color legend
stokes_wavefoamDisplay.SetScalarBarVisibility(renderView1, True)

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D('p')

# set scalar coloring
ColorBy(stokes_wavefoamDisplay, ('CELLS', 'alpha.water'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
stokes_wavefoamDisplay.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
stokes_wavefoamDisplay.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'alphawater'
alphawaterLUT = GetColorTransferFunction('alphawater')

# get opacity transfer function/opacity map for 'alphawater'
alphawaterPWF = GetOpacityTransferFunction('alphawater')

# get 2D transfer function for 'alphawater'
alphawaterTF2D = GetTransferFunction2D('alphawater')

# create a new 'Annotate Time'
annotateTime1 = AnnotateTime(registrationName='AnnotateTime1')

# Properties modified on stokes_wavefoam
stokes_wavefoam.CellArrays = ['U', 'alpha.water', 'p', 'p_rgh']

# show data in view
stokes_wavefoamDisplay = Show(stokes_wavefoam, renderView1, 'UnstructuredGridRepresentation')

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# show color bar/color legend
stokes_wavefoamDisplay.SetScalarBarVisibility(renderView1, True)

# show data in view
annotateTime1Display = Show(annotateTime1, renderView1, 'TextSourceRepresentation')

# update the view to ensure updated data information
renderView1.Update()

# get layout
layout1 = GetLayout()

# layout/tab size in pixels
layout1.SetSize(926, 606)

# current camera placement for renderView1
renderView1.Set(
    CameraPosition=[25.0, -120.49459192762143, -6.25],
    CameraFocalPoint=[25.0, 0.25, -6.25],
    CameraViewUp=[0.0, 0.0, 1.0],
    CameraParallelScale=31.25099998400051,
)

# save animation
SaveAnimation(filename='/home/eproselkov/openfoam/A03/A03/runs/original/stokes_wave/stokes_wave_alpha_from_paraview.avi', viewOrLayout=renderView1, location=16, ImageResolution=[924, 604],
    FrameRate=10,
    FrameWindow=[0, 199])

#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(926, 606)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.Set(
    CameraPosition=[25.0, -120.49459192762143, -6.25],
    CameraFocalPoint=[25.0, 0.25, -6.25],
    CameraViewUp=[0.0, 0.0, 1.0],
    CameraParallelScale=31.25099998400051,
)


##--------------------------------------------
## You may need to add some code at the end of this python script depending on your usage, eg:
#
## Render all views to see them appears
# RenderAllViews()
#
## Interact with the view, usefull when running from pvpython
# Interact()
#
## Save a screenshot of the active view
# SaveScreenshot("path/to/screenshot.png")
#
## Save a screenshot of a layout (multiple splitted view)
# SaveScreenshot("path/to/screenshot.png", GetLayout())
#
## Save all "Extractors" from the pipeline browser
# SaveExtracts()
#
## Save a animation of the current active view
# SaveAnimation()
#
## Please refer to the documentation of paraview.simple
## https://www.paraview.org/paraview-docs/nightly/python/
##--------------------------------------------