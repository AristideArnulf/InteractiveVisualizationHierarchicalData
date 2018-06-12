from flask import Flask, render_template
import json
import plotly
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import math
import os
from Bio import Phylo
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot


app = Flask(__name__)
app.debug = True


@app.route('/')
def index():

    def createPhylo(phy, length=1, angleFirst=0, angleLast=360, firstTerm='first'):

        angleFirst *= math.pi / 180
        angleLast *= math.pi / 180

        def getYcoord(phy):
            pointTerm = phy.count_terminals()

            if firstTerm == 'first':
                pointY = dict((term, i) for i, term in enumerate(phy.get_terminals()))
            elif firstTerm == 'last':
                pointY = dict((term, i) for i, term in enumerate(reversed(phy.get_terminals())))

            def setYcoord(cl):
                for sc in cl:
                    if sc not in pointY:
                        setYcoord(sc)
                pointY[cl] = 0.5 * (pointY[cl.clades[0]] + pointY[cl.clades[-1]])

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
            return angleFirst + (angleLast - angleFirst) * (py - pointYmin) / float(pointYmax - pointYmin)

        def lineNodes(lt='radial', xNeg=0, xPos=0, yPos=0, yDown=0, yUp=0):
            if lt == 'radial':
                ang = pointYpolar(yPos)
                x = [xNeg * math.cos(ang), xPos * math.cos(ang), None]
                y = [xNeg * math.sin(ang), xPos * math.sin(ang), None]
            elif lt == 'angular':
                angDown = pointYpolar(yDown)
                angUp = pointYpolar(yUp)
                k = np.linspace(0, 1, 10)
                ang = (1 - k) * angDown + k * angUp
                x = list(xPos * np.cos(ang)) + [None]
                y = list(xPos * np.sin(ang)) + [None]
            return x, y

        def lineNodeLst(cl, xNeg, xLink, yLink, xCurve, yCurve):
            xPos = pointRad[cl]
            yPos = pointYcoord[cl]
            x, y = lineNodes(lt='radial', xNeg=xNeg, xPos=xPos, yPos=yPos)
            xLink.extend(x)
            yLink.extend(y)
            if cl.clades:
                yUp = pointYcoord[cl.clades[0]]
                yDown = pointYcoord[cl.clades[-1]]
                x, y = lineNodes(lt='angular', xPos=xPos, yDown=yDown, yUp=yUp)
                xCurve.extend(x)
                yCurve.extend(y)

                for desc in cl:
                    lineNodeLst(desc, xPos, xLink, yLink, xCurve, yCurve)

        xLink = []
        yLink = []
        xCurve = []
        yCurve = []
        lineNodeLst(phy.root, 0, xLink, yLink, xCurve, yCurve)
        xPoint = []
        yPoint = []

        for cl in phy.find_clades(order='level'):
            ang = pointYpolar(pointYcoord[cl])
            xPoint.append(pointRad[cl] * math.cos(ang))
            yPoint.append(pointRad[cl] * math.sin(ang))

        return xPoint, yPoint, xLink, yLink, xCurve, yCurve
    # Read in the Data via Pandas
    p = Phylo.read('Data/long.tre', 'newick')
    xPoint, yPoint, xLink, yLink, xCurve, yCurve = createPhylo(p, firstTerm='last')
    txt = []
    for cl in p.find_clades(order='level'):
        if cl.name and cl.branch_length:
            txt.append(cl.name + '<br>branch-length: ' + '{:4f}'.format(cl.branch_length))
        else:
            txt.append('')
    drawPoint = dict(type='scatter', x=xPoint, y=yPoint, mode='markers', marker=dict(color='rgb(153,0,153)'),
                     text=txt, hoverinfo='text')
    drawLinks = dict(type='scatter', x=xLink, y=yLink, mode='lines', line=dict(color='rgb(20,20,20)', width=1.2),
                     hoverinfo='none')
    drawCurves = dict(type='scatter', x=xCurve, y=yCurve, mode='lines', line=dict(color='rgb(20,20,20)', width=1.2,
                                                                                  shape='spline'), hoverinfo='none')
    layout = dict(title='', font=dict(family='Droid Sans', size=14), width=900, height=950, autosize=False,
                  showlegend=False,
                  xaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, title=''),
                  yaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, title=''),
                  hovermode='closest', plot_bgcolor='rgb(245,245,245)', margin=dict(t=75))
    fig = dict(data=[drawLinks, drawCurves, drawPoint], layout=layout)
    # Create the Plotly Data Structure



        # Convert the figures to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the Template
    return render_template('layouts/index.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(port=9999, debug=True)
