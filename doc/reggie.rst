.. _reggie:

========================================
 Reggie : A Graphical Registration Tool
========================================

During JB's visit in January we layed out a set of features that we
felt would make for an ideal interactive registration tool.  This tool
would allow researchers to compare and interact with registered
images, manually aligning them, etc... 


Primary Features
----------------

These are features everyone felt were important to have and therefore
would be implemented first.  :ref:`secondary_features` would be implemented
later.

Views
^^^^^

This would primarily be a 2D slice-plane viewer.  Set of views to
choose from:

- Single 2D slice-plane view
- Orthographic 2D slice-plane view (axial, coronal, sagittal)
- 2D slice-plane overlays (including images with different dimensions)
- 2D Side-by-side orthogonal slice-plane views (similar to SPM's
  *Check Reg*)
- 2D ROIs (filled or outline mode)

Manipulators
^^^^^^^^^^^^

Graphical tools for manual interaction with images.

- Sliders

  - Use case: Using sliders to manually adjust the rotation angles to
    improve the alignment of two images.
  - Sliders would probably have an editbox attached to them.

- Editbox

  - This would allow you to enter a specific transformation value, say
    for rotation.

- Rich Listbox

  - This would be similar to the GIMP layer functionality. It would allow choosing
  
    - data for overlay
    - turn overlay on or off
    - order of overlays
    - different colormap for each overlay
    - scaling of intensity range for each overlay

- Mouse: pan, rotate, zoom, contrast, brightness (a la siemens viewer)

Information
^^^^^^^^^^^

- Labelled axes

  - Clearly labeled axes, left/right, anterior/posterior,
    inferior/superior
  - Have a widget for switching between world or voxel coordinates

- Filename (and path option) clearly labelled

  - It was mentioned that in some visualization tools it can be
    difficult to determine which file you are viewing or where it is
    on disk.  We should make this simple to determine.

- Get value from picked voxel/coordinate


Transforms
^^^^^^^^^^

- View the current transform of an image.

  - View the 4x4 affine from the nifti header.
  - Should this be visible in the main display, like in SPM or should
    it be in a dialog that one has to open, like in MRIcron?

- Output the transform in a standard format

  - After some manual edits on the image alignment, it should be easy
    to save the transform to a file.
  - Reload this transform from the file.
  - Probably save the 4x4 transform as a numpy array in a .npy file. ???

- Apply a transform to other images

  - What SPM calls *reorient*
  - Option to reorient to a new file or existing file (overwrite)

Tools
^^^^^

- Contrast adjustment with slider
- Flip left/right of the image.
- Toggle Crosshairs on/off

- Undo/Redo to previous "Best Alignment"

  - User driven Bookmarked alignments.  Allow the user to bookmark a
    transform and restore it later.
  - Automatically save undo points by user chosen measure.  (A
    :ref:`secondary_features`, implement after the Bookmarked
    Alignments.)


.. _secondary_features:

Secondary Features
------------------

Lower priority features that will be implemented when the Primary
Features are completed.

- Interpolation options

  - To start with we'll just used nearest neighbor.  Later we'll add
    more.

- 3D View

  - Cortical surface-mesh  visualization with overlay for planes
  - Support for overlays on surface-meshes (activation, morphological and other properties)
  - Tensor and track visualization
  - Combining 3D surfaces with volume data might be one of the most useful ways to register structural and other images. see: http://www.ncbi.nlm.nih.gov/pubmed/19573611

- Scroll through 4D images.

  - Using a slider, scroll through time and view the image frames.
  - Ability to choose one frame to realign the other frames to.
  - Be able to see time series corresponding to some ROI

- 4D movie mode

  - Hit a button and watch the viewer walk through the frames.
  - fslview has this feature.  May be useful for finding bad frames?

- Multiple images viewed and yoked.  

  - One may want to have many views on a volume, possibly with
    different transforms applied.  Ex: original, normalized, template
    image, etc..

- Editor
  
  Being able to manipulate ROIs on surfaces and volumes

