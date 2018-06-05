import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

__author__ = 'Frank luiken'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/index.html")
def index2():
	return render_template('index.html')

@app.route("/upload")
def uploadData():
	return render_template('upload.html')

@app.route("/uploaded", methods=['POST', 'GET'])
def uploaded():

	plot=0

	target = os.path.join(APP_ROOT, 'test/')
	print(target)
	if not os.path.isdir(target):
		os.mkdir(target)
	print(request.files.getlist("file"))
	for upload in request.files.getlist("file"):
		print(upload)
		print("{} is the file name".format(upload.filename))
		filename = upload.filename
		# This is to verify files are supported
		ext = os.path.splitext(filename)[1]
		if (ext == ".tre" or ".nwk"):
			print("File supported moving on...")
		else:
			render_template("Error.html", message="Files uploaded are not supported...")
		destination = "/".join([target, filename])
		print("Accept incoming file:", filename)
		print("Save it to:", destination)
		upload.save(destination)

	#BOKEH PLOT TEST!!!!!

	import pandas as pd
	import numpy as np
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

	target = os.path.dirname(__file__)
	path = ("test/Newicktree.nwk")

	#import file to t
	from ete3 import Tree
	t = Tree(os.path.join(target, path), format=1)

	p = figure(plot_width=600, plot_height=600)
	border_x = 0
	border_y = 0
	border_width = 0
	border_height = 0

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
		DrawTree(NodeHeight,0,0,500,700)

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
		   color= viridis(len(rects)))
		print(p)

	plot = Temp(t)
	print(plot)

	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()

	script, div = components(p)

	# return send_from_directory("images", filename, as_attachment=True)
	return render_template("complete.html", script=script, div=div, js_resources=js_resources, css_resources=css_resources)

if __name__ == "__main__":
	app.run(port=4555, debug=True)
