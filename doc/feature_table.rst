.. _feature-table:

============================
 Feature grid for 2D viewer
============================

Each sub-section below refers to a particular feature that we might
consider implementing.  For each feature, there may be notes and
discussion about the feature, and example or two of packages with that
feature implemented.  Then there is a value for our work, out of 10, and
the relative amount of effort or time to implement, again out of 10.
Obviously we'll have to get a feel for the relative ratings, but some
rating is better than none.

Single slice-plane view
==========================

Examples: :ref:`fsl-single-slice`

* Value: 9.0
* Effort 2.0

Orthographic slice-plane view
================================

Allowing e.g. axial, coronal, sagittal.  This is the standard view used
in - for example SPM.

Examples: :ref:`fsl-ortho-slice`, :ref:`spm-ortho-slice`

* Value: 9.0
  Because it is the neuroimaging standard view.
* Effort: 3.0 
  I (MB) scored this 3.0, but have little idea of how much
  effort it would be

Yoked orthogonal slice-plane views
==================================

Allows - click in one image, crosshair moves to given point in that
image and updates orthogonal views.  The yoked view of the other image
updates to show the equivalent point in that image.

Example: :ref:`spm-checkreg`

* Value: 8.0
* Effort: 3.0

Lightbox view
=============

So-called because it is similar to the view that clinicians get from the
standard MRI / CT film print, viewed on an X-ray lightbox.

Example: :ref:`fsl-lightbox`

* Value: 5.0
* Effort: 4.0

