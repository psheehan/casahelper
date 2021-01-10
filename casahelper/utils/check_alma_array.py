# Tool to estimate image parameters.

from .Track import Track
from .get_spwsforband import get_spwsforband
from .get_bands import get_bands
import casatools
import numpy

def check_alma_array(track):
    # Check that the value provided for track is appropriate.

    if type(track) == Track:
        filename = track.ms
    elif type(track) == str:
        filename = track
    else:
        filename = None

    # Create an instance of the imager tool.

    ms = casatools.ms()
    msmd = casatools.msmetadata()

    # Get the baselines from the dataset.

    ms.open(filename)
    ms.selectinit(0)
    baselines = ms.getdata(items=['uvdist'])['uvdist']
    ms.close()

    # Get the frequencies and average to get the mean frequency.

    spws = get_spwsforband(filename, band=get_bands(filename)[0])

    msmd.open(filename)
    freqs = numpy.concatenate([msmd.chanfreqs(spw) for spw in spws])
    widths = numpy.concatenate([msmd.chanwidths(spw) for spw in spws])
    msmd.close()

    mean_freq = (freqs * widths).sum() / widths.sum()

    # Convert baselines from m to lambda.

    baselines *= mean_freq / 3e8

    # Use the 75th percentile baseline to determine the array.

    b75 = numpy.percentile(baselines*3e8/mean_freq, 75)

    if b75 < 45:
        array = "ACA"
    elif b75 < 300:
        array = "SB"
    else:
        array = "LB"

    return array
