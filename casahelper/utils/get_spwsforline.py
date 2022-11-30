from .get_line_info import get_line_info
from .Track import Track
import casatools 
import numpy

def get_spwsforline(track, line):
    # Check that the value provided for track is appropriate.

    if type(track) == Track:
        filename = track.contsub
    elif type(track) == str:
        filename = track
    else:
        raise ValueError("track must be a Track or string.")

    # Create instances of the tools we'll need.

    msmd = casatools.msmetadata()
    ms = casatools.ms()

    # If the line is "SPW*", simply return the relevant spw.

    if "SPW" in line:
        msmd.open(filename)
        if int(line[3:]) in msmd.fdmspws():
            msmd.close()
            return line.split("SPW")[1]
        else:
            msmd.close()
            return ''

    # Check whether a list of lines was provided.

    if type(line) == str:
        lines = get_line_info([line])
    else:
        raise ValueError("Lines must be a string")

    # Open the track with each tool.
    
    msmd.open(filename)
    ms.open(filename)

    # Check each FDM spectral window for lines in the line list.

    spws = []

    for spw in msmd.fdmspws():
        if len(msmd.intentsforspw(spw)) == 0:
            continue
        print(spw)

        # Get the channel frequencies in the LSRK frame, where we typically
        # know the velocities.

        freqs = ms.cvelfreqs(spwids=[spw], fieldids=[0], mode="channel", \
                outframe="LSRK")

        # Check whether the line is in the spw or not.

        chan = numpy.argmin(numpy.abs(freqs/1e9 - lines[line]))

        if chan > 0 and chan < freqs.size-1:
            spws.append(str(spw))
        else:
            continue

    msmd.close()
    ms.close()

    return ",".join(spws)
