# Functions adapted from https://github.com/transientskp/tkp/blob/master/tkp/utility/sigmaclip.py
import numpy as np

def clip(data, mean, sigma):
    """Performs sigma clipping of data around mean.

    Parameters
    ----------
    data numpy.ndarray: 
        Array of values.
    mean: float
        Value around which to clip (does not have to be the mean).
    sigma: float
        Sigma-value for clipping.

    Returns
    -------
    indices: numpy.ndarray
        Indices of non-clipped data.
    """
    ilow = data >= mean - sigma
    ihigh = data <= mean + sigma
    indices = np.logical_and(ilow, ihigh)

    return indices


def calc_sigma(data, errors=None):
    """Calculates the weighted standard deviation.

    Parameters
    ----------
    data: numpy.ndarray
        Data to be averaged.
    errors: numpy.ndarray, default 'None'
        Errors for the data. If 'None', unweighted
        values are calculated.

    Returns
    -------
    wmean: numpy.ndarray
        Weighted mean.
    wsigma: numpy.ndarray
        Weighted standard deviation.
    """
    if errors is None:
        w = 1.0
    else:
        w = 1.0 / errors ** 2
        wmean = np.average(data, weights=w)

    V1 = w.sum()
    V2 = (w ** 2).sum()
    # weighted sample variance
    wsigma = np.sqrt(((data - wmean) * (data - wmean) * w).sum() *
                     (V1 / (V1 * V1 - V2)))

    return wmean, wsigma


def weighted_sigmaclip(data, errors=None, niter=1, n_sigma=3,
                       use_median=False):
    """Remove outliers from data which lie more than n_sigma
    standard deviations from mean.

    Parameters
    ----------
    data: numpy.ndarray
        Array containing data values.
    errors: numpy.ndarray, default 'None'
        Errors associated with the data. If 'None', unweighted mean 
        and standard deviation are used in calculations.
    niter: int, default '1' 
        Number of iterations to calculate mean and standard
        deviation, and reject outliers, If niter is negative,
        iterations will continue until no more clipping occurs or
        until abs('niter') is reached, whichever is reached first.
    n_sigma: float, default '3' 
        Number of standard deviations used for sigma clipping.
    use_median: bool, default 'False':
        If 'True', use median of data instead of mean.

    Returns
    -------
    indices: boolan numpy.array
        Boolean numpy array of indices indicating which
        elements are clipped (False), with the same shape as the
        input
    i: int
        Number of iterations
    """
    # indices keeps track which data should be discarded
    indices = np.ones(len(data.ravel()),
                      dtype=np.bool).reshape(data.shape)

    if niter < 0:
        nniter = -niter
    else:
        nniter = niter

    for i in range(nniter):
        newdata = data[indices]
        if errors is None:
            newerrors = None
        else:
            newerrors = errors[indices]

        N = len(newdata)
        if N < 2:
            # no data left to clip
            return indices, i

        mean, sigma = calc_sigma(newdata, newerrors)
        if use_median:
            mean = np.median(newdata)
        newindices = clip(data, mean, n_sigma * sigma)

        if niter < 0:
            # break when no changes
            if (newindices == indices).all():
                break
        indices = newindices

    return indices, i + 1