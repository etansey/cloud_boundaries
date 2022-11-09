def calc_5min_cloudboundaries(t_loop, a_pts, thresh, cloud_top, cloud_base, index, cloud_top_5min, cloud_base_5min):
    '''
    This function looks at 5 minutes' worth of cloud base and height retrievals from combined radar & ceilometer.
    5-minute chunk must contain a minimum tuneable threshold of e.g. 1 minute worth of retrieved CBH, CTH
    to qualify as "cloud-containing"...

    input variables:
    t_loop     = 5-minute time index
    a_pts      = all full res points contained in the 5-minute period
    thresh     = number of 12-second periods that must contain CBH/CTH to qualify the 5-minute chunk as "cloudy"
    cloud_top  = radar-ceilometer cloud top heights
    cloud_base = ceilometer cloud base
    index      = which cloud layer (0 thru 4 for 5 total possible layers)

    input/output:
    cloud_base_5min, cloud_top_5min to be updated by this function
    '''
    import numpy as np

    tops_tmp  = np.copy(cloud_top[a_pts, index])   # >>> 5-minute period cloud tops -- layer index
    bases_tmp = np.copy(cloud_base[a_pts, index])  # >>> 5-minute period cloud bases -- layer
    if len(tops_tmp[~np.isnan(tops_tmp)]) >= thresh:     # >>> minimum 1 minute worth of CTH retrievals?
        cloud_top_5min[t_loop,index] = np.nanmedian(tops_tmp)
    if len(bases_tmp[~np.isnan(bases_tmp)]) >= thresh:   # >>> minimum 1 minute worth of CBH retrievals?
        if ~np.isnan(cloud_top_5min[t_loop,index]):       # >>> exclude CBHs that are above median CTH
            bases_tmp[(bases_tmp>cloud_top_5min[t_loop,index])] = np.nan
        cloud_base_5min[t_loop,index] = np.nanmedian(bases_tmp)

    return(cloud_top_5min, cloud_base_5min)
