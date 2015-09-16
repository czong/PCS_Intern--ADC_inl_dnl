#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

########## SYSTEM ###############
import sys
import gc
from scipy import stats
from scipy.interpolate import interp1d
from numpy import *
from pdb import set_trace
import traceback
from chaco.api import Plot, ArrayPlotData
from traits.api import *
from traitsui.api import *
from enable.api import ComponentEditor
from sklearn import linear_model

import wx

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from traits.api import Any, Instance
from traitsui.wx.editor import Editor
from traitsui.wx.basic_editor_factory import BasicEditorFactory



contents = open('dc.csv').read()
contents = contents.split('\n')
contents = [_ for _ in contents if _]
contents = [ _.split(',') for _ in contents]
contents = [ (float(_.strip()), float(__.strip())) for _, __ in contents]



x = [_[0] for _ in contents]
y = [_[1] for _ in contents]

min_i = 5500
max_i = 22300
x=x[min_i:max_i]
y=y[min_i:max_i]
x=array(x)
y=array(y)

class _MPLFigureEditor(Editor):
	scrollable = True

	def init(self,parent):
		self.control = self._create_canvas(parent)
		self.set_tooltip()
	
	def update_editor(self):
		pass

	def _create_canvas(self,parent):
		""" Create the MPL canvas."""
		# the panel lets us add additional controls.
		panel = wx.Panel(parent,-1,style=wx.CLIP_CHILDREN)
		sizer = wx.BoxSizer(wx.VERTICAL)
		panel.SetSizer(sizer)
		# matplotlib commands to create a canvas
		mpl_control = FigureCanvas(panel,-1,self.value)
		sizer.Add(mpl_control,1,wx.LEFT |wx.TOP |wx.GROW)
		toolbar = NavigationToolbar2Wx(mpl_control)
		sizer.Add(toolbar,0,wx.EXPAND)
		self.value.canvas.SetMinSize((10,10))
		return panel

class MPLFigureEditor(BasicEditorFactory):
	klass = _MPLFigureEditor


class LinearPlot(HasTraits):
	#plot = Instance(Plot)
	figure = Instance(Figure, ())
	traits_view = View(
		VGroup(
			Item('figure',editor = MPLFigureEditor(),show_label=False),
		),
		width = 1200,
		height = 900,
		resizable=True,
		title='linearPlot'
	)
	
	def __init__(self):
		super(LinearPlot,self).__init__()
		# linear regression fitting and predict y_fit
		regr = linear_model.LinearRegression()
		regr.fit(x[:,newaxis],y)		
		y_fit = regr.predict(x[:,newaxis])
		
		bits=11	
		onebit = 1.0/(2**bits)
		stepsz = (max(y)-min(y))/len(y)
		nsteps_per_lsb = onebit/stepsz
		total_lsb_steps = int(len(y)/nsteps_per_lsb)
		steps_either_side = int(nsteps_per_lsb/2)
		centers = [int(round(nsteps_per_lsb*_)) for _ in range(total_lsb_steps)]
		dnl = [average(y[centers[hi]-steps_either_side:centers[hi]+steps_either_side])-average(y[centers[low]-steps_either_side:centers[low]+steps_either_side]) for low, hi in zip(range(total_lsb_steps-1),range(1,total_lsb_steps))]
		dnl = array(dnl)
		dnl = (dnl-onebit)/onebit
		lower = -int(len(dnl)/2)
		upper = lower+len(dnl)
		dnl_x = array(range(lower,upper))
		print("x:",len(x))
		print("dnl:",len(dnl))
		#lower = -int(len(dnl)/2)
		#upper = lower+len(dnl)
		inl = (y-y_fit)/onebit	
		#print("Coefficients:\n",regr.coef_)
		#print("intercept:\n",regr.intercept_)

		axes1 = self.figure.add_subplot(311)
		axes1.plot(x,regr.predict(x[:,newaxis]),color='blue')
		axes1.scatter(x,y,color='red')
		axes1.set_title('fitting')
		axes1.set_xlim(x[0],x[-1])		
		
		axes2 = self.figure.add_subplot(312)
		axes2.plot(x,inl,color='red')
		axes2.set_title('INL')
		axes2.set_xlim(x[0],x[-1])		

		axes3 = self.figure.add_subplot(313)
		axes3.plot(dnl_x,dnl,color='red')	
		axes3.set_title('DNL')
		axes3.set_xlim(lower,upper)
		#plt.scatter(x,y,color='red')
		#plt.plot(x,regr.predict(x[:,newaxis]),color='blue',linewidth=3)
		#plt.xticks(())
		#plt.yticks(())
		#plt.show()



if __name__ == "__main__":
	LinearPlot().configure_traits()
