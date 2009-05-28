
import os
import wx

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.cm as cm

from image import ImageData, _slice_planes

# Menu IDs
ID_ABOUT=101
ID_EXIT=110
ID_OPEN=120

WIDTH = 800
HEIGHT = 600


#
# Wx code
#        
class CanvasFrame(wx.Frame):

    def __init__(self, parent=None, id=wx.ID_ANY, title="Simple wx viewer"):
        wx.Frame.__init__(self, parent, id, title, size=(WIDTH, HEIGHT))

        # Window dimensions are used to size the splitter proportions.
        window_width, window_height = self.GetSizeTuple()
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)

        # Figure Panel
        self.fig_panel = wx.Panel(self.splitter, -1)

        # Image data
        self.img = ImageData()
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.imshow(self.img.data, origin='lower', 
                                 interpolation='nearest',
                                 cmap=cm.gray)

        # First param to FigureCanvas must be self.panel or the
        # matplotlib figure doesn't resize when the window resizes!
        self.canvas = FigureCanvas(self.fig_panel, -1, self.figure)
        
        self.fig_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fig_sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.canvas.SetMinSize((100, 100))
        self.fig_panel.SetSizer(self.fig_sizer)

        #
        # Control Panel and widgets
        #
        self.ctrl_panel = wx.Panel(self.splitter, -1)
        self.ctrl_sizer = wx.BoxSizer(wx.VERTICAL)

        # affine
        box = wx.StaticBox(self.ctrl_panel, -1, 'Affine Transform:')
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.gridsizer = wx.GridSizer(4, 4, 2, 2)
        self.affine_txt = []
        for elem in range(16):
            self.affine_txt.append(wx.TextCtrl(self.ctrl_panel, -1, '0.0',
                                               size=(60, -1),
                                               style=wx.TE_READONLY))
            
        self.gridsizer.AddMany(self.affine_txt)
        bsizer.Add(self.gridsizer, 0)
        self.ctrl_sizer.Add(bsizer, 0)

        # Radio box
        self.slice_plane = wx.RadioBox(
            self.ctrl_panel, -1, "View Slice:", wx.DefaultPosition, 
            wx.DefaultSize, _slice_planes, 1, wx.RA_SPECIFY_COLS
            )
        self.Bind(wx.EVT_RADIOBOX, self.EvtSelectSlice, self.slice_plane)
        #rb.SetToolTip(wx.ToolTip("This is a ToolTip!"))
        #rb.SetLabel("wx.RadioBox")
        self.ctrl_sizer.Add(self.slice_plane, 0, wx.ALL, 10)

        # Slider 
        # wx.Slider(parent, id, value, min, max, position, size, style)
        self.slider = wx.Slider(self.ctrl_panel, -1, 0, 0, 100, (-1, -1),
                                (-1, -1), wx.SL_HORIZONTAL |
                                wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.ctrl_sizer.Add(self.slider, 0, wx.ALL, 10)
        self.ctrl_panel.SetSizer(self.ctrl_sizer)
        self.Bind(wx.EVT_SCROLL, self.EvtSlider, self.slider)

        # Add widgets to splitter
        self.splitter.SetMinimumPaneSize(10)
        self.splitter.SplitVertically(self.fig_panel, self.ctrl_panel, 
                                      int(window_width * 0.60))
        

        # Setting up the menu.
        filemenu = wx.Menu()
        #filemenu.Append(ID_ABOUT, "&About"," Information about this program")
        filemenu.Append(ID_OPEN, "&Open", "Open a document")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Event handlers for menus
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)

        self.Centre()
        self.Show(True)


    def set_affine(self, affine):
        for ind, val in enumerate(affine.flat):
            self.affine_txt[ind].ChangeValue(str(val))

    def OnExit(self, event):
        self.Close(True)

    def OnOpen(self, event):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.img.load_image(os.path.join(dirname, filename))
            self.set_affine(self.img.get_affine())
            self.update_slider()
        dlg.Destroy()
        self.update_image()

    def OnPaint(self, event):
        self.draw()

    def draw(self):
        self.canvas.draw()

    def EvtSelectSlice(self, evt):
        self.img.set_slice_plane(_slice_planes[evt.GetInt()])
        self.update_slider()
        self.update_image()

    def EvtSlider(self, evt):
        self.img.set_slice_index(self.slider.GetValue())
        self.update_image()

    def update_slider(self):
        rng = self.img.get_range()
        self.slider.SetRange(rng[0], rng[1])

    def update_image(self):
        """Update data in the matplotlib figure."""
        data = self.img.data
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
        self.draw()


class MyApp(wx.App):
    def OnInit(self):
        frame = CanvasFrame()
        frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

