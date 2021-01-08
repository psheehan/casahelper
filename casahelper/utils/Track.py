# Define which combinations of fields and spectral windows are used for 
# various things.

from .get_bands import get_bands

class Track:
    def __init__(self, filename, spw='', refant='0', science='', band='cont', 
            cell="0.1arcsec", imsize=600, mask='', niter=100, selfcal=None, 
            spwmap=None, sidelobethreshold=3.0, noisethreshold=5.0,
            minbeamfrac=0.3, lownoisethreshold=1.5, asdm=None):
        self.ms = filename

        trackname = filename.split(".ms")[0]
        self.contsub = trackname+'.ms.contsub'
        self.asdm = asdm

        if selfcal == None:
            selfcal = []
        if spwmap == None:
            spwmap = []

        self.selfcal = selfcal
        self.selfcal_base = trackname+'.selfcal'
        self.nselfcal = len(selfcal)
        self.spwmap = spwmap

        if band == "cont":
            bands = get_bands(self.ms)
            if len(bands) > 1:
                raise RuntimeError("Track "+self.ms+" has multiple bands, but "
                        "Track objects can only have one. Please specify the "
                        "correct band using the band keyword.")
            band = bands[0]
        self.band = band

        self.vis = trackname+"_"+self.band+".vis"
        self.image = trackname+"_"+self.band
        self.fits = self.image+".fits"
        self.residual = self.image+".residual.fits"

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

