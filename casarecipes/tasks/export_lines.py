# Export the visibilities.

from casatasks import mstransform, concat
import casatools
import os

def export_lines(data, line_list, line_center_list, combined=None, \
        time=True, timebin="30s", mode="velocity", start="-20km/s", \
        width="0.5km/s", nchan=81, outframe="LSRK", \
        datacolumn="corrected"):
    # Create instances of the needed tools.

    msmd = casatools.msmetadata()
    ms = casatools.ms()

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

    # Loop through the tracks and export.

    for track in tracks:
        for iline, line_center in enumerate(line_center_list):
            # Check whether the averaged data file already exists.
            if not os.path.exists(track.vis.replace("345GHz",line_list[iline])):
                # Pick out the relevant SPWs for this line.

                msmd.open(track.contsub)
                ms.open(track.contsub)

                # Check which spectral windows include this line.

                spws = []
                for spw in msmd.fdmspws():
                    freqs = ms.cvelfreqs(spwids=[spw], fieldids=[0], \
                            mode="channel", outframe="LSRK")

                    if freqs.min() < line_center*1e9 < freqs.max():
                        spws.append(str(spw))

                # If multiple windows contain the line, turn on the combinespws
                # flag.
                combinespws = False
                if len(spws) > 1:
                    combinespws = True

                # Format the list of spectral windows.
                spws = ','.join(spws)
                print("Exporting spws for {0:s}: {1:s}".\
                        format(line_list[iline], spws))

                msmd.close()
                ms.close()

                # Now do the mstransform call.

                mstransform(vis=track.contsub, outputvis=track.vis.\
                        replace("345GHz", line_list[iline]), spw=spws, \
                        timeaverage=time, timebin=timebin, mode=mode, \
                        start=start, width=width, nchan=nchan, \
                        restfreq=str(line_center)+'GHz', outframe=outframe, \
                        interpolation='linear', regridms=True, \
                        datacolumn=datacolumn, combinespws=combinespws)

    # Also concatenate into a single file if requested.

    if combine:
        for iline, line_center in enumerate(line_center_list):
            concat(vis=[track.vis.replace("345GHz",line_list[iline]) for \
                    track in group], concatvis=combined.vis.replace("345GHz",\
                    line_list[iline]))

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")

