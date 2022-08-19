from casatasks import rmtables
import os

def clean_last():
    # Remove files that were created during the previous run of this script.

    for fileext in ["*.selfcal*",\
            "*.fits",\
            "*.flux*",\
            "*.image*",\
            "*.model*",\
            "*.fitmodel*",\
            "*.psf*",\
            "*.residual*",\
            "*.gridwt",\
            "*.vis",\
            "*.mask",\
            "*.pb*",\
            "*.pbcor",\
            "*.sumwt*",\
            "*.png",\
            "*.alpha*",\
            "*.beta*",\
            "*.contsub"]:
        rmtables(fileext)

    os.system("rm -r *.fits")
