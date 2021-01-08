import casatools 
import numpy

def get_bands(track, intent="*OBSERVE_TARGET*"):
    # Check that the value provided for track is appropriate.

    if type(track) == str:
        filename = track
    else:
        raise ValueError("Data must be a string.")

    # Create instances of the tools we'll need.

    msmd = casatools.msmetadata()

    # Get the list of spectral windows.

    msmd.open(filename)
    spws = msmd.spwsforintent(intent)

    # Get the frequencies for all of the spectral windows.

    freqs = [msmd.chanfreqs(spw).mean() for spw in spws]
    msmd.close()

    # Check which band this is in and return the name.

    bands = []
    for freq in freqs:
        if 8. <= freq/1e9 <= 12:
            bands.append("10GHz")
        elif 12. < freq/1e9 <= 18:
            bands.append("15GHz")
        elif 18 < freq/1e9 <= 26.5:
            bands.append("22GHz")
        elif 26.5 < freq/1e9 <= 40:
            bands.append("33GHz")
        elif 40 < freq/1e9 <= 50:
            bands.append("44GHz")
        elif 84 <= freq/1e9 <= 116:
            bands.append("100GHz")
        elif 211 <= freq/1e9 <= 275:
            bands.append("230GHz")
        elif 275 <= freq/1e9 <= 373:
            bands.append("345GHz")
        else:
            raise ValueError(str(freq/1e9)+" GHz could not be associated with a"
                    " known frequency band.")

    # Return the unique bands that were found.

    bands = list(numpy.unique(bands))

    return bands
