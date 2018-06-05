import os
from bokeh.io import output_notebook, show
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.resources import CDN, INLINE
from bokeh.embed import components, file_html
from bokeh.util.string import encode_utf8
import squarify
from bokeh.palettes import Paired, magma, Plasma256, viridis, linear_palette, Category20
import json
from ete3 import Tree

p = figure(plot_width=600, plot_height=600)
border_x = 0
border_y = 0
border_width = 0
border_height = 0

def TreeMain(filename):
	target = os.path.dirname(__file__)
	path = os.path.join("test/", str(filename))

	#import file to t
	global t
	t = Tree(os.path.join(target, path), format=1)

	plot = Temp(t)
	return components(plot)


def TraverseTree(node, MyBorder):
	if node.is_root():
		MyBorder = border_x, border_y, border_width, border_height
		DrawTree([len(node)], MyBorder)
		for i in range(0,len(node.get_children())):
			ParentBorder = MyBorder
			TraverseTree(node.children[i], ParentBorder)

	elif node.is_leaf() == False  & node.is_root() == False:
		for i in range(0,len(node.get_children())):
			ParentBorder = MyBorder
			TraverseTree(node.children[i], ParentBorder)

def Temp(node):
	NodeHeight = []
	for i in node.traverse():
		NodeHeight.append(len(i))
	#DrawTree(NodeHeight,0,0,500,700)
	return DrawTree(NodeHeight,0,0,500,700)

def DrawTree(vals, ParentBorderLeft, ParentBorderBottom, ParentBorderRight, ParentBorderTop):
	# these values define the coordinate system for the returned rectangles
	# the values will range from x to x + width and y to y + height
	border_x = ParentBorderLeft
	border_y = ParentBorderBottom
	border_width = ParentBorderRight
	border_height = ParentBorderTop

	values = vals

	# values must be sorted descending (and positive, obviously)
	values.sort(reverse=True)

	# the sum of the values must equal the total area to be laid out
	values = squarify.normalize_sizes(values, border_width, border_height)
	rects = squarify.squarify(values, border_x, border_y, border_width, border_height)

	#values assigned to coordinates
	top = []
	bottom = []
	left = []
	right = []
	#colors = []
	for i in range(len(rects)):
		top.append(rects[i].get("dy"))
		bottom.append(rects[i].get("y"))
		left.append(rects[i].get("x"))
		right.append(rects[i].get("dx"))
		#colors.append(Category20[i])
	top = [x + y for x, y in zip(bottom, top)]
	right = [x + y for x, y in zip(left, right)]

	#plot figure
	p = figure(plot_width=800, plot_height=500)
	p.quad(top = top,
	   bottom = bottom ,
	   left = left,
	   right= right,
	   color= viridis(len(rects)),
	line_color = 'white',
	line_width = 2,
	 	)
	p.grid.visible = False
	p.axis.visible = False
	return p
