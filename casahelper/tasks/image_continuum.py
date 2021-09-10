from ..utils import Track, TrackGroup
from casatasks import tclean, exportfits, imstat
import os

def image_continuum(data, robust=[-1,0.5,2], nsigma=3.0, fits=False, \
        savemodel=False, suffix="_robust{0:3.1f}", uvtaper=[], nterms=1):
    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
        combine = False
        combined = data
    elif type(data) == TrackGroup:
        tracks = data.tracks
        combine = True
        combined = data
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

    # Check to make sure robust is a list.

    if type(robust) != list:
        robust = [robust]

    # Check whether we asked for multiple Taylor terms.

    if nterms >= 2:
        terms_suffix = ".tt0"
    else:
        terms_suffix = ""

    # Now loop through the requested robust values and image.

    for robust_value in robust:
        tclean(vis=[track.ms for track in tracks], spw=[track.spw for track in \
                tracks], field=[track.science for track in tracks], \
                imagename=combined.image+suffix.format(robust_value), \
                specmode='mfs', nterms=nterms, niter=combined.niter, gain=0.1, \
                nsigma=nsigma, imsize=combined.imsize, cell=combined.cell, \
                stokes='I', deconvolver='hogbom', gridder='standard', \
                weighting='briggs', robust=robust_value, interactive=False, \
                pbcor=False, usemask=combined.mask, \
                sidelobethreshold=combined.sidelobethreshold, \
                noisethreshold=combined.noisethreshold, \
                lownoisethreshold=combined.lownoisethreshold, \
                minbeamfrac=combined.minbeamfrac, fastnoise=False, \
                verbose=True, pblimit=-0.2, uvtaper=uvtaper)

        if savemodel:
            model_empty = imstat(imagename=combined.image+suffix.\
                    format(robust_value)+".model"+terms_suffix)["max"] == 0

            if not model_empty:
                tclean(vis=[track.ms for track in tracks], spw=[track.spw for \
                        track in tracks], field=[track.science for track in \
                        tracks], imagename=combined.image+suffix.format(\
                        robust_value), specmode='mfs', nterms=nterms, niter=0, \
                        gain=0.1, nsigma=nsigma, imsize=combined.imsize, \
                        cell=combined.cell, stokes='I', deconvolver='hogbom', \
                        gridder='standard', weighting='briggs', \
                        robust=robust_value, interactive=False, \
                        pbcor=False, usemask=combined.mask, \
                        sidelobethreshold=combined.sidelobethreshold, \
                        noisethreshold=combined.noisethreshold, \
                        lownoisethreshold=combined.lownoisethreshold, \
                        minbeamfrac=combined.minbeamfrac, \
                        savemodel="modelcolumn", calcres=False, calcpsf=False, \
                        fastnoise=False, verbose=True, pblimit=-0.2, \
                        uvtaper=uvtaper)

        # Export the relevant images to fits files if requested.

        if fits:
            exportfits(imagename=combined.image+suffix.format(robust_value)+\
                    ".image"+terms_suffix, fitsimage=combined.image+\
                    suffix.format(robust_value)+".fits")

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
