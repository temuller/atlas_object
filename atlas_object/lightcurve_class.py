import numpy as np
import pandas as pd

from atlas_object.utils import flux2mag, mag2flux
from atlas_object.rolling import weighted_rolling
from atlas_object.sigma_clipping import weighted_sigmaclip

class lightcurve(object):
    """Light curve class.
    """

    def __init__(self, band, lcs_df):
        """
        Parameters
        ----------
        band: str
            ATLAS band (o or c).
        lcs_df: DataFrame
            ATLAS forced photometry.
        """
        self.band = band

        data = lcs_df[lcs_df.F == band]
        self.time = data.MJD.values
        self.flux = data.uJy.values
        self.flux_err = data.duJy.values
        self.mag = data.m.values
        self.mag_err = data.dm.values
        color_dict = {'c': 'cyan', 'o': 'orange'}
        self.color = color_dict[band]
        self.snr = data.uJy.values / data.duJy.values
        self.zp = 23.9

    def __repr__(self):
        return f'band: {self.band}'

    def __getitem__(self, item):
        return getattr(self, item)

    def mask_lc(self, mask):
        """Masks the light curve with the given mask.

        Parameters
        ----------
        mask: booleans
            Mask with the same length as the light curves.
        """
        self.time = self.time.copy()[mask]
        self.flux = self.flux.copy()[mask]
        self.flux_err = self.flux_err.copy()[mask]
        self.mag = self.mag.copy()[mask]
        self.mag_err = self.mag_err.copy()[mask]
        self.snr = self.snr.copy()[mask]

    def sigma_clip(self, niter=1, n_sigma=3, use_median=False):
        """Performs sigma clipping.

        Parameters
        ----------
        niter: int, default ``1``
            The number of sigma-clipping iterations to perform.
            If niter is negative, iterations will continue until no more
            clipping occurs or until abs('niter') is reached, whichever
            is reached first.
        n_sigma: float, default '3'
            Number of standard deviations used.
        use_median: bool, default 'False':
            If 'True', use median of data instead of mean.
        """
        indices, iter_val = weighted_sigmaclip(self.flux, self.flux_err,
                                               niter, n_sigma, use_median)
        self.time = self.time[indices]
        self.flux = self.flux[indices]
        self.flux_err = self.flux_err[indices]
        self.mag = self.mag[indices]
        self.mag_err = self.mag_err[indices]
        self.indices = indices
        self.iter = iter_val

    def rolling(self, window, center=False,
                sigma_clip=False, **sigclip_kwargs):
        """Weighted rolling mean function.

        Parameters
        ----------
        window: float
            Time window in units of days.
        center: bool, default 'False'
            If 'False', set the window labels as the right
            edge of the window index. If 'True', set the window
            labels as the center of the window index.
        sigma_clip: bool, default 'False'
            If 'True', sigma clipping is performed within rolling
            windows.
        sigclip_kwargs: dict
            Input parameters for the sigma clipping. See 'sigma_clip()'.
        """
        x, y, yerr, inds = weighted_rolling(self.time, self.flux,
                                            self.flux_err, window, center,
                                            sigma_clip, **sigclip_kwargs)
        self.time = x
        self.flux = y
        self.flux_err = yerr
        self.mag, self.mag_err = flux2mag(y, self.zp, yerr)
        self.indices = inds


class lightcurves(object):
    """Multi-colour light curves class.
    """

    def __init__(self, lcs_df):
        """
        Parameters
        ----------
        lcs_df: DataFrame
            ATLAS forced photometry.
        """
        self.bands = lcs_df.F.unique()

        for band in self.bands:
            lc = lightcurve(band, lcs_df)
            setattr(self, band, lc)

    def __repr__(self):
        return str(self.bands)

    def __getitem__(self, item):
        return getattr(self, item)