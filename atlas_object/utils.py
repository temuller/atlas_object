import requests
import numpy as np

def download_test_data():
    """Downloads an ATLAS force photometry file.
    """
    url = 'https://raw.githubusercontent.com/temuller/atlas_object/main/notebooks/test_lc.csv'
    response = requests.get(url)
    open("test_lc.csv", "wb").write(response.content)

def flux2mag(flux, zp, flux_err=0.0):
    """Converts fluxes to magnitudes, propagating errors if given.
    Note: if there are negative or zero fluxes, these are converted to NaN values.
    Parameters
    ----------
    flux : array
        Array of fluxes.
    zp : float or array
        Zero points.
    flux_err : array, default ``0.0``
        Array of flux errors.
    Returns
    -------
    mag : array
        Fluxes converted to magnitudes.
    mag_err : array
        Flux errors converted to errors in magnitudes.
    """

    if type(flux) == np.ndarray:
        flux_ = np.array([f if f >= 0.0 else np.nan for f in flux])  # turns negative and 0.0 values to NaN
    elif flux <= 0.0:
        flux_ = np.nan
    else:
        flux_ = flux

    mag = -2.5 * np.log10(flux_) + zp
    mag_err = np.abs(2.5 * flux_err / (flux_ * np.log(10)))

    return mag, mag_err


def mag2flux(mag, zp, mag_err=0.0):
    """Converts magnitudes to fluxes, propagating errors if given.
    Parameters
    ----------
    mag : array
        Array of magnitudes.
    zp : float or array
        Zero points.
    mag_err : array, default ``0.0``
        Array of magnitude errors.
    Returns
    -------
    flux : array
        Magnitudes converted to fluxes.
    flux_err : array
        Magnitude errors converted to errors in fluxes.
    """

    flux = 10 ** (-0.4 * (mag - zp))
    flux_err = np.abs(flux * 0.4 * np.log(10) * mag_err)

    return flux, flux_err