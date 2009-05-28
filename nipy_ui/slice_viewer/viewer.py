"""Simple image viewer using nipy, matplotlib and traits.  

The purpose of this code was to learn traits and explore the GUI
functionality in comparison with wxWidgets.  It was not written with
the intent of being used as a long term tool.
"""

import os

from enthought.traits.api import (HasTraits, Instance, Int, Range, Enum, Str,
                                  Array, Float, on_trait_change)
from enthought.traits.ui.api import (View, Item, Group, HSplit, Handler, 
                                     VSplit, EnumEditor, ArrayEditor)
from enthought.traits.ui.menu import (Action, StandardMenuBar, Menu, MenuBar)
from enthought.pyface.api import FileDialog, OK, CANCEL
from enthought.pyface.action.api import MenuBarManager, MenuManager

from mpl_figure import MPLFigureEditor
from matplotlib.figure import Figure
import matplotlib.cm as cm

from image import ImageData, _slice_planes

class SingleImage(object):
    """Matplotlib figure with a single Axes object."""

    def __init__(self, figure, data):
        """Update a matplotlib figure with one subplot.

        Parameters
        ----------
        fig : matplotlib.figure.Figure object
        data : array-like

        """
        super(SingleImage, self).__init__(figure, data)
        self.fig = figure
        self.data = data
        self.axes = self.fig.add_subplot(111)
        self.axes.imshow(self.data, origin='lower', interpolation='nearest',
                         cmap=cm.gray)
        
    def set_data(self, data):
        """Update data in the matplotlib figure."""
        self.axes.images[0].set_data(data)
        # BUG: When we slice the nipy image, data is still a
        # nipy image but the _data attr is now a numpy array, not
        # a pyniftiio object.  We take advantage of this bug to
        # access the max and min luminance values.
        vmin = data._data.min()
        vmax = data._data.max()
        self.axes.images[0].set_clim(vmin, vmax)
        ydim, xdim = data.shape
        self.axes.set_xlim((0, xdim))
        self.axes.set_ylim((0, ydim))

    def draw(self):
        """Force canvas to redraw the axes."""
        if self.fig.canvas is not None:
            self.fig.canvas.draw()


class MainWindow(HasTraits):
    """Main window for the viewer built using Traits."""
    # Traited attributes
    figure = Instance(Figure)
    slice_index_low = Int(0)   # These have to be trait ints or they don't work
    slice_index_high = Int(91) # with the dynamic updating of the Range slider.
    slice_index = Range(low='slice_index_low',
                        high='slice_index_high')
    slice_plane = Enum(_slice_planes)
    affine = Array(Float, (4,4))

    def __init__(self):
        super(MainWindow, self).__init__()
        # Initialize our nipy image object
        self.img = ImageData()
        # Initialize our matplotlib figure
        self.img_plot = SingleImage(self.figure, self.img.data)

    #
    # Initializers for Traited attrs
    #
    def _figure_default(self):
        """Initialize matplotlib figure."""
        figure = Figure()
        return figure

    def _slice_index_default(self):
        """Initialize slice_index attr without triggering the
        on_trait_change method.
        """
        return 0


    #
    # Event handlers
    #
    @on_trait_change('slice_index, slice_plane')
    def update_slice_index(self):
        self.img.set_slice_index(self.slice_index)
        self.update_image_slicing()
        self.image_show()

    #
    # Data Model methods
    #
    def update_affine(self):
        self.affine = self.img.get_affine()
        
    def update_image_slicing(self):

        # XXX: BUG: self.slice_index is set by the slider of the
        # current slice.  When we switch the slice plane, this index
        # may be outside the range of the new slice.  Need to handle
        # this.

        if self.slice_plane == 'Axial':
            self.img.set_slice_plane(_slice_planes[0])
        elif self.slice_plane == 'Sagittal':
            self.img.set_slice_plane(_slice_planes[1])
        elif self.slice_plane == 'Coronal':
            self.img.set_slice_plane(_slice_planes[2])
        else:
            raise AttributeError('Unknown slice plane')

        # update figure data
        self.img_plot.set_data(self.img.data)

        # get range information for slider
        low, high = self.img.get_range()
        # update range slider
        self.slice_index_low = low
        self.slice_index_high = high

    def image_show(self):
        self.img_plot.draw()

    #
    # View code
    #

    # Menus
    def open_menu(self):
        dlg = FileDialog()
        dlg.open()
        if dlg.return_code == OK:
            self.img.load_image(dlg.path)
            self.update_affine()
            self.update_slice_index()
    menu_open_action = Action(name='Open Nifti', action='open_menu')

    file_menubar = MenuBar(Menu(menu_open_action,
                                name='File'))
    
    # Items
    fig_item = Item('figure', editor=MPLFigureEditor())
    # radio button to pick slice
    _slice_opts = {'Axial' : '1:Axial',
                    'Sagittal' : '2:Sagittal',
                    'Coronal' : '3:Coronal'}
    slice_opt_item = Item(name='slice_plane',
                          editor=EnumEditor(values=_slice_opts),
                          style='custom')
 
    affine_item = Item('affine', label='Affine', style='readonly')
    # BUG: The rendering with the 'readonly' style creates an ugly wx
    # "multi-line" control.

    traits_view = View(HSplit(Group(fig_item),
                              Group(affine_item,
                                    slice_opt_item,
                                    Item('slice_index'))
                              ),
                       menubar=file_menubar,
                       width=0.80, height=0.80,
                       resizable=True)

    # Status bar
    # XXX: Don't know where to import this from?  Documentation is
    # only for pyface.
    #status_bar_manager = StatusBarManager()

if __name__ == '__main__':
    MainWindow().configure_traits()

