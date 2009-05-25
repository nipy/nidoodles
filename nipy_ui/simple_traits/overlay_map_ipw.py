#
# fMRI Overlay Visualization with ImagePlaneWidgets
#
# Author: Per B. Sederberg <psederberg@...> 
# Copyright (c) 2009, Per B. Sederberg
# License: BSD Style.
#
# Based on various examples by Gael Varoquaux
#

import threading
import time

import numpy as np

from enthought.traits.api import HasTraits, DelegatesTo, Range, Instance, \
        on_trait_change, Array, Float, List, Bool, Enum
from enthought.traits.ui.api import View, Item, HGroup, HSplit, Group, \
     spring, RangeEditor, VGroup, VSplit
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.pipeline_base import PipelineBase
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene

from enthought.mayavi.modules.image_plane_widget import ImagePlaneWidget

from nifti import NiftiImage

class OverlayMap(HasTraits):
    """
    Use mayavi to plot three image cut planes through an fMRI volume
    and stat-map overlay.
    """
    
    # Main scene
    scene = Instance(MlabSceneModel, ())

    # the image planes and lookup tables
    overlays = List(Instance(ImagePlaneWidget))
    underlays = List(Instance(ImagePlaneWidget))
    over_lut = Instance(HasTraits)
    under_lut = Instance(HasTraits)

    # lower range of the overlay lookup table
    _over_low_min = Float(0.0)
    _over_low_max = Float(0.1)
    over_low = Range(low='_over_low_min', high='_over_low_max',
                     value=0.0, mode='slider')

    # upper range of the overlay lookup table
    _over_hi_min = Float(0.0)
    _over_hi_max = Float(0.1)
    over_hi = Range(low='_over_hi_min', high='_over_hi_max',
                     value=0.01, mode='slider')


    # Whether to see x,y,z planes
    x_visible = Bool(True)
    y_visible = Bool(True)
    z_visible = Bool(True)

    # Which colormap to use 
    colormap = Enum("hot", 
                    "jet",
                    "autumn")
    
    def __init__(self, under_image, over_image):
        """
        Provide the underlay and overlay NiftiImages.  Can also
        provide filename strings.

        Example:

        stat = OverlayMap('anat.nii.gz','stat.nii.gz')
        """
        # we've got traits
        HasTraits.__init__(self)

        # load in the image
        if isinstance(under_image, NiftiImage):
            # use it
            self.__under_image = under_image
        elif isinstance(under_image, str):
            # load from file
            self.__under_image = NiftiImage(under_image)
        else:
            raise ValueError("under_image must be a NiftiImage or a file.")

        # TODO: set the extent and spacing of the under image

        # set the over data
        if isinstance(over_image, str):
            # load from file
            over_image = NiftiImage(over_image)

        if isinstance(over_image, NiftiImage):
            # TODO: make sure it matches the dims of under image
            # TODO: set the extent
            
            # save just the dat
            self.__over_image = over_image.data.T

        elif isinstance(over_image, np.ndarray):
            # just set it
            # assumes it matches the dims and extent of the under image
            self.__over_image = over_image

        else:
            raise ValueError("over_image must be a NiftiImage, ndarray, or file.")

        self.__over_image = np.ma.masked_invalid(self.__over_image)

        self.configure_traits()
        pass

    def _plane_callback1(self, widget, event):
	    self._update_planes(0)

    def _plane_callback2(self, widget, event):
	    self._update_planes(1)

    def _plane_callback3(self, widget, event):
	    self._update_planes(2)

    def _update_planes(self,num):
        # set the underlay positions.
        
        # TODO: it may make more sense to do this in the callback for
        # each individual plane when it is called instead of all at
        # once

        #for i in range(len(self.overlays)):
	#if widget == self.overlays[i]:
            #    print "widget is overlay", i
	    #elif widget == self.underlays[i]:
            #    print "widget is underlay", i
	    #else:
	    #    print "widget", widget
                

            # from what I can tell, all these are necessary
        self.underlays[num].ipw.update_traits()
        self.overlays[num].ipw.origin = self.underlays[num].ipw.origin
        self.overlays[num].ipw.point1 = self.underlays[num].ipw.point1
        self.overlays[num].ipw.point2 = self.underlays[num].ipw.point2
        self.overlays[num].ipw.update_traits()
        self.overlays[num].ipw.update_placement()
        #self.overlays[num].scene.render()
                      
    @on_trait_change('scene.activated')
    def _create_plot(self):
        # shorten things a bit
        mlab = self.scene.mlab

        # generate the scalar_fields
        over = mlab.pipeline.scalar_field(np.ma.masked_invalid(self.__over_image).filled(0))
        #over_thresh = mlab.pipeline.threshold(over,low=self.__over_image.mean())
        under = mlab.pipeline.scalar_field(np.ma.masked_invalid(self.__under_image.data.T).filled(0))

        # create the planes for the x,y,z axes
        self.underlays = []
        self.overlays = []
        for orient in ['x_axes','y_axes','z_axes']:
            # first the underlay
            # TODO: fix the slice_index, which is a hack
            under = mlab.pipeline.image_plane_widget(under,colormap='gray',
                                                     slice_index=92,
                                                     plane_opacity=0,
                                                     plane_orientation=orient)
            # set up the lookup table
            under.ipw.user_controlled_lookup_table = True
            if self.under_lut is None:
                # set it
                self.under_lut = under.module_manager.scalar_lut_manager.lut
            else:
                # use it
                under.module_manager.scalar_lut_manager.lut.table = self.under_lut.table

            # add the interaction event
	    if orient == "x_axes":
                under.ipw.add_observer("InteractionEvent", self._plane_callback1)
	    elif orient == "y_axes":
                under.ipw.add_observer("InteractionEvent", self._plane_callback2)
	    else:
                under.ipw.add_observer("InteractionEvent", self._plane_callback3)
            
            # add it to the list
            self.underlays.append(under)

            # set up the overlay
            # TODO: fix the slice_index, which is a hack
            over = mlab.pipeline.image_plane_widget(over,
                                                    colormap=self.colormap,
                                                    slice_index=92,
                                                    plane_opacity=0,
                                                    plane_orientation=orient)
            # set the lookup table
            over.ipw.user_controlled_lookup_table = True
            if self.over_lut is None:
                # is first one, so set it with alpha at bottom
                lut = over.module_manager.scalar_lut_manager.lut.table.to_array()
                lut[:40, -1] = np.linspace(0,255,40)
                over.module_manager.scalar_lut_manager.lut.table = lut
                self.over_lut = over.module_manager.scalar_lut_manager.lut
            else:
                # use it
                over.module_manager.scalar_lut_manager.lut.table = self.over_lut.table

            # turn off the interaction
            over.ipw.interaction = False
            # append 
            self.overlays.append(over)

        # set the overlay upper bounds range
        over_min = np.ma.masked_invalid(self.__over_image).min()
        over_max = np.ma.masked_invalid(self.__over_image).max()
        over_mean = np.ma.masked_invalid(self.__over_image).mean()
        print "mmm:", over_min, over_max, over_mean
        self._over_hi_min = float(over_min) #self.__over_image.min()
        self._over_hi_max = float(over_max) #self.__over_image.max()
        self.over_hi = over_max #self.__over_image.max()

        # set the overlay lower bounds range
        self._over_low_min = float(over_min) #self.__over_image.min()
        self._over_low_max = float(over_max) #self.__over_image.max()
        self.over_low = over_mean #self.__over_image.mean()

    #@on_trait_change('over_hi')
    def _over_hi_changed(self):
        if self.over_hi < self.over_low:
            # set low to be hi
            self.over_low = self.over_hi
        else:
            # update the range
            self._update_overlay_range()
        
    #@on_trait_change('over_low')
    def _over_low_changed(self):
        if self.over_low > self.over_hi:
            # set hi to be low
            self.over_hi = self.over_low
        else:
            # update the range
            self._update_overlay_range()
        
    def _update_overlay_range(self):
        # XXX: Do I need to copy here?
        new_range = self.overlays[0].module_manager.scalar_lut_manager.data_range.copy()
        new_range[0] = self.over_low
        new_range[1] = self.over_hi
        for i in range(len(self.overlays)):
            self.overlays[i].module_manager.scalar_lut_manager.data_range = new_range

    def _x_visible_changed(self):
        # toggle the proper plane on or off
        self._update_plane_visible(0,self.x_visible)
    def _y_visible_changed(self):
        # toggle the proper plane on or off
        self._update_plane_visible(1,self.y_visible)
    def _z_visible_changed(self):
        # toggle the proper plane on or off
        self._update_plane_visible(2,self.z_visible)

    def _update_plane_visible(self, plane_id, bool_val):
        self.underlays[plane_id].visible = bool_val
        self.overlays[plane_id].visible = bool_val

    def _colormap_changed(self):
        print self.colormap
        for o in self.overlays:
            #TODO: Change colormap, don't know how exactly
            #print o.module_manager.scalar_lut_manager.lut
            pass

    # define the view
    view = View(
        VSplit(
            Group(Item('scene', editor=SceneEditor(scene_class=MayaviScene), 
                       height=500, width=500, show_label=False)),
            Group(
                Group(Item('over_low', label="Lower Thresh"),
                      Item('over_hi', label="Upper Thresh"),
                      label="Overlay Properties",
                      show_border=True),
            ),
            Group(
                HGroup(Item('x_visible'),
                       Item('y_visible'),
                       Item('z_visible'),
                       Item('colormap'),
                       label="Plane visibility + colormap",
                       show_border=True),
            ),
        ),
        resizable=True,
        title='Overlay Viewer')
    

if __name__ == "__main__":

    # let's try it out
    # XXX: This will break without files there
    stat = OverlayMap(under_image=NiftiImage('/home/thorsten/struct_brain.nii.gz'),
                      over_image=NiftiImage('/home/thorsten/struct_brain.nii.gz'))
    #stat = OverlayMap(under_image=NiftiImage('TT_icbm452.nii.gz'),
    #                  over_image=NiftiImage('stats.nii.gz'))

