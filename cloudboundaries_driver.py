import numpy as np

def radar_lidar_DQ_bitunpack(RADAR_LIDAR_BOUNDARIES_data_quality_flag):
    '''
    This function interprets bit-packed DQ flags from the radar-lidar cloud top/base height retrieval.
    Returns individual bits for boolean indexing... e.g.  some_array[(b1==1) & (b2==2) & np.isnan(b3)] = Bad
                                                          some_array[np.isnan(b1) & np.isnan(b2) & np.isnan(b3)] = Good
    '''
    # >>> initialize DQ flags
    DQ_FLAGS = ('Ceilometer/Lidar data missing / not used', 'Cloud Radar data missing / not used', 'Maximum allowed layers exceeded. Upper layer boundaries with span several physical layers.')
    dq_flags = bitset('dq_flags', DQ_FLAGS)
    # >>> MAKE A PIE CHART OF THE RADAR ISSUES
    DQ_bits = ["" for i in range(len(RADAR_LIDAR_BOUNDARIES_data_quality_flag))]
    for ii in range(len(RADAR_LIDAR_BOUNDARIES_data_quality_flag)):
        tmp = dq_flags.fromint(RADAR_LIDAR_BOUNDARIES_data_quality_flag[ii])
        DQ_bits[ii] = tmp.bits()
    b1, b2, b3 = (np.zeros([len(RADAR_LIDAR_BOUNDARIES_data_quality_flag)]) for x in range(3))
    for ii in range(len(RADAR_LIDAR_BOUNDARIES_data_quality_flag)):
        b1[ii] = int(DQ_bits[ii][0])
        b2[ii] = int(DQ_bits[ii][1])
        b3[ii] = int(DQ_bits[ii][2])
    b1[b1==1], b1[b1==0] = 1, np.nan
    b2[b2==1], b2[b2==0] = 2, np.nan
    b3[b3==1], b3[b3==0] = 3, np.nan
    return(b1, b2, b3)
#___________________________________________________________________________________________________________________________________________
    # >>> radar-lidar merged data -- personal correspndence for access
rpath = '/home/fenwick/datasets/MICRE/Marchand_Retrievals/V1.95/NetCDF/'
all_rdata = np.array([f for f in os.listdir(rpath) if f.startswith("Cloud_and_Precipitation_Properties_MICRE_V1.95")])
all_rdata.sort()
#___________________________________________________________________________________________________________________________________________
        # >>> loop through all radar-lidar merged data files ... run cloud boundaries function
for rfile in all_rdata:
    date = rfile[-11:-3]
    # >>> load .nc and variables
    rdata = Dataset(rpath + rfile,'r')
    boundaries_time_gmt = np.array(rdata.variables['RADAR_LIDAR_BOUNDRIES_time_gmt'][:])
    boundaries_n_layers = np.array(rdata.variables['RADAR_LIDAR_BOUNDRIES_time_gmt'][:])
    cloud_top           = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_layer_radar_top'][:])
    cloud_base          = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_layer_median_lidar_base'][:])
    boundaries_n_layers = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_n_layers'][:])
    ceil_n_layers       = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_n_ARM_Ceilometer_columns'][:])
    ceil_obsc_n_layers  = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_n_ARM_Ceilometer_columns_obscured'][:])
    boundaries_DQ       = np.array(rdata.variables['RADAR_LIDAR_BOUNDARIES_data_quality_flag'][:])
    b1, b2, b3          = radar_lidar_DQ_bitunpack(boundaries_DQ) # >>> process DQ flags: b1=1 -> ceil missing/not used
                                                                  # >>>                   b2=2 -> radar missing/not used
                                                                  # >>>                   b3=3 -> max layers exceeded
    # >>> 5-MINUTE TIME ARRAY
    tstep_minutes = 5
    dt = tstep_minutes*60/3600   # >>> seconds
    time_gmt = np.arange(0.5*dt,0.5*dt+((24/dt)-0.5)*dt,dt)     # >>> size = n_times x 1 -- time should be first dimension
    n_phase_times = len(time_gmt)
    # >>> store 5-minute cloud tops, bases
    cloud_top_5min  = np.nan*np.ones([n_phase_times,5])
    cloud_base_5min = np.nan*np.ones([n_phase_times,5])

    # >>> loop through 5-minute chunks of radar-lidar boundaries data
    for t_loop in range(n_phase_times):
        a_pts = np.where(abs(boundaries_time_gmt - time_gmt[t_loop]) <= 0.5*dt )[0] # >>> indices in 5-minute period
        ceil_n_tmp = np.copy(ceil_n_layers[a_pts])

        # >>> cloud layer 1
        cloud_top_5min, cloud_base_5min = calc_5min_cloudboundaries(t_loop, a_pts, 5, cloud_top, cloud_base, 0, cloud_top_5min, cloud_base_5min)
        if np.isnan(cloud_base_5min[t_loop,0]) and ~np.isnan(cloud_top_5min[t_loop,0]):
            print(date, '   top', cloud_top_5min[t_loop,0], '   base', cloud_base_5min[t_loop,0], '\n', cloud_base[a_pts,0], '\n\n')
            # >>> minimum 1 minute of multi-layer cloud present?
        if len(boundaries_n_layers[a_pts][boundaries_n_layers[a_pts]>1]) >= 5:
            # >>> cloud layer 2
            cloud_top_5min, cloud_base_5min = calc_5min_cloudboundaries(t_loop, a_pts, 5, cloud_top, cloud_base, 1, cloud_top_5min, cloud_base_5min)
            # >>> cloud layer 3
            cloud_top_5min, cloud_base_5min = calc_5min_cloudboundaries(t_loop, a_pts, 5, cloud_top, cloud_base, 2, cloud_top_5min, cloud_base_5min)
            # >>> cloud layer 4
            cloud_top_5min, cloud_base_5min = calc_5min_cloudboundaries(t_loop, a_pts, 5, cloud_top, cloud_base, 3, cloud_top_5min, cloud_base_5min)
            # >>> cloud layer 5
            cloud_top_5min, cloud_base_5min = calc_5min_cloudboundaries(t_loop, a_pts, 5, cloud_top, cloud_base, 4, cloud_top_5min, cloud_base_5min)
