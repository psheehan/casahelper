from ..utils import get_line_info, Track, TrackGroup
from casatasks import flagdata, flagmanager
import casatools
import numpy
import os

# Flag lines in the FDM specral windows.

def flag_lines(data, lines, vmin=-20., vmax=20.):
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

    # Create the proper instances of casa tools.

    msmd = casatools.msmetadata()
    ms = casatools.ms()

    # Save the flags before additional flagging.

    for track in tracks:
        flagmanager(vis=track.ms, mode="save", versionname="PreLineFlagging")

    # Loop through the tracks and flag the lines.

    for track in tracks:
        # Open the track with each tool.
        
        msmd.open(track.ms)
        ms.open(track.ms)

        # Check each FDM spectral window for lines in the line list.

        for spw in msmd.fdmspws():
            # Get the channel frequencies in the LSRK frame, where we typically
            # know the velocities.

            freqs = ms.cvelfreqs(spwids=[spw], fieldids=[0], mode="channel", \
                    outframe="LSRK")

            # Check which channels fall in the appropriate velocity range 
            # around the line center.

            for line in lines:
                # Convert frequencies to velocities.

                velocities = (lines[line] - freqs/1e9) / lines[line] * 3e5

                # Find which channels are closest to vmin and vmax.

                chanmin = numpy.argmin(numpy.abs(velocities - vmin))
                chanmax = numpy.argmin(numpy.abs(velocities - vmax))
                if chanmin > chanmax:
                    chanmin, chanmax = chanmax, chanmin
                elif chanmin == chanmax:
                    continue

                spwstring = "{0:d}:{1:d}~{2:d}".format(spw, chanmin, chanmax)

                # Flag the channels that were identified.

                print("Flagging SPW {0:s} because of line {1:s}".\
                        format(spwstring, line))
                flagdata(vis=track.ms, mode="manual", spw=spwstring, \
                        flagbackup=False)

        msmd.close()
        ms.close()

    # Save the flags.

    for track in tracks:
        flagmanager(vis=track.ms, mode="save", versionname="PostLineFlagging")

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
