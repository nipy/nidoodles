""" This is a temporary placeholder until the Nipy Image class is
fully functional.  Much of this code started as a way to access the
axial, coronal, and sagittal slices as I build the UI.  Once the guts
of the UI are working, this code shold be replaced with proper nipy
code.  It is assumed the image array is in TZYX order! (the current
nipy ordering)
"""

import numpy as np

from nipy.io.api import load_image

_slice_planes = ['Axial', 'Sagittal', 'Coronal']

# Nifti orientation codes from nifti1_io.h
NIFTI_L2R = 1    # Left to Right
NIFTI_R2L = 2    # Right to Left
NIFTI_P2A = 3    # Posterior to Anterior
NIFTI_A2P = 4    # Anterior to Posterior
NIFTI_I2S = 5    # Inferior to Superior
NIFTI_S2I = 6    # Superior to Inferior

class ImageData(object):
    def __init__(self):
        self.data = np.random.random((100, 100))
        self.img = None
        self.filename = None
        self.curr_slice_plane = _slice_planes[0]
        self.curr_slice_index = 0
        self.axes_order = None

    def load_image(self, filename):
        self.img = load_image(filename)
        self.filename = filename
        print 'Opening file:', filename
        self.axes_order = self._axes_order_from_orientation()
        self.set_slice_plane()

    def set_slice_plane(self, plane=None):
        if plane is None:
            plane = self.curr_slice_plane
        self.curr_slice_plane = plane
        if plane is _slice_planes[0]:
            self.data = self._axial_slice(self.curr_slice_index)
        elif plane is _slice_planes[1]:
            self.data = self._sagittal_slice(self.curr_slice_index)
        elif plane is _slice_planes[2]:
            self.data = self._coronal_slice(self.curr_slice_index)
        else:
            raise IndexError('Unknown slice plane:' % plane)

    def set_slice_index(self, index=0):
        if self.curr_slice_index != index:
            # XXX Need to check the index is in the range of the slice axes.
            self.curr_slice_index = index
            self.set_slice_plane()

    def get_affine(self):
        """Return 4x4 affine."""
        # Currently 4D images in nipy have a 5x5 affine.  Remove the
        # time component.
        if self.img.ndim == 4:
            return self.img.affine[1:, 1:]
        else:
            return self.img.affine

    def get_range(self):
        #
        # DEBUG NOTE: capsuled.nii.gz image orientation is [4,5,1]
        #   shape is (160, 256, 240) - x, z, y
        #   data and orientation is in y, z, x order
        #

        # XXX: The order of the img.shape is reversed from the
        # orientation order.  Need to sort this out more later.
        # Flipping them with the '2-index' works for all the images I
        # tested on, which had various orientations.
        axs = dict([(k, 2-v) for k, v in self.axes_order.iteritems()])
        if self.curr_slice_plane is _slice_planes[0]:
            # Axial
            return (0, self.img.shape[axs['z']] - 1)
        elif self.curr_slice_plane is _slice_planes[1]:
            # Sagittal
            return (0, self.img.shape[axs['x']] - 1)
        elif self.curr_slice_plane is _slice_planes[2]:
            # Coronal
            return (0, self.img.shape[axs['y']] - 1)

    def _axes_order_from_orientation(self):
        # XXX Should not be digging into the pynifti object.
        orient = self.img._data.orientation
        # Determine the orientation of the image, which axes map to the
        # indices 0, 1, and 2.
        try:
            xindx = orient.index(NIFTI_L2R)
        except ValueError:
            xindx = orient.index(NIFTI_R2L)
        try:
            yindx = orient.index(NIFTI_P2A)
        except ValueError:
            yindx = orient.index(NIFTI_A2P)
        try:
            zindx = orient.index(NIFTI_I2S)
        except ValueError:
            zindx = orient.index(NIFTI_S2I)

        return {'x':xindx, 'y':yindx, 'z':zindx}

    def _orient_map(self, x, y, z, t):
        # Get orientation of image.  

        # XXX Should not be digging into the pynifti object.
        orient = self.img._data.orientation

        # XXX: Use roll axis to roll the time dim to the end for 4D
        # images.  Do this instead of the _make_3d function.  All other
        # functions can ignore the index order.
        # tmp = np.rollaxis(data, 0, 4)

        #img = _make_3d(img, t)

        # Determine the orientation of the image, which axes map to the
        # indices 0, 1, and 2.
        try:
            xindx = orient.index(NIFTI_L2R)
        except ValueError:
            xindx = orient.index(NIFTI_R2L)
        try:
            yindx = orient.index(NIFTI_P2A)
        except ValueError:
            yindx = orient.index(NIFTI_A2P)
        try:
            zindx = orient.index(NIFTI_I2S)
        except ValueError:
            zindx = orient.index(NIFTI_S2I)
        # Create a mapping of our orienation indices with the slicing
        index_slicing = {xindx:x, yindx:y, zindx:z}

        # XXX: Need to look into this orientation further.  Eventually
        # this should all be handled in the Image Class.  I had to flip
        # the axes_order (hence the 2-indx) in order to get the correct
        # length of each axis.  Not clear what's going on the with order.
        axes_order = {'x':2-xindx, 'y':2-yindx, 'z':2-zindx}
        return index_slicing, axes_order

    def _index_slice(self, x, y, z, t):
        index_slicing, axes_order = self._orient_map(x, y, z, t)
        # Slice the image using the orientation mapping 
        return self.img[index_slicing[2], index_slicing[1], index_slicing[0]]

    def _axial_slice(self, zindex):
        """Return axial slice of the image. Assume tzyx ordering."""
        slice_order = {self.axes_order['x']:slice(None),
                       self.axes_order['y']:slice(None),
                       self.axes_order['z']:zindex}
        return self.img[slice_order[2], slice_order[1], slice_order[0]]

    def _sagittal_slice(self, xindex):
        """Return sagittal slice of the image."""
        slice_order = {self.axes_order['x']:xindex,
                       self.axes_order['y']:slice(None),
                       self.axes_order['z']:slice(None)}
        return self.img[slice_order[2], slice_order[1], slice_order[0]]

    def _coronal_slice(self, yindex):
        """Return coronal slice of the image."""
        slice_order = {self.axes_order['x']:slice(None),
                       self.axes_order['y']:yindex,
                       self.axes_order['z']:slice(None)}
        return self.img[slice_order[2], slice_order[1], slice_order[0]]


"""
def _make_3d(img, t=0):
    if img.ndim is 4:
        # BUG: When I slice a nipy Image, I get back a nipy Image.
        # However, the new image is created from an array and
        # coordmap, and no longer associated with a file or header.
        # As a result the orientation information I attempt to use
        # later in _index_slice is no longer available.
        img = img[t, :, :, :]
    return img
"""
