from casatasks import flagdata
import casatools

# Flag lines in the FDM specral windows.

def flag_lines(data, line_list, line_center_list, vmin=-20., vmax=20.):
    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
    elif type(data) == TrackGroup:
        tracks = data.tracks
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

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

            for iline, line_center in enumerate(line_center_list):
                # Convert frequencies to velocities.

                velocities = (line_center - freqs/1e9) / line_center * 3e5

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
                        format(spwstring, line_list[iline]))
                flagdata(vis=track.ms, mode="manual", spw=spwstring, \
                        flagbackup=False)

        msmd.close()
        ms.close()

    # Save the flags.

    for track in tracks:
        flagmanager(vis=track.ms, mode="save", versionname="PostLineFlagging")

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
