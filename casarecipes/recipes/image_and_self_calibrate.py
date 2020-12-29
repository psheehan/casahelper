from . import reset_ms, flag_lines, self_calibrate, image_continuum \
        export_continuum, sub_continuum, image_lines, export_lines
import os

def image_and_self_calibrate(group, combined, line_list=None, \
        line_center_list=None):
    # Remove files that were created during the previous run of this script.

    for fileext in ["*.selfcal*","*.fits","*.flux*","*.image","*.model", \
            "*.psf","*.residual","*.vis","*.mask","*.pb","*.pbcor","*.sumwt",\
            "*.png","*.contsub"]:
        os.system("rm -r "+fileext)

    # Reset the data to its initial state before we do anything.

    reset_ms(tracks)

    # Flag some extra data.

    # Save the flags.

    for track in tracks:
        flagmanager(vis=track.ms, mode="save", versionname="PostManualFlagging")

    # Flag lines in the FDM specral windows.

    if line_list != None:
        flag_lines(tracks, line_list, line_center_list, vmin=-20.0, vmax=20.0)

    # Create an image of each individual dataset and determine whether to 
    # self-calibrate that track.

    self_calibrate(group)

    # Create an image of each individual dataset.

    image_continuum(tracks, robust=2, nsigma=3.0, fits=False)

    ##### Create the final image of the combined data for each group.

    image_continuum(group, combined=combined, robust=[-1,0.5,2], nsigma=3, \
            fits=True)

    # Create a .vis file for each of the tracks.

    export_continuum(group, combined=combined, chan=True, nchan=4, time=True, \
            timebin='30s', datacolumn="corrected")

    # If lines are included, image them.

    if line_list != None:
        # Un-flag the spectral lines.

        for track in tracks:
            flagmanager(vis=track.ms, mode="restore", \
                    versionname="PreLineFlagging")

        # Subtract off the continuum.

        sub_continuum(tracks, line_list, line_center_list, vmin=-5.0, vmax=15.0)

        # Re-flag the spectral lines.

        for track in tracks:
            flagmanager(vis=track.ms, mode="restore", \
                    versionname="PostLineFlagging")

        # Loop through the groups and image.

        image_lines(group, line_list, line_center_list, combined=combined, \
                robust=2, start="-5km/s", width="0.25km/s", nchan=80, \
                outframe="LSRK", nsigma=3.0, fits=True)

        # Export the visibilities.

        export_lines(tracks, line_list, line_center_list, combined=combined, \
                time=True, timebin="30s", mode="velocity", start="-5km/s", \
                width="0.25km/s", nchan=80, outframe="LSRK", \
                datacolumn="corrected")

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
