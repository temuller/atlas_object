import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy

from atlas_object.lightcurve_class import lightcurves

class atlas_object(object):
    """Class that represents an object with ATLAS photometry.
    """
    def __init__(self, lc_file):
        """
        Parameters
        ----------
        lc_file: str
            Light-curve CSV file with ATLAS photometry.
        """
        self.lc_file = lc_file
        lc_df = pd.read_csv(lc_file)
        self.lc_df = lc_df
        self.lcs = lightcurves(lc_df)
        self.init_lcs = deepcopy(self.lcs)
        self.bands = lc_df.F.unique()
        self.modified = False

    def __repr__(self):
        rep = (f'LC file: {self.lc_file}')
        return rep

    def __getitem__(self, item):
        return getattr(self, item)

    def plot_original(self, xmin=None, xmax=None):
        """Plots the initial light curves.

        Parameters
        ----------
        xmin: float, default 'None'
            Minimum x-axis range.
        xmax: float, default 'None'
            Maximum x-axis range.
        """
        mags = np.empty(0)

        fig, ax = plt.subplots(figsize=(8, 6))
        for filt in self.bands:
            init_lcs = self.init_lcs[filt]
            ax.errorbar(init_lcs.time, init_lcs.mag, init_lcs.mag_err,
                        fmt='o', label=filt, c=init_lcs.color, mec='k')
            mags = np.r_[mags, init_lcs.mag]

        ax.set_ylabel('Appartent Magnitude', fontsize=18)
        ax.set_xlabel('MJD', fontsize=18)
        ax.tick_params(labelsize=18)
        ax.set_ylim(mags.min() - 0.5, mags.max() + 0.5)
        ax.set_xlim(xmin, xmax)
        ax.invert_yaxis()
        ax.legend(fontsize=18)
        plt.show()

    def plot_lcs(self, xmin=None, xmax=None):
        """Plots the current state of the light curves.

        Parameters
        ----------
        xmin: float, default 'None'
            Minimum x-axis range.
        xmax: float, default 'None'
            Maximum x-axis range.
        """
        mags = np.empty(0)

        fig, ax = plt.subplots(figsize=(8, 6))
        for filt in self.bands:
            if self.modified:
                lcs = self.lcs[filt]
                ax.errorbar(lcs.time, lcs.mag, lcs.mag_err,
                            fmt='*', c=lcs.color)
                alpha = 0.2
            else:
                alpha = 1

            init_lcs = self.init_lcs[filt]
            ax.errorbar(init_lcs.time, init_lcs.mag, init_lcs.mag_err,
                        fmt='o', label=filt, c=init_lcs.color, mec='k',
                        alpha=alpha)
            mags = np.r_[mags, init_lcs.mag]

        ax.set_ylabel('Appartent Magnitude', fontsize=18)
        ax.set_xlabel('MJD', fontsize=18)
        ax.tick_params(labelsize=18)
        ax.set_ylim(mags.min() - 0.5, mags.max() + 0.5)
        ax.set_xlim(xmin, xmax)
        ax.invert_yaxis()
        ax.legend(fontsize=18)
        plt.show()

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
        color_dict = {'c': 'blue', 'o': 'red'}
        for filt in self.bands:
            self.lcs[filt].rolling(window, center,
                                   sigma_clip,
                                   **sigclip_kwargs)
            self.lcs[filt].color = color_dict[filt]
        self.modified = True

    def sigma_clip(self, niter=0, n_sigma=3, use_median=False):
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
        color_dict = {'c': 'blue', 'o': 'red'}
        for filt in self.bands:
            self.lcs[filt].sigma_clip(niter, n_sigma, use_median)
            self.lcs[filt].color = color_dict[filt]
        self.modified = True