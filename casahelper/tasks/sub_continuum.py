# Subtract off the continuum.

from ..utils import get_line_info, Track, TrackGroup
from casatasks import uvcontsub
import casatools
import numpy
import os

def sub_continuum(data, lines, vmin=-20.0, vmax=20.0):
    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
    elif type(data) == TrackGroup:
        tracks = data.tracks
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

    # Create instances of the necessary casatools tools.

    msmd = casatools.msmetadata()
    ms = casatools.ms()

    # Loop through the tracks to find spectral lines to avoid, and then 
    # subtract off the continuum.

    for track in tracks:
        msmd.open(track.ms)
        ms.open(track.ms)

        # Check each spectral window for relevant lines that need to be
        # excluded.
        fitspw = []
        for spw in msmd.fdmspws():
            # Get the frequencies in this spectral window.
            freqs = ms.cvelfreqs(spwids=[spw], fieldids=[0], mode="channel", \
                    outframe="LSRK")

            # Check tho see if any of these frequencies match the lines in the
            # list provided.
            spwstrings = []
            for line in lines:
                # Get the velocities relative to each line.
                velocities = (lines[line] - freqs/1e9) / lines[line] * 3e5

                # Check the range of channels corresponding to vmin and vmax.
                chanmin = numpy.argmin(numpy.abs(velocities - vmin))
                chanmax = numpy.argmin(numpy.abs(velocities - vmax))
                if chanmin > chanmax:
                    chanmin, chanmax = chanmax, chanmin
                elif chanmin == chanmax:
                    continue

                spwstring = "{0:d}~{1:d}".format(chanmin, chanmax)

                spwstrings.append(spwstring)

            fitspw.append(str(spw)+":"+';'.join(spwstrings))

        spw = ",".join(msmd.fdmspws().astype(str))

        msmd.close()
        ms.close()

        fitspw = ','.join(fitspw)
        print("fitspw = ",fitspw)

        # Do the continuum subtraction.
        uvcontsub(vis=track.ms, fitorder=0, spw=spw, combine="scan", \
                fitspw=fitspw, excludechans=True)

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
