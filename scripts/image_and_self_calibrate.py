from casarecipes.tasks import reset_ms, flag_lines, self_calibrate, \
        image_continuum, export_continuum, sub_continuum, image_lines, \
        export_lines
import glob
import os

################################################################################
#####
##### Set up the track info.
#####
################################################################################

data = glob.glob("*.ms")

# Create a list of the track objects.

ACA = []
SB = []
LB = []

for filename in data:
    image_name = filename.split(".ms")[0]
    print(image_name)

    im.open(filename)
    imparams = im.advise(takeadvice=False)
    im.close()

    if imparams[2]["value"] > 2:
        cell = '0.25arcsec'
        npix = 512
        ACA.append(TrackInfo(image_name, refant=refant(filename), science='0', \
                spw='', image=image_name, cell=cell, imsize=npix, niter=500, \
                sidelobethreshold=1.25, noisethreshold=5.0, minbeamfrac=0.1, \
                lownoisethreshold=2.0, mask='auto-multithresh', selfcal=[], \
                spwmap=[]))
    elif imparams[2]["value"] > 0.2:
        cell = '0.05arcsec'
        npix = 512
        SB.append(TrackInfo(image_name, refant=refant(filename), science='0', \
                spw='', image=image_name, cell=cell, imsize=npix, niter=500, \
                sidelobethreshold=2.0, noisethreshold=4.25, minbeamfrac=0.3, \
                lownoisethreshold=1.5, mask='auto-multithresh', selfcal=[], \
                spwmap=[]))
    else:
        if "04489" in filename:
            cell = '0.01arcsec'
            sidelobethreshold = 2.0
        else:
            cell = '0.03arcsec'
            sidelobethreshold = 3.0
        npix = 1024
        LB.append(TrackInfo(image_name, refant=refant(filename), science='0', \
                spw='', image=image_name, cell=cell, imsize=npix, niter=500, \
                sidelobethreshold=sidelobethreshold, noisethreshold=5.0, \
                minbeamfrac=0.3, lownoisethreshold=1.5, \
                mask='auto-multithresh', selfcal=[], spwmap=[]))

tracks = ACA + SB + LB

# And the info for the combined tracks.

groups = []
combined_list = []
for group, name in zip([ACA, SB, LB],["ACA","SB","LB"]):
    # Skip groups that are empty.

    if len(group) == 0:
        continue

    # Set the appropriate auto-masking parameters.

    if name == "ACA":
        sidelobethreshold = 1.25
        noisethreshold = 5.0
        lownoisethreshold = 2.0
        minbeamfrac = 0.1
    elif name == "SB":
        sidelobethreshold = 2.0
        noisethreshold = 4.25
        lownoisethreshold = 1.5
        minbeamfrac = 0.3
    elif name == "LB":
        if '04489' in filename:
            sidelobethreshold = 2.0
        else:
            sidelobethreshold = 3.0
        noisethreshold = 5.0
        lownoisethreshold = 1.5
        minbeamfrac = 0.3

    # Otherwise, add to the groups list and create a combined info for them.

    groups.append(group)

    combined_list += [TrackInfo('04287+1801_345GHz_'+name, \
            image='04287+1801_345GHz_'+name, \
            cell=str(min([float(track.cell.split("a")[0]) for track in \
            group]))+"arcsec", imsize=max([track.imsize for track in group]), \
            niter=1000, sidelobethreshold=sidelobethreshold, \
            noisethreshold=noisethreshold, lownoisethreshold=lownoisethreshold,\
            minbeamfrac=minbeamfrac, mask='auto-multithresh')]

# Create a Track for all of the tracks combined, regardless of group.

everything = TrackInfo('04287+1801_345GHz', image='04287+1801_345GHz', \
        cell=str(min([float(track.cell.split("a")[0]) for track in \
        tracks]))+"arcsec", imsize=max([track.imsize for track in tracks]), \
        niter=1000, sidelobethreshold=2.0, noisethreshold=4.25, \
        minbeamfrac=0.3, lownoisethreshold=1.5, mask='auto-multithresh')

################################################################################
#####
##### Reset the data to its initial state before we do anything.
#####
################################################################################

# Remove files that were created during the previous run of this script.

for fileext in ["*.selfcal*","*.fits","*.flux*","*.image","*.model","*.psf",\
        "*.residual","*.vis","*.mask","*.pb","*.pbcor","*.sumwt","*.png",\
        "*.contsub"]:
    os.system("rm -r "+fileext)

# Reset the MS files to their initial state.

reset_ms(tracks)

################################################################################
#####
##### Flag some extra data.
#####
################################################################################

# Save the flags.

for track in tracks:
    flagmanager(vis=track.ms, mode="save", versionname="PostManualFlagging")

# Flag lines in the FDM specral windows.

if line_list != None:
    flag_lines(tracks, line_list, line_center_list, vmin=-20.0, vmax=20.0)

################################################################################
#####
##### Self-calibration.
#####
################################################################################

# Create an image of each individual dataset and determine whether to 
# self-calibrate that track.

self_calibrate(group)

################################################################################
#####
##### Post-calibration Imaging
#####
################################################################################

# Create an image of each individual dataset.

image_continuum(tracks, robust=2, nsigma=3.0, fits=False)

##### Create the final image of the combined data for each group.

image_continuum(group, combined=combined, robust=[-1,0.5,2], nsigma=3, \
        fits=True)

# Create a .vis file for each of the tracks.

export_continuum(group, combined=combined, chan=True, nchan=4, time=True, \
        timebin='30s', datacolumn="corrected")

################################################################################
#####
##### Image the spectral line data.
#####
################################################################################

# Un-flag the spectral lines.

for track in tracks:
    flagmanager(vis=track.ms, mode="restore", versionname="PreLineFlagging")

# Subtract off the continuum.

sub_continuum(tracks, line_list, line_center_list, vmin=-20.0, vmax=20.0)

# Re-flag the spectral lines.

for track in tracks:
    flagmanager(vis=track.ms, mode="restore", versionname="PostLineFlagging")

# Loop through the groups and image.

image_lines(group, line_list, line_center_list, combined=combined, \
        robust=2, start="-20km/s", width="0.5km/s", nchan=80, \
        outframe="LSRK", nsigma=3.0, fits=True)

# Export the visibilities.

export_lines(tracks, line_list, line_center_list, combined=combined, \
        time=True, timebin="30s", mode="velocity", start="-20km/s", \
        width="0.5km/s", nchan=80, outframe="LSRK", datacolumn="data")
