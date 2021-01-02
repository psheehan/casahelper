from ..utils import Track, TrackGroup
from casatasks import mstransform, concat
import casatools
import os

def export_continuum(data, chan=True, nchannels=4, time=True, timebin="30s", \
        datacolumn="corrected"):
    # Create instances of the needed tools.

    msmd = casatools.msmetadata()

    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
        combine = False
    elif type(data) == TrackGroup:
        tracks = data.tracks
        combine = True
        combined = data
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

    # Loop through the tracks and average.

    for track in tracks:
        if not os.path.exists(track.vis):
            msmd.open(track.ms)

            nbins = []
            for i in msmd.spwsforfield(int(track.science)):
                nbins += [int(msmd.chanfreqs(i).size / nchannels)]

            msmd.done()

            mstransform(vis=track.ms, outputvis=track.vis, spw=track.spw, \
                    chanaverage=chan, chanbin=nbins, timeaverage=time, \
                    timebin=timebin, datacolumn=datacolumn)

    # Also concatenate into a single file.

    if combine:
        concat(vis=[track.vis for track in tracks], concatvis=combined.vis)

    # Clean up any files we don't want anymore.

    os.system("rm -rf concat.last mstransform.last")
