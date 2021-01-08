# Script to split science targets from a calibrated MS file produced by NRAO.

from casahelper.utils import Track, get_bands
from casahelper.tasks import split_objects
import os

# Create the track instance.

track = Track('file') # For file named file.ms

# Split off the science data.

for band in get_bands(track, intent="*OBSERVE_TARGET*"):
    split_objects(track, outdir=os.environ["HOME"]+"/Documents/Objects", \
            band=band, clobber=False, corr="LL,RR", datacolumn="corrected")
