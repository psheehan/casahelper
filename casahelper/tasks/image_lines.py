# Image the spectral line data.

from casatasks import tclean, exportfits
from ..utils import get_line_info, Track, TrackGroup, get_spwsforline
import numpy
import glob
import os

def image_lines(data, lines, combined=None, robust=[-1,0.5,2], start='-20km/s',\
        width='0.5km/s', nchan=41, outframe='LSRK', nsigma=3.0, fits=False, \
        parallel=False, savespace=False):
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

    # Check whether a list of lines was provided.

    if type(lines) == str:
        lines = get_line_info([lines])
    elif type(lines) == list:
        lines = get_line_info(lines)
    else:
        if type(lines) != dict:
            raise ValueError("Lines must be a string, list of strings, or "
                    "a dictionary.")

    # Check to make sure robust is a list.

    if type(robust) != list:
        robust = [robust]

    # Loop through the lines and robust values and make an image.

    for line in lines:
        if numpy.all(numpy.array([get_spwsforline(track, line) for \
                track in tracks]) == ''):
            print("#############################")
            print("")
            print("Skipping ",line," because no valid SPWs were found.")
            print("")
            print("#############################")
            continue

        for robust_value in robust:
            print("#############################")
            print("")
            print("Imaging ",line," with robust parameter ",robust_value)
            if "SPW" not in line:
                print("Line frequency = "+str(lines[line])+"GHz")
            print("spw = ",[get_spwsforline(track, line) for track in tracks])
            print("")
            print("#############################")

            # Make sure previous instances are deleted.
            if len(glob.glob(combined.image.replace(combined.band,\
                    line)+"_robust{0:3.1f}".format(robust_value)+".*")) > 0:
                os.system("rm -rf "+combined.image.replace(combined.band,\
                    line)+"_robust{0:3.1f}".format(robust_value)+".*")

            tclean(vis=[track.contsub for track in tracks], \
                    spw=[get_spwsforline(track,line) for \
                    track in tracks], field=[track.science for track in \
                    tracks], imagename=combined.image.replace(combined.band,\
                    line)+"_robust{0:3.1f}".format(robust_value), \
                    specmode='cube', start=start, width=width, nchan=nchan, \
                    restfreq=str(lines[line])+"GHz" if "SPW" not in line \
                    else '', outframe=outframe, \
                    nterms=1, niter=int(10*combined.niter), gain=0.1, \
                    nsigma=nsigma, imsize=combined.imsize, cell=combined.cell, \
                    stokes='I', deconvolver='hogbom', gridder='standard', \
                    weighting='briggs', robust=robust_value, \
                    interactive=False, pbcor=False, usemask=combined.mask, \
                    sidelobethreshold=combined.sidelobethreshold, \
                    noisethreshold=combined.noisethreshold, \
                    lownoisethreshold=combined.lownoisethreshold, \
                    minbeamfrac=combined.minbeamfrac, fastnoise=False, \
                    verbose=True, pblimit=-0.2, parallel=parallel)

            # Export the relevant images to fits files.

            if fits:
                exportfits(imagename=combined.image.replace(combined.band,\
                        line)+"_robust{0:3.1f}.image".format(robust_value), \
                        fitsimage=combined.image.replace(combined.band,line)+\
                        "_robust{0:3.1f}.fits".format(robust_value))

            if savespace:
                ext_list = [".mask",".model",".pb",".psf",".sumwt"]
                if fits:
                    ext_list += [".image"]

                for ext in ext_list:
                    os.system("rm -rf "+combined.image.replace(combined.band,\
                            line)+"_robust{0:3.1f}"+ext)

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
