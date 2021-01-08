from casahelper.tasks import reset_ms, flag_lines, self_calibrate, \
        image_continuum, export_continuum, sub_continuum, image_lines, \
        export_lines, clean_last
from casahelper.utils import Track, TrackGroup, get_refant, image_advice
from casatasks import flagmanager, flagdata
import glob
import os

################################################################################
#####
##### Set up the track info.
#####
################################################################################

data = glob.glob("*.ms")

# Create a list of the track objects.

tracks = []

for filename in data:
    tracks.append(Track(filename, refant=get_refant(filename), science='0', \
            spw='', niter=500, **image_advice(filename, fieldofview="30arcsec",\
            mask='auto-multithresh', array="ALMA-auto"))

# And the info for the combined tracks.

combined = TrackGroup('04287+1801', tracks, niter=5000, \
        **image_advice(mask='auto-multithresh', array="ALMA-SB")

# The list of lines in the dataset.

lines = ["13CO3-2","C18O3-2","CN3-2_72-52","CN3-2_52-32","CN3-2_52-52_7",\
        "CN3-2_52-52_3","CS7-6"]

################################################################################
#####
##### Reset the data to its initial state before we do anything.
#####
################################################################################

# Remove files that were created during the previous run of this script.

clean_last()

# Reset the MS files to their initial state.

reset_ms(combined)

################################################################################
#####
##### Flag some extra data.
#####
################################################################################

# Add manual flags here.

# Save the flags.

for track in combined.tracks:
    flagmanager(vis=track.ms, mode="save", versionname="PostManualFlagging")

# Flag lines in the FDM specral windows.

flag_lines(combined, lines, vmin=-20.0, vmax=20.0)

################################################################################
#####
##### Self-calibration.
#####
################################################################################

# Create an image of each individual dataset and determine whether to 
# self-calibrate that track.

self_calibrate(combined)

################################################################################
#####
##### Post-calibration Imaging
#####
################################################################################

# Create an image of each individual dataset.

for track in combined.tracks:
    image_continuum(track, robust=2, nsigma=3.0, fits=False)

##### Create the final image of the combined data for each group.

image_continuum(combined, robust=[-1,0.5,2], nsigma=3, fits=True)

# Create a .vis file for each of the tracks.

export_continuum(combined, chan=True, nchannels=4, time=True, timebin='30s', \
        datacolumn="corrected")

################################################################################
#####
##### Image the spectral line data.
#####
################################################################################

# Un-flag the spectral lines.

for track in combined.tracks:
    flagmanager(vis=track.ms, mode="restore", versionname="PreLineFlagging")

# Subtract off the continuum.

sub_continuum(combined, lines, vmin=-20.0, vmax=20.0)

# Re-flag the spectral lines.

for track in combined.tracks:
    flagmanager(vis=track.ms, mode="restore", versionname="PostLineFlagging")

# Loop through the groups and image.

image_lines(combined, lines, robust=2, start="-20km/s", width="0.5km/s", \
        nchan=80, outframe="LSRK", nsigma=3.0, fits=True)

# Export the visibilities.

export_lines(combined, lines, time=True, timebin="30s", mode="velocity", \
        start="-20km/s", width="0.5km/s", nchan=80, outframe="LSRK", \
        datacolumn="data")
