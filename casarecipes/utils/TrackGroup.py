# Define which combinations of fields and spectral windows are used for 
# various things.

class TrackGroup:
    def __init__(self, trackname, tracks, image='', cell="0.1arcsec", \
            imsize=600, mask='', niter=100, sidelobethreshold=3.0, \
            noisethreshold=5.0, minbeamfrac=0.3, lownoisethreshold=1.5):
        self.ms = trackname+'.ms'
        self.contsub = trackname+'.ms.contsub'
        self.vis = trackname+".vis"

        self.tracks = tracks

        self.image = image
        self.fits = image+".fits"
        self.residual = image+".residual.fits"

        self.cell = cell
        self.imsize = imsize
        self.niter = niter

        self.mask = mask

        self.sidelobethreshold = sidelobethreshold
        self.noisethreshold = noisethreshold
        self.minbeamfrac = minbeamfrac
        self.lownoisethreshold = lownoisethreshold

