# Tool to estimate image parameters.

from .Track import Track
import casatools

def image_advice(track=None, fieldofview="30arcsec", mask="auto-multithresh", \
        array="ALMA-auto"):
    # Check that the value provided for track is appropriate.

    if type(track) == Track:
        filename = track.ms
    elif type(track) == str:
        filename = track
    else:
        filename = None

    # Create an instance of the imager tool.

    im = casatools.imager()

    # Create a dictionary to put the advice.

    advice = {}

    # Get the imager advice on cells and npix.

    if filename != None:
        im.open(filename)
        initial_advice = im.advise(fieldofview=fieldofview)
        im.close()

        advice["imsize"] = initial_advice[1]*3
        advice["cell"] = str(initial_advice[2]["value"]/3) + \
                initial_advice[2]["unit"]

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
                cell = initial_advice[2]["value"]

                if cell > 2:
                    array = "ALMA-ACA"
                elif cell > 0.2:
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
