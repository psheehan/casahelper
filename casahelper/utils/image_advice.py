# Tool to estimate image parameters.

from .Track import Track
from .get_spwsforband import get_spwsforband
from .get_bands import get_bands
import casatools
import numpy
import sympy

def image_advice(track=None, fieldofview="30arcsec", mask="auto-multithresh", \
        array="ALMA-auto", usepercentile=80, usebeam=None):
    # Check that the value provided for track is appropriate.

    if type(track) == Track:
        filenames = [track.ms]
    elif type(track) == str:
        filenames = [track]
    elif type(track) == list:
        filenames = [t.ms if type(t) == Track else t for t in track]
    else:
        filenames = None

    # Create an instance of the imager tool.

    ms = casatools.ms()
    msmd = casatools.msmetadata()
    tb = casatools.table()

    # Create a dictionary to put the advice.

    advice = {}

    # Get the imager advice on cells and npix.

    if filenames != None:
        # Loop through the files and get baselines and frequencies.

        baselines, freqs, widths = [], [], []
        for filename in filenames:
            # Get the baselines from the dataset.

            tb.open(filename)
            spw_col = tb.getcol('DATA_DESC_ID')
            tb.close()

            ms.open(filename)
            ms.selectinit(spw_col[0])
            baselines += [ms.getdata(items=['uvdist'])['uvdist']]
            ms.close()

            # Get the frequencies and average to get the mean frequency.

            spws = get_spwsforband(filename, band=get_bands(filename)[0])

            msmd.open(filename)
            freqs += [msmd.chanfreqs(spw) for spw in spws]
            widths += [numpy.abs(msmd.chanwidths(spw)) for spw in spws]
            msmd.close()

        baselines = numpy.concatenate(baselines)
        freqs = numpy.concatenate(freqs)
        widths = numpy.concatenate(widths)

        # Average to get the mean frequency.

        mean_freq = (freqs * widths).sum() / widths.sum()

        # Convert baselines from m to lambda.

        baselines *= mean_freq / 3e8

        # Estimate the beam size from the baseline at the 80th percentile.

        l80 = numpy.percentile(baselines, 80)

        beam = 0.574 / l80 / 4.8481e-6

        if usebeam != None:
            beam = usebeam

        # Use the beam size to calculate the appropriate cell size.

        cell = beam / 2

        advice["cell"] = str(cell/5)+"arcsec"

        # If field of view is not directly specified, use the size of the
        # of the primary beam to estimate the appropriate size.

        if fieldofview == "auto":
            if array == "VLA":
                fieldofview = str(45./(mean_freq/1e9) * 1.5 * 60.)+"arcsec"

        # Now use the cell size to calculate the image size.

        imsize = max(64, int(float(fieldofview.split("a")[0])/(cell)))*5

        # If odd, add one.

        if imsize % 2 == 1:
            imsize += 1

        # Check the prime factorization to make sure this is an efficient
        # image size. If not, augment by 2 to make sure it stays even.

        while max(sympy.primefactors(imsize)) > 7:
            imsize += 2

        advice["imsize"] = imsize

    # Add the mask.

    advice["mask"] = mask

    # Add auto-multithresh parameters based on the array.

    if mask == "auto-multithresh":
        # If we've asked for automatic characterization.

        if array == "ALMA-auto":
            if filenames == None:
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
