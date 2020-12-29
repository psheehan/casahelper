# Subtract off the continuum.

from casatasks import uvcontsub
import casatools

def sub_continuum(tracks, line_list, line_center_list, vmin=-20.0, vmax=20.0):
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
            for iline, line_center in enumerate(line_center_list):
                # Get the velocities relative to each line.
                velocities = (line_center - freqs/1e9) / line_center * 3e5

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
