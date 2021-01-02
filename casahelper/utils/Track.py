# Define which combinations of fields and spectral windows are used for 
# various things.

class Track:
    def __init__(self, trackname, spw='', refant='0', science='', image='', 
            cell="0.1arcsec", imsize=600, mask='', niter=100, selfcal=[], 
            spwmap=[], sidelobethreshold=3.0, noisethreshold=5.0,
            minbeamfrac=0.3, lownoisethreshold=1.5):
        self.ms = trackname+'.ms'
        self.contsub = trackname+'.ms.contsub'
        self.vis = trackname+".vis"

        self.selfcal = selfcal
        self.selfcal_base = trackname+'.selfcal'
        self.nselfcal = len(selfcal)
        self.spwmap = spwmap

        self.image = image
        self.fits = image+".fits"
        self.residual = image+".residual.fits"

        self.science = science
        self.spw = spw
        self.refant = refant

        self.cell = cell
        self.imsize = imsize
        self.niter = niter

        self.mask = mask

        self.sidelobethreshold = sidelobethreshold
        self.noisethreshold = noisethreshold
        self.minbeamfrac = minbeamfrac
        self.lownoisethreshold = lownoisethreshold

