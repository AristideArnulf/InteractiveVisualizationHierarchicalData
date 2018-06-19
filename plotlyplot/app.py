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
    import math
    from Bio import Phylo
    from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
    init_notebook_mode(connected=True)
    import plotly
    p = Phylo.read('Data/long.tre', 'newick')

    def yCoordinate(tree):
        'Sourced from Bio.Phylo._utils'
        termCount = tree.count_terminals()
        term = list(reversed(tree.get_terminals()))
        yCoords = {term[i]: (termCount - i) for i in range(len(term))}

        def setYPos(c):
            for sc in c:
                if sc not in yCoords:
                    setYPos(sc)
            yCoords[c] = 0.5 * (yCoords[c.clades[0]] + yCoords[c.clades[-1]])

        if p.root.clades:
            setYPos(p.root)
        return yCoords

    dC = p.depths()
    yCoords = yCoordinate(p)
    minCoordValues = (min(yCoords.values()) - 1)
    maxCoordValues = max(yCoords.values())
    rangeMinMax = maxCoordValues - minCoordValues

    def angY(i):
        return (2 * math.pi) * (i - minCoordValues) / rangeMinMax

    def link(x1, x2, y1):
        ang = angY(y1)
        x = []
        y = []
        x.append(x1 * math.cos(ang))
        x.append(x2 * math.cos(ang))
        x.append(None)
        y.append(x1 * math.sin(ang))
        y.append(x2 * math.sin(ang))
        y.append(None)
        return x, y

    def curve(x2, y2, y3):
        ang1 = angY(y2)
        ang2 = angY(y3)
        k = [0.0, 0.111, 0.222, 0.333, 0.444,
             0.555, 0.666, 0.777, 0.888, 1.0]
        revk = list(reversed(k))
        for i in range(len(k)):
            k[i] *= ang1
        for i in range(len(revk)):
            revk[i] *= ang2
        ang = [a + b for a, b in zip(k, revk)]
        x = []
        y = []
        for i in range(len(ang)):
            x.append(math.cos(ang[i]))
            y.append(math.sin(ang[i]))
        for i in range(len(x)):
            x[i] *= x2
        x.append(None)
        for n in range(len(y)):
            y[n] *= x2
        y.append(None)
        return x, y

    def linkCreate(c, x1, link1=None, link2=None):
        if link1 is None:
            link1 = []
        if link2 is None:
            link2 = []
        x2 = dC[c]
        y1 = yCoords[c]
        x, y = link(x1=x1, x2=x2, y1=y1)
        link1.extend(x)
        link2.extend(y)
        i = 0
        while i < len(c):
            linkCreate(c[i], x2, link1, link2)
            i += 1
        return link1, link2

    def curveCreate(c, x1, curve1=None, curve2=None):
        if curve1 is None:
            curve1 = []
        if curve2 is None:
            curve2 = []
        if c.clades:
            x2 = dC[c]
            y3 = yCoords[c.clades[0]]
            y2 = yCoords[c.clades[-1]]
            x, y = curve(x2=x2, y2=y2, y3=y3)
            curve1.extend(x)
            curve2.extend(y)
            i = 0
            while i < len(c):
                curveCreate(c[i], x2, curve1, curve2)
                i += 1
            return curve1, curve2

    def pointCreate(point1=[], point2=[]):
        for c in p.find_clades(terminal=True, order='preorder'):
            ang = angY(yCoords[c])
            point1.append(dC[c] * math.cos(ang))
            point2.append(dC[c] * math.sin(ang))
        return point1, point2

    link1, link2 = linkCreate(p.root, 0)
    curve1, curve2 = curveCreate(p.root, 0)
    point1, point2 = pointCreate()

    txt = []
    for c in p.find_clades(order='level'):
        if c.name and c.branch_length:
            txt.append('{} {} <br>{} {:f}'.format('Name - ', c.name, 'Branch Length - ', c.branch_length))
        elif c.branch_length:
            txt.append('{} {:f}'.format('Branch Length - ', c.branch_length))
        else:
            txt.append('')
    drawPoint = dict(type='scatter', x=point1, y=point2, mode='markers',
                     marker=dict(symbol='circle', color=',rgb(153,0,153)'),
                     text=txt, hoverinfo='text')
    drawLinks = dict(type='scatter', x=link1, y=link2, mode='lines', line=dict(color='rgb(20,20,20)', width=1.2),
                     hoverinfo='none')
    drawCurves = dict(type='scatter', x=curve1, y=curve2, mode='lines', line=dict(color='rgb(20,20,20)', width=1.2,
                                                                                  shape='spline', smoothing=1.3),
                      hoverinfo='none')
    layout = dict(font=dict(family='Droid Sans', size=14), width=900, height=950, showlegend=False,
                  xaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False),
                  yaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False),
                  hovermode='closest')
    div = dict(data=[drawLinks, drawCurves, drawPoint], layout=layout)

    # Convert the figures to JSON
    graphJSON = json.dumps(div, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the Template
    return render_template('layouts/index.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(port=9999, debug=True)
