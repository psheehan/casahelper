# Split off data for individual science targets from a calibrated MS file.

from ..utils import Track, TrackGroup, get_spwsforband
from casatasks import split
import casatools
import numpy
import os

def split_objects(data, outdir="", band="33GHz", clobber=False, corr="XX,YY", \
        datacolumn="corrected", intent="*OBSERVE_TARGET*"):
    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
        combine = False
        combined = data
    elif type(data) == TrackGroup:
        tracks = data.tracks
        combine = True
        combined = data
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

    # Create the proper instances of casa tools.

    msmd = casatools.msmetadata()

    # Loop through the tracks and export.

    for track in tracks:
        # Open the MS File that was grabbed.

        msmd.open(track.ms)

        # Split off the science data.

        for i in msmd.fieldsforintent(intent):
            # Get the object name.

            obj = msmd.fieldnames()[i].replace(" ","")

            # Check if the output directory exists. If not, create it. If the
            # split off MS file already exists, delete it.

            if not os.path.exists(outdir+"/"+obj+"/"+band):
                os.system("mkdir -p "+outdir+"/"+obj+"/"+band)
            else:
                if os.path.exists(outdir+"/"+obj+"/"+band+"/"+obj+"_"+\
                        track.ms):
                    if clobber:
                        os.system("rm -r "+outdir+"/"+obj+"/"+band+"/"+obj+"_"+\
                                track.ms+"*")
                    else:
                        raise Warning("Output file "+outdir+"/"+obj+"/"+band+\
                                "/"+obj+"_"+track.ms+" exists and clobber="
                                "False. Skipping.")

            # Now split off the relevant data.

            spw = ','.join(get_spwsforband(track, band=band, intent=intent).\
                    astype(str))

            split(vis=track.ms, datacolumn=datacolumn, spw=spw, field=str(i), \
                    correlation=corr, intent=intent, outputvis=outdir+"/"+obj+\
                    "/"+band+"/"+obj+"_"+track.ms)

        # Close the MS file that was grabbed.

        msmd.done()

    # Clean up any files we don't want anymore.

    os.system("rm -rf *.last")
