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

import numpy as np

from nipy.io.api import load_image

from image import ImageData, _slice_planes

class MatplotlibImage(object):
    def __init__(self, figure, data=None):
        self.fig = figure
        if data is None:
            # fill in data with small array to create plots
            self.data = np.empty((100, 100), dtype='int16')
        
    def set_data(self, data):
        raise NotImplementedError

    def draw(self):
        """Force canvas to redraw the axes."""
        if self.fig.canvas is not None:
            self.fig.canvas.draw()


class SingleImage(MatplotlibImage):
    """Matplotlib figure with a single Axes object."""

    def __init__(self, figure, data=None):
        """Update a matplotlib figure with one subplot.

        Parameters
        ----------
        fig : matplotlib.figure.Figure object
        data : array-like, optional

        """
        super(SingleImage, self).__init__(figure, data)
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


class VolumeImage(object):
    """Matplotlib figure with 3 Axes' showing a full volumne."""
    def __init__(self, figure, data=None):
        super(VolumeImage, self).__init__(figure, data)
        #self.axes = self.fig.add_subplot(2,2,1)
        for plt in range(3):
            self.fig.add_subplot(2, 2, plt+1)
            self.fig.gca().imshow(self.data, origin='lower', 
                                  interpolation='nearest',
                                  cmap=cm.gray)

    def set_data(self, data):
        """Update data in matplotlib figure."""
        raise NotImplementedError


class MainWindow(HasTraits):
    """Main window for the viewer."""
    # Traited attributes
    figure = Instance(Figure)
    slice_index_low = Int(0)   # These have to be trait ints or they don't work
    slice_index_high = Int(91) # with the dynamic updating of the Range slider.
    slice_index = Range(low='slice_index_low',
                        high='slice_index_high')
    slice_plane = Enum('Axial', 'Sagittal', 'Coronal')
    affine = Array(Float, (4,4))

    def __init__(self, filename):
        # XXX: Need to remove dependency of filename on construction
        # soon.  Already some of the calls below depend on this.  User
        # should be able to open the app and then specify the file.
        super(MainWindow, self).__init__()
        self.img = None
        self.filename = filename
        self.img_plot = SingleImage(self.figure)
        self.load_image(self.filename)
        self.update_image_slicing()
        self.image_show()
                

    def load_image(self, filename):
        self.img = load_image(filename)
        self.filename = filename
        # Make sure our image is in a standard nifti space so we can
        # access slice planes easily.  Note this can be slow for large
        # images!
        #self.img = coerce2nifti(tmpimg, standard=True)
        self.update_affine()
        self.update_slice_index()

    def update_affine(self):
        self.affine = self.img.affine
        
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
        self.update_image_slicing()
        self.image_show()

    #
    # Data Model methods
    #
    def update_image_slicing(self):

        # XXX: BUG: self.slice_index is set by the slider of the
        # current slice.  When we switch the slice plane, this index
        # may be outside the range of the new slice.  Need to handle
        # this.

        if self.slice_plane == 'Axial':
            #data = self.img[self.slice_index, :, :]
            data = _axial_nifti_slice(self.img, self.slice_index)
            self.img_plot.set_data(data)
            high = self.img.shape[0]
        elif self.slice_plane == 'Sagittal':
            #data = self.img[:, :, self.slice_index]
            data = _sagittal_nifti_slice(self.img, self.slice_index)
            self.img_plot.set_data(data)
            high = self.img.shape[1]
        elif self.slice_plane == 'Coronal':
            #data = self.img[:, self.slice_index, :]
            data = _coronal_nifti_slice(self.img, self.slice_index)
            self.img_plot.set_data(data)
            high = self.img.shape[2]
        else:
            raise AttributeError('Unknown slice plane')
        # update range slider
        self.slice_index_low = 0
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
            self.load_image(dlg.path)
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


def _axial_nifti_slice(img, zindex, xlim=None, ylim=None, t=0):
    """Return axial slice of the image. Assume xyzt ordering."""
    
    if img.ndim is 4:
        img = img[:, :, :, t]
    #xdim, ydim, zdim = img.shape
    if xlim is None:
        xlim = slice(None)
    if ylim is None:
        ylim = slice(None)
    return img[xlim, ylim, zindex]

def _coronal_nifti_slice(img, yindex, xlim=None, zlim=None, t=0):
    """Return coronal slice of the image."""

    if img.ndim is 4:
        img = img[:, :, :, t]
    if xlim is None:
        xlim = slice(None)
    if zlim is None:
        zlim = slice(None)
    return img[xlim, yindex, zlim]

def _sagittal_nifti_slice(img, xindex, ylim=None, zlim=None, t=0):
    """Return sagittal slice of the image."""

    if img.ndim is 4:
        img = img[:, :, :, t]
    if not ylim:
        ylim = slice(None)
    if not zlim:
        zlim = slice(None)
    return img[xindex, ylim, zlim]


if __name__ == '__main__':
    fsl_fn = os.path.expanduser('~/local/fsl/data/standard/avg152T1.nii.gz')
    MainWindow(fsl_fn).configure_traits() #view='volume_view'

