from casatasks import tclean, exportfits

def image_continuum(group, combined=None, robust=[-1,0.5,2], nsigma=3.0, \
        fits=False):
    # Check whether a list of tracks was provided.

    if type(group) != list:
        if combined != None:
            combined = group

        group = [group]

    # Check to make sure robust is a list.

    if type(robust) != list:
        robust = [robust]

    # Now loop through the requested robust values and image.

    for robust_value in robust:
        tclean(vis=[track.ms for track in group], spw=[track.spw for track in \
                group], field=[track.science for track in group], \
                imagename=combined.image+"_robust{0:3.1f}".format(robust), \
                specmode='mfs', nterms=1, niter=combined.niter, gain=0.1, \
                nsigma=nsigma, imsize=combined.imsize, cell=combined.cell, \
                stokes='I', deconvolver='hogbom', gridder='standard', \
                weighting='briggs', robust=robust_value, interactive=False, \
                pbcor=False, usemask=track.mask, \
                sidelobethreshold=combined.sidelobethreshold, \
                noisethreshold=combined.noisethreshold, \
                lownoisethreshold=combined.lownoisethreshold, \
                minbeamfrac=combined.minbeamfrac, fastnoise=False, \
                verbose=True, pblimit=-0.2)

        # Export the relevant images to fits files if requested.

        if fits:
            exportfits(imagename=combined.image+"_robust{0:3.1f}.image".format(\
                    robust), fitsimage=combined.image+"_robust{0:3.1f}.fits".\
                    format(robust))

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
