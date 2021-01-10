from casatasks import tclean, imstat, gaincal, applycal, flagmanager
from ..utils import plotcal, Track, TrackGroup
from .image_continuum import image_continuum
import casatools
import numpy
import os

# Create an image of each individual dataset and determine whether to 
# self-calibrate that track.

def self_calibrate(data, nsigma0=5.0, solint=['inf','30s','15s','inf','30s'], \
        minsnr = [5.0,5.0,5.0,5.0,5.0], gaintype=['T','T','T','T','T'], \
        calmode=['p','p','p','ap','ap'], \
        combine=['all','sideband','sideband','baseband','baseband'], \
        niter=[5000,5000,5000,5000,5000], nsigma=[5.,5.,3.,3.,3.]):

    # Create instances of the needed tools.

    msmd = casatools.msmetadata()
    tb = casatools.table()

    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
        combined = data
    elif type(data) == TrackGroup:
        tracks = data.tracks
        combined = data
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

    # First create an image of each track in the group to get the number of 
    # rounds of self calibration to try.

    selfcal = []

    for track in tracks:
        if not os.path.exists(track.image+"_selfcal0"):
            image_continuum(track, robust=2, nsigma=3., fits=False, \
                    savemodel=False, suffix="_selfcal0")

        snr = imstat(imagename=track.image+"_selfcal0.image")["max"] / \
                (1.4826 * imstat(imagename=track.image+"_selfcal0.residual")\
                ["medabsdevmed"])
        print(snr)

        if snr > 120:
            selfcal.append(4)
        elif snr > 80:
            selfcal.append(3)
        elif snr > 40:
            selfcal.append(2)
        else:
            selfcal.append(1)

    print(selfcal)

    # If any of the tracks have high enough S/N, give self-calibration a try.

    if numpy.any(numpy.array(selfcal) > 0):
        # Create an initial model.

        image_continuum(combined, robust=0.5, nsigma=nsigma0, fits=False, \
                savemodel=True, suffix="_selfcal0")

        # Check whether a model was actually calculated, or whether the model 
        # image is empty.

        model_empty = imstat(imagename=combined.image+\
                "_selfcal0.model")["max"] == 0

        # Re-run to clean down to a lower level, without adding to the model.

        if nsigma0 > 5:
            image_continuum(combined, robust=0.5, nsigma=5.0, fits=False, \
                    savemodel=False, suffix="_selfcal0")

        # Self-calibration parameters.

        if model_empty:
            print("Model is empty, setting selfcal to 0 for all.")
            selfcal = [0 for i in range(len(selfcal))]

        # Do the self-calibration.

        for i in range(max(selfcal)):
            for j, track in enumerate(tracks):
                # If this track doesn't have high enough S/N, don't 
                # self-calibrate.

                if selfcal[j] <= i:
                    continue

                # Get the proper number of spectral windows, combined in the 
                # correct way.

                msmd.open(track.ms)

                nspws = len(msmd.spwsforfield(int(track.science)))
                if combine[i] == "all":
                    spw_groups = ['']
                    new_spwmap = [0 for l in range(nspws)]
                    combine_str = "spw"

                elif combine[i] == "baseband":
                    spw_groups = [','.join(msmd.spwsforbaseband()[key].\
                            astype(str)) for key in msmd.spwsforbaseband()]
                    new_spwmap = [int(spw_groups[msmd.baseband(l)-1].
                            split(",")[0]) for l in range(nspws)]
                    combine_str = "spw"

                elif combine[i] == "sideband":
                    usb_lsb = [0 if msmd.sideband(l) < 0 else 1 for \
                            l in range(nspws)]
                    spw_groups = [",".join(numpy.where(numpy.array(usb_lsb) \
                            == key)[0].astype(str)) for key in [0,1]]
                    new_spwmap = [int(spw_groups[usb_lsb[l]].split(",")[0]) \
                            for l in range(nspws)]
                    combine_str = "spw"

                else:
                    spw_groups = ['']
                    new_spwmap = [l for l in range(nspws)]
                    combine_str = "scan"

                msmd.done()

                # Do the gain calibration.

                for l, spw_group in enumerate(spw_groups):
                    gaincal(vis=track.ms, caltable=track.selfcal_base+str(\
                            track.nselfcal+1), field=track.science, \
                            spw=spw_group, selectdata=True, solint=solint[i], \
                            refant=track.refant, minsnr=minsnr[i], \
                            gaintype=gaintype[i], calmode=calmode[i], \
                            combine=combine_str, gaintable=track.selfcal, \
                            spwmap=track.spwmap, append=bool(l))

                # Check whether the selfcal had too many flags.

                tb.open(track.selfcal_base+str(track.nselfcal+1))
                flags = tb.getcol("FLAG")
                tb.close()

                if flags.sum() / flags.size > 1./3:
                    print("Discarding "+track.selfcal_base+str(track.nselfcal+\
                            1)+" because too many solutions were flagged.")
                    # Don't try any further selfcal iterations on this track.
                    selfcal[j] = i
                    continue

                # Add the self-calibration table to the list.

                track.selfcal += [track.selfcal_base+str(track.nselfcal+1)]
                track.nselfcal += 1
                track.spwmap += [new_spwmap]

                # Make plots of the calibration tables.

                plotcal(caltable=track.selfcal[-1], xaxis='time', yaxis='phase')
                if 'a' in calmode[i]:
                    plotcal(caltable=track.selfcal[-1], xaxis='time', \
                            yaxis='amp')
                elif solint[i] != 'inf':
                    plotcal(caltable=track.selfcal[-1], xaxis='time', \
                            yaxis='phase', iteraxis='scan', coloraxis='ant1')

                # Apply the calibration.

                applycal(vis=track.ms, field=track.science, spw=track.spw, \
                        gaintable=track.selfcal, gainfield=[track.science for \
                        k in range(track.nselfcal)], \
                        interp=['linear' for k in range(track.nselfcal)], \
                        calwt=[True for k in range(track.nselfcal)], \
                        flagbackup=False, spwmap=track.spwmap, \
                        applymode='calonly')

                # Create a set of flags at this state.

                flagmanager(vis=track.ms, mode="save", \
                        versionname="PostSelfcal"+str(track.nselfcal))

            # If all of the track solutions were discarded, skip making a new
            # image.

            if max(selfcal) <= i:
                continue

            # Re-image the data before the next self-calibration iteration 

            image_continuum(combined, robust=0.5, nsigma=nsigma[i], fits=False,\
                    savemodel=True, suffix="_selfcal"+str(i+1))

            # Re-run one last time to clean down to 5 sigma, for best 
            # comparison with previous iterations.

            if nsigma[i] > 5:
                image_continuum(combined, robust=0.5, nsigma=5.0, fits=False, \
                        savemodel=False, suffix="_selfcal"+str(i+1))

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
