Traits or wxPython
==================

At this point, the main GUI toolkits we are trying to choose between
are wxPython and Traits UI.  Since Traits is built upon wxPython, I
suspect in the long run we'll use a combination of the two.  It is my
understanding that Enthought has a lot of wx code mixed into their
traited client applications.  This appears to be necessary to get a
solid, professional looking application.


Traits UI
---------

After spending a few days learning Traits, these are my (Chris) first
impressions.  I was using Traits version 3.0.1.

Pros:

  * Notification: Event handling is very easy.  Define a method and
    add the on_trait_change decorator and you're off.

  * Attribute Validation and Initialization: Type and bounds checking
    is easy and convenient.

  * Simple GUIs are easy.

  * Small amount of code can do a lot.  It did not take much code to
    get a few widgets up and be responsive.

Cons:

  * Documentation is lacking and the docstrings are uninformative.
    Most of the docstrings I looked at were like this from Item::

        An element in a Traits-based user interface.

    I'm regularly searching through the Traits and Traits UI docs, the
    mailing list and grepping the examples.

  * The examples are often too trivial, and only demonstrate simple
    GUIs.  For example, the menu example doesn't attach the menu to an
    application window, instead it prints a list of menu items to
    stdout.  As a result it took some experimentation to figure out
    how to create a menu.  Menu's are standard GUI components, adding
    one to my app should be easy.

  * Application level GUIs are hard.  I'm finding it hard to layout my
    widgets to get a professional looking application window.  And at
    times the default layout clips some widgets or even hides them
    completely.

  * Matplotlib: Will need to spend time learning wxPython and
    TraitsEditors in order to get a Matplolib window working smoothly.

  * BUG: The 'readonly' style for an Array Item looks terrible.

  * BUG: The editbox at the right-hand of the slider (Range Editor)
    doesn't behave as I would expect.  After entering a number you
    have to change focus (move cursor) to another widget for the value
    you entered to trigger and event.  I would expect hitting "Enter"
    to work.

  * StatusBar: I have yet to find documenation on the status bar and
    how to add one.

  * BUG: Widgets at the bottom can disappear (or not show up on open)
    on resize.  This was my initial motivation for adding a StatusBar,
    so there was always something padding the bottom of the window.
    `This cookbook example
    <http://www.scipy.org/Cookbook/EmbeddingInTraitsGUI>`_
    demonstrates the behavior.  On startup, this gui looks ok (The
    Scale sliders is a bit squished in the bottom of the window).
    Resizing the window so it's smaller causes the slider to
    disappear, or fall behind the matplotlib toolbar.

  * Sometimes the automatic layout goes wrong and applications with
    splitter windows open with some of the panels completely closed.
    For example, sometimes when I open mayavi all I see is the python
    interpreter:

      .. image:: images/mayavi2_startup_osx.png

  * Pyface: There's two apis, the old one and pyface?  I'm still a
    little confused by how pyface fits in.  The Traits User Manual
    makes no mention of pyface.  But some of the examples use it and
    was the only way I found to get some of the widgets working.


