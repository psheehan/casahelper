# Tool to estimate image parameters.

from .Track import Track
from .get_spwsforband import get_spwsforband
from .get_bands import get_bands
import casatools
import numpy

def image_advice(track=None, fieldofview="30arcsec", mask="auto-multithresh", \
        array="ALMA-auto", usepercentile=80):
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

    # Create a dictionary to put the advice.

    advice = {}

    # Get the imager advice on cells and npix.

    if filename != None:
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

        # Estimate the beam size from the baseline at the 80th percentile.

        l80 = numpy.percentile(baselines, 80)

        beam = 0.574 / l80 / 4.8481e-6

        # Use the beam size to calculate the appropriate cell size.

        cell = beam / 2

        advice["cell"] = str(cell/5)+"arcsec"
        advice["imsize"] = max(64, int(float(fieldofview.split("a")[0])/ \
                (cell) / 10 + 1)*10)*5

    # Add the mask.

    advice["mask"] = mask

    # Add auto-multithresh parameters based on the array.

    if mask == "auto-multithresh":
        # If we've asked for automatic characterization.

        if array == "ALMA-auto":
            if filename == None:
                raise RuntimeError("For auto selecting of auto-multithresh "
                        "parameters, a filename must be provided.")
            else:
                # Use the 75th percentile baseline to determine the array.

                b75 = numpy.percentile(baselines*3e8/mean_freq, 75)

                if b75 < 45:
                    array = "ALMA-ACA"
                elif b75 < 300:
                    array = "ALMA-SB"
                else:
                    array = "ALMA-LB"

        # Now, get the auto-masking parameters.

        if array == "ALMA-LB":
            advice["sidelobethreshold"] = 3.0
            advice["noisethreshold"] = 5.0
            advice["lownoisethreshold"] = 1.5
            advice["minbeamfrac"] = 0.3
        elif array == "ALMA-SB":
            advice["sidelobethreshold"] = 2.0
            advice["noisethreshold"] = 4.25
            advice["lownoisethreshold"] = 1.5
            advice["minbeamfrac"] = 0.3
        elif array == "ALMA-ACA":
            advice["sidelobethreshold"] = 1.25
            advice["noisethreshold"] = 5.0
            advice["lownoisethreshold"] = 2.0
            advice["minbeamfrac"] = 0.1
        elif array == "VLA":
            advice["sidelobethreshold"] = 1.5
            advice["noisethreshold"] = 5.0
            advice["lownoisethreshold"] = 2.0
            advice["minbeamfrac"] = 0.1
        else:
            raise ValueError(array+" is not a recognized option with default "
                    "auto-masking settings.")

    return advice
