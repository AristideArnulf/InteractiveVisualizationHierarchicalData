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

#Define Figure
p = figure(plot_width=800, plot_height=500)
Border = []
Colors = viridis(15)
a = 0


def TreeTestMain(filename):
	target = os.path.dirname(__file__)
	path = os.path.join("test/", str(filename))

	#import file to t
	global t
	t = Tree(os.path.join(target, path), format=1)
	BuildTree(t)
	return components(p)

def BuildTree(node):
    global a
    if node.is_root():
        TempBorder = [0,0,500,700]
        ParentCoordinates = GetCoor([len(node)], TempBorder)
        RootColor = Colors[a]
        a = a+1
        Border.append(ParentCoordinates[0])
        Drawing(ParentCoordinates[0], RootColor)
        TraverseNode(node)

    elif node.is_leaf() == False  & node.is_root() == False:
        TraverseNode(node)

def TraverseNode(node):
    global a
    weights = []
    NodeBorder = Border[-1]
    NodeBorder[0] = NodeBorder[0]+10
    NodeBorder[1] = NodeBorder[1]+10
    NodeBorder[2] = NodeBorder[2]-10
    NodeBorder[3] = NodeBorder[3]-10

    for i in range(0,len(node.get_children())):
        weights.append(len(node.children[i]))
    ChildCoordinates = GetCoor(weights, NodeBorder)
    for i in range(0,len(node.get_children())):
        ChildColor = Colors[a]
        a = a+1
        Drawing(ChildCoordinates[i], ChildColor)
        Border.append(ChildCoordinates[i])
        BuildTree(node.children[i])
        del Border[-1]

def GetCoor(vals, MyBorder):
    # these values define the coordinate system for the returned rectangles
    # the values will range from x to x + width and y to y + height
    border_x = MyBorder[0]
    border_y = MyBorder[1]
    border_width = MyBorder[2]-MyBorder[0]
    border_height = MyBorder[3]-MyBorder[1]

    values = vals

    # values must be sorted descending (and positive, obviously)
    values.sort(reverse=True)

    # the sum of the values must equal the total area to be laid out
    values = squarify.normalize_sizes(values, border_width, border_height)
    rects = squarify.squarify(values, border_x, border_y, border_width, border_height)

    #values assigned to coordinates
    rect = []
    for i in range(len(rects)):
        temp = []
        temp.append(rects[i].get("x"))
        temp.append(rects[i].get("y"))
        temp.append(rects[i].get("dx")+rects[i].get("x"))
        temp.append(rects[i].get("dy")+rects[i].get("y"))
        rect.append(temp)
    return rect

def Drawing(Coordinates, color):
    p.quad(top = Coordinates[3],
       bottom = Coordinates[1] ,
       left = Coordinates[0],
       right = Coordinates[2],
       color = color,
           line_color = 'white',
           line_width = 3,)
    p.grid.visible = False
    p.axis.visible = False

def SetUpColor(node):
    counter = 0
    for i in node.traverse("postorder"):
        counter += 1
    return counter
