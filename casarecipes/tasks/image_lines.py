# Image the spectral line data.

from casatasks import tclean

def image_lines(group, line_list, line_center_list, combined=None, \
        robust=[-1,0.5,2], start='-20km/s', width='0.5km/s', nchan=41, \
        outframe='LSRK', nsigma=3.0, fits=False):
    # Check whether a list of tracks was provided.

    if type(group) != list:
        if combined != None:
            combined = group

        group = [group]

    # Check whether a list of lines was provided.

    if type(line_list) != list:
        line_list = [line_list]
    if type(line_center_list) != list:
        line_center_list = [line_center_list]

    # Check to make sure robust is a list.

    if type(robust) != list:
        robust = [robust]

    # Loop through the lines and robust values and make an image.

    for iline, line_center in enumerate(line_center_list):
        for robust_value in robust:
            tclean(vis=[track.contsub for track in group], spw=[track.spw for \
                    track in group], field=[track.science for track in group], \
                    imagename=combined.image.replace("345GHz",line_list[iline])\
                    +"_robust{0:3.1f}".format(robust), specmode='cube', \
                    start=start, width=width, nchan=nchan, \
                    restfreq=str(line_center)+"GHz", outframe=outframe, \
                    nterms=1, niter=int(10*combined.niter), gain=0.1, \
                    nsigma=nsigma, imsize=combined.imsize, cell=combined.cell, \
                    stokes='I', deconvolver='hogbom', gridder='standard', \
                    weighting='briggs', robust=robust_value, \
                    interactive=False, pbcor=False, usemask=track.mask, \
                    sidelobethreshold=combined.sidelobethreshold, \
                    noisethreshold=combined.noisethreshold, \
                    lownoisethreshold=combined.lownoisethreshold, \
                    minbeamfrac=combined.minbeamfrac, fastnoise=False, \
                    verbose=True, pblimit=-0.2)

            # Export the relevant images to fits files.

            if fits:
                exportfits(imagename=combined.image.replace("345GHz",\
                        line_list[iline])+"_robust{0:3.1f}.image".\
                        format(robust), fitsimage=combined.image.\
                        replace("345GHz",line_list[iline])\
                        +"_robust{0:3.1f}.fits".format(robust))

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
