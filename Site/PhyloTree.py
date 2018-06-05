import math
import numpy as np
import plotly
import os

from Bio import Phylo
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot

def PhyloMain(filename):
	target = os.path.dirname(__file__)
	path = os.path.join("test/", "NewickTree.nwk")#str(filename))

	phy = Phylo.read(os.path.join(target, path), 'newick')
	xPoint, yPoint,  xLink, yLink, xCurve, yCurve    = createPhylo(phy,  firstTerm='last')
	txt=[]
	for clade in phy.find_clades(order='level'):
		if clade.name and clade.confidence and clade.branch_length:
			txt.append(clade.name+'<br>branch-length: '+'{:4f}'.format(clade.branch_length)+
						'<br>confidence: '+'{:d}'.format(int(clade.confidence.value)))
		elif clade.name is None and clade.branch_length is not None and clade.confidence is not None:
			txt.append('<br>branch-length: '+'{:4f}'.format(clade.branch_length)+'<br>confidence: '+\
						'{:d}'.format(int(clade.confidence.value)))
		elif clade.name and clade.branch_length and clade.confidence is None:
			txt.append(clade.name+'<br>branch-length: '+'{:4f}'.format(clade.branch_length))
		else:
			txt.append('')
	drawPoint=dict(type='scatter',
					x = xPoint,
					y= yPoint,
					mode='markers',
					marker=dict(color='rgb(153,0,153)'),
					text = txt, hoverinfo='text')

	drawLinks=dict(type='scatter',
					x = xLink,
					y = yLink,
					mode='lines',
					line=dict(color='rgb(20,20,20)',
					width=1.2),
				   hoverinfo='none')

	drawCurves=dict(type='scatter',
					x = xCurve,
					y=yCurve, mode='lines',
					line=dict(color='rgb(20,20,20)',
					width=1.2,
					shape='spline'),
					hoverinfo='none')
	layout=dict(title='',
				font=dict(family='Balto',size=14),
				width=900,
				height=950,
				autosize=False,
				showlegend=False,
				xaxis=dict(showline=False,
							zeroline=False,
							showgrid=False,
							showticklabels=False,
							title=''),
				yaxis=dict(showline=False,
							zeroline=False,
							showgrid=False,
							showticklabels=False,
							title=''),
				hovermode='closest',
							plot_bgcolor='rgb(245,245,245)',
							margin=dict(t=75))

	fig=dict(data=[drawLinks, drawCurves, drawPoint], layout=layout)
	div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)
	return div

def createPhylo(phy, length=1, angleFirst=0, angleLast=360, firstTerm='first'):

	angleFirst *= math.pi/180
	angleLast *= math.pi/180

	def getYcoord(phy):
		pointTerm = phy.count_terminals()

		if firstTerm == 'first':
			pointY = dict((term, i) for i, term in enumerate(phy.get_terminals()))
		elif firstTerm == 'last':
			pointY = dict((term, i) for i, term in enumerate(reversed(phy.get_terminals())))

		def setYcoord(clade):
			for sc in clade:
				if sc not in pointY:
					setYcoord(sc)
			pointY[clade] = 0.5 * (pointY[clade.clades[0]] + pointY[clade.clades[-1]])
		if phy.root.clades:
			setYcoord(phy.root)
		return pointY

	def rad(phy):
		pointRad = phy.depths()

		if not np.count_nonzero(pointRad.values()):
			pointRad = phy.depths(unit_branch_lengths=True)
		return pointRad

	pointRad = rad(phy)
	pointYcoord = getYcoord(phy)
	pointYvalues = pointYcoord.values()
	pointYmin, pointYmax = min(pointYvalues), max(pointYvalues)
	pointYmin -= length

	def pointYpolar(py):
		return angleFirst + (angleLast - angleFirst) * (py-pointYmin) / float(pointYmax-pointYmin)

	def lineNodes(lt='radial', xNeg=0, xPos=0, yPos=0,  yDown=0, yUp=0):
		if lt == 'radial':
			ang = pointYpolar(yPos)
			x = [xNeg*math.cos(ang), xPos*math.cos(ang), None]
			y = [xNeg*math.sin(ang), xPos*math.sin(ang), None]
		elif lt == 'angular':
			angDown = pointYpolar(yDown)
			angUp = pointYpolar(yUp)
			k = np.linspace(0,1, 10)
			ang = (1-k) * angDown + k * angUp
			x = list(xPos * np.cos(ang)) + [None]
			y = list(xPos * np.sin(ang)) + [None]
		return x,y

	def lineNodeLst(clade,  xNeg,  xLink, yLink, xCurve, yCurve):
		xPos = pointRad[clade]
		yPos = pointYcoord[clade]
		x,y = lineNodes(lt='radial', xNeg = xNeg, xPos = xPos, yPos = yPos)
		xLink.extend(x)
		yLink.extend(y)
		if clade.clades:
			yUp = pointYcoord[clade.clades[0]]
			yDown = pointYcoord[clade.clades[-1]]
			x,y = lineNodes(lt='angular',  xPos=xPos, yDown=yDown, yUp = yUp)
			xCurve.extend(x)
			yCurve.extend(y)

			for desc in clade:
				lineNodeLst(desc, xPos, xLink, yLink, xCurve, yCurve)

	xLink=[]
	yLink=[]
	xCurve=[]
	yCurve=[]
	lineNodeLst(phy.root,  0, xLink, yLink, xCurve, yCurve)
	xPoint=[]
	yPoint=[]

	for clade in phy.find_clades(order='level'):
		ang = pointYpolar(pointYcoord[clade])
		xPoint.append(pointRad[clade]*math.cos(ang))
		yPoint.append(pointRad[clade]*math.sin(ang))

	return xPoint, yPoint,  xLink, yLink, xCurve, yCurve
