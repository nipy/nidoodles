.. _viz_tasks:

============================
 Common Visualization Tasks
============================

Below is a list of common visualization tasks done in neuroimaging.
Common or desired visualization features are also mixed in.


2D visualization
----------------

* View MRI in any canonical plane

  * Orthogonal slice views axial, sagittal, coronal of same brain (SPM
    like).

* View MRI in any combination of arbitrary slices
* View cutouts of an MRI with any angle of the cutouts
* Take intersections between surfaces and volumes via slices
* Yoke interactions between multiple slice planes.  Or disable yoked
  interactions.

Overlays
^^^^^^^^

* Overlay image slices
* Overlay surface outlines on slices
* Overlay activation(s), labels(ROIs) on any of the above

3D visualization
----------------

* Cut planes
* Cortical surfaces
* Tractography
* Anatomical connectivity
* ECoG
* 3D/2D yoking
* Activation isosurfaces

* Colocate points between volumes and surfaces:
   
  Two windows, one showing slices (let's say in cardinal orientations)
  and one showing a surface. When I click on the surface it takes
  me/highlights to intersection of the cardinal planes at that
  point. When I click on the volume it takes me to/highlights the
  closest surface point.
 
* Overlay curvature, thickness maps on surfaces
* Edit labels on volumes and surfaces
* Edit regions as nurbs on surfaces

ROI Drawing
-----------
* Editing/Drawing
* Picking
* Masking

Misc
----

* Light box / mosaic views:

  * View same slice from multiple volumes.
  * View all slices from same volume.

* Time series animations
* Maximum intensity projection
* Profile view, 1D intensity plot of a picked image scan-line

  * Example image from Mike Trumpis' viewer:
  
    .. image:: ../images/mike_viewer.png

* Horizontal, vertical and temporal profiles with a prespecified width.

  Horizontal and vertical profiles should integrate the data across
  this width, temporal profiles should integrate the data across a
  rectangular region.  This isn't obviously necessary for fmri
  studies, but it is extremely useful when looking for image
  artfiacts.  AFNI's time profiles are frustratingly close to this,
  but they don't integrate over a region.

* Load multiple datasets at once so that switching between datasets
  can be done with a single button click.  That's the best way to
  compare two nearly identical images but it isn't as easy as it
  should be with most packages.

* Linkage to web resources (pubmed, atlases)
* Registration analysis and verification

* Can we view a BOLD time series?
* Can we view effect sizes instead of T-maps?
* Can view effect sizes with contour-lines of T-maps?
* Can we edit our anatomical ROIs?
* Can we display the results on surfaces?
* Can we display our results with our ROIs on volumes and surfaces?
* Can we edit our ROIs on surfaces?
* Can we display DTI tracks?
* Can we display FA images?
* Can we visualize the sensitivity profiles of the different coils
  simultaneously?
* Can we visualize SWI veinograms?



