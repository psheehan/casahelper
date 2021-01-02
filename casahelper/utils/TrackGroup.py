# Define which combinations of fields and spectral windows are used for 
# various things.

class TrackGroup:
    def __init__(self, trackname, tracks, name='cont', cell=None, \
            imsize=None, mask='', niter=100, sidelobethreshold=3.0, \
            noisethreshold=5.0, minbeamfrac=0.3, lownoisethreshold=1.5):
        self.ms = trackname+'.ms'
        self.contsub = trackname+'.ms.contsub'

        self.tracks = tracks

        self.name = name
        self.vis = trackname+"_"+self.name+".ms"
        self.image = trackname+"_"+name
        self.fits = self.image+".fits"
        self.residual = self.image+".residual.fits"

        if cell == None:
            self.cell = str(min([float(track.cell.split("a")[0]) for track in \
                    tracks]))+"arcsec"
        else:
            self.cell = cell

        if imsize == None:
            self.imsize = max([track.imsize for track in tracks])
        else:
            self.imsize = imsize

        self.niter = niter

        self.mask = mask

        self.sidelobethreshold = sidelobethreshold
        self.noisethreshold = noisethreshold
        self.minbeamfrac = minbeamfrac
        self.lownoisethreshold = lownoisethreshold

