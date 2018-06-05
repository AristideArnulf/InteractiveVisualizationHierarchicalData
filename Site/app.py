import os
import TreeMap
import TreeMapTest
import PhyloTree
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

	script, div = TreeMapTest.TreeTestMain(filename)
	phylot = PhyloTree.PhyloMain(filename)


	#Return the plot to html
	return render_template("complete.html", script=script, div=div, phylot=phylot)

if __name__ == "__main__":
	app.run(port=4555, debug=True)
