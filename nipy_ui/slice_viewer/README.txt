Traits vs wxWidgets
===================

In order to learn how to use traits and compare the functionality
against using wxWidgets directly, I created a simple GUI for viewing
nifti images.  The traits-based viewer is in the trait_viewer.py
module, the wx-based viewer is in the wxviewer.py module.  Both
viewers use an image class defined in image.py to abstract out the
image handling issues.  image.py also has a class for handling some of
the matplotlib plot details.  The traits-based viewer uses a Traits
Editor that Gael wrote in mpl_figure.py.

To run the viewers::

  python trait_viewer.py

  python wxviewer.py


Functionality
-------------

There were several GUI features I specifically wanted to test out in
this exercise:

* Creating a window frame with a splitter
* General layout of the widgets
* Embedding a matplotlib figure which resizes properly with the window.
* Menus
* Some standard widgets:

  * Radio box
  * Text control
  * Slider




