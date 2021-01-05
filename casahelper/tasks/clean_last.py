import os

def clean_last():
    # Remove files that were created during the previous run of this script.

    for fileext in ["*.selfcal*",\
            "*.fits",\
            "*.flux*",\
            "*.image",\
            "*.model",\
            "*.psf",\
            "*.residual",\
            "*.vis",\
            "*.mask",\
            "*.pb",\
            "*.pbcor",\
            "*.sumwt",\
            "*.png",\
            "*.contsub"]:
        os.system("rm -r "+fileext)
