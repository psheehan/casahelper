from casaplotms import plotms

# Before getting started, define a procedure which will plot the calibration
# in a way I'm happy with so that I don't have to type it over and over again.

def plotcal(caltable=None, xaxis=None, yaxis=None, iteraxis='antenna', \
        coloraxis='spw'):
    filename = caltable+"."+yaxis+"."+iteraxis+".calplots.png"
    
    if yaxis == 'phase':
        plotrange = [0,0,-180,180]
    elif yaxis == 'amp':
        plotrange = []

    plotms(vis=caltable, xaxis=xaxis, yaxis=yaxis, iteraxis=iteraxis,\
            coloraxis=coloraxis, spw='', gridrows=7, gridcols=7, showgui=False,\
            plotfile=filename, plotrange=plotrange, width=3000, height=3000,\
            dpi=300, overwrite=True)
