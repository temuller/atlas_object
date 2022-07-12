import numpy as np
from atlas_object.sigma_clipping import weighted_sigmaclip

def weighted_rolling(x_data, y_data, yerr_data=None,
                     window=3, center=False,
                     sigma_clip=False, **sigclip_kwargs):
    """Weighted rolling functions, similar to pandas
    rolling function.

    Parameters
    ----------
    x_data: array
        X-axis data.
    y_data: array
        Y-axis data.
    yerr_data: array
        Y-axis error.
    window: float
        Time window in the same units as 'x'.
    center: bool, default 'False'
        If 'False', set the window labels as the right 
        edge of the window index. If 'True', set the window 
        labels as the center of the window index.

    Returns
    -------
    4-tuple with rolling data ('x', 'y' and 'yerr' arrays) and
    indices of the data removed by the sigma clipping
    """
    rolling_dict = {'x': [], 'y': [], 'yerr': []}
    if yerr_data is None:
        yerr_data = np.ones_like(y_data)

    x_used = np.empty(0)
    for i, x in enumerate(x_data):
        # window type
        if center == True:
            roll_x = x_data.copy()
            roll_y = y_data.copy()
            roll_yerr = yerr_data.copy()
            mask = np.abs(x - roll_x) <= window / 2
        else:
            roll_x = x_data[:i + 1].copy()
            roll_y = y_data[:i + 1].copy()
            roll_yerr = yerr_data[:i + 1].copy()
            mask = x - roll_x <= window

        roll_x = roll_x[mask]
        roll_y = roll_y[mask]
        roll_yerr = roll_yerr[mask]

        # if only one or no data point is left, 
        # no need to do anything else
        if len(roll_x) == 0:
            continue
        elif len(roll_x) == 1:
            rolling_dict['x'].append(roll_x[0])
            rolling_dict['y'].append(roll_y[0])
            rolling_dict['yerr'].append(roll_yerr[0])
            continue

        # sigma clipping within rolling segments 
        if sigma_clip:
            if 'errors' in sigclip_kwargs.keys():
                errors = sigclip_kwargs['errors']
                sigclip_kwargs.pop('errors')
            else:
                errors = roll_x
            mask, n_iter = weighted_sigmaclip(roll_y,
                                              errors,
                                              **sigclip_kwargs)
            roll_x = roll_x[mask]
            roll_y = roll_y[mask]
            roll_yerr = roll_yerr[mask]

            if len(roll_x) == 0:
                continue

        # keep track of the values being used
        x_used = np.r_[x_used, roll_x]

        # calculate weighted mean and error propagation
        # x-axis
        rolling_dict['x'].append(roll_x.mean())
        # y-axis
        w = 1 / roll_yerr ** 2
        wmean = np.average(roll_y, weights=w)
        rolling_dict['y'].append(wmean)
        # y-error: standard deviation of the weighted mean
        wstd = np.sqrt(1 / np.sum(w))
        rolling_dict['yerr'].append(wstd)

    # turn lists into arrays    
    for key, values in rolling_dict.items():
        rolling_dict[key] = np.array(rolling_dict[key])

    # values used
    indices = np.array([True if x in x_used else False for x in x_data])

    return rolling_dict['x'], rolling_dict['y'], rolling_dict['yerr'], indices