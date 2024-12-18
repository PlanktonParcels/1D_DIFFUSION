import utils, settings
from netCDF4 import Dataset
import xarray as xr
import numpy as np


def depth_concentration(w_10, w_rise, diffusion_type, boundary, alpha, theta, gamma, bin_size=0.5, remove_file=True,
                        wave_roughness=False):
    """
    Binning the parcels output for a given run into vertical bins of size bin_size.
    note: the concentrations are not normalized, that is done later when the concentrations are loaded
    :param w_10: 10m wind speed
    :param w_rise: rise velocity
    :param diffusion_type: diffusion type, either SWB or KPP
    :param boundary: boundary condition, and whether M-0 or M-1
    :param alpha: memory term for M-1
    :param theta: Langmuir circulation amplification term
    :param gamma: for SWB diffusion, the multiple of the Hs to which we have constant diffusion
    :param remove_file: if True, remove the original parcels output file
    :param wave_roughness: if True, have surface roughness be wave height dependent
    :return:
    """
    # Loading the relevant parcels file
    parcels_file = utils.get_parcels_output_name(w_10, w_rise, diffusion_type, boundary=boundary, mld=settings.MLD,
                                                 alpha=alpha, theta=theta, wave_roughness=wave_roughness, gamma=gamma)
    dataset = xr.open_zarr(parcels_file)
    time = dataset.time.values[0, :]
    time_steps = len(time)
    # Setting the depth bins and creating the output directory
    depth_bins = np.arange(0, settings.max_depth, bin_size)
    output_dir = {}
    # Looping through all the saved timesteps in the parcels output
    for t in range(time_steps):
        # Loading the depth data for all the particles
        depth = dataset.z.values[:, t]
        # Saving the binned concentrations
        concentrations, bin_edges = np.histogram(depth, bins=depth_bins)
        output_dir[t] = concentrations
        # Check if particles have been removed, if yes raise an assertion error
        removed_frac = np.sum(depth) / depth.shape[0] * 100.
        str_format = diffusion_type, boundary, w_10, w_rise, alpha
#PL     assert removed_frac == 0.0, "Particle number was not conserved for {} with {}, (w_10={}, w_rise={}, a={})".format(*str_format)

    # Saving the bin edges, and specifying which time slice was the last for easy loading later
    output_dir['bin_edges'] = (depth_bins[:-1] + depth_bins[1:]) / 2
    output_dir['last_time_slice'] = t

    # Now, we calculate the mean profile, and the standard deviation at each depth level
    output_dir['mean_profile'] = np.zeros(output_dir[output_dir['last_time_slice']].shape, dtype=float)
    output_dir['std_profile'] = np.zeros(output_dir[output_dir['last_time_slice']].shape, dtype=float)
    # Calculate the mean concentration
    for t in range(time_steps):
        output_dir['mean_profile'] += output_dir[t] / time_steps
    # Calculate the standard deviation
    for t in range(len(time)):
        output_dir['std_profile'] += np.square(output_dir[t] - output_dir['mean_profile']) / time_steps
    output_dir['std_profile'] = np.sqrt(output_dir['std_profile'])

    # Pickling the concentration array
    print(utils.get_concentration_output_name(w_10, w_rise, diffusion_type, boundary, alpha=alpha, theta=theta, wave_roughness=wave_roughness, gamma=gamma))

    utils.save_obj(filename=utils.get_concentration_output_name(w_10, w_rise, diffusion_type, boundary, alpha=alpha,
                                                                theta=theta, wave_roughness=wave_roughness,
                                                                gamma=gamma),
                   item=output_dir)
    # We don't need the parcels file for any subsequent analysis, so I'm removing it to save storage on my computer
    if remove_file:
        utils.remove_file(conduct=True, file_name=parcels_file)


def depth_bin_numbers(w_10, w_rise, diffusion_type, boundary, alpha, theta, gamma, wave_roughness=False, conduct=False):
    """
    State the number of particles that are within the defined depth ranges
    :param w_10: 10m wind speed
    :param w_rise: rise velocity
    :param diffusion_type: diffusion type, either SWB or KPP
    :param boundary: boundary condition, and whether M-0 or M-1
    :param alpha: memory term for M-1
    :param theta: Langmuir circulation amplification term
    :param gamma: for SWB diffusion, the multiple of the Hs to which we have constant diffusion
    :param wave_roughness: if True, have surface roughness be wave height dependent
    :param conduct: if True, carry out the function
    :return:
    """
    if conduct:
        # Load the concentration file
        data_dict = utils.load_obj(filename=utils.get_concentration_output_name(w_10, w_rise, diffusion_type, boundary,
                                                                                alpha=alpha, theta=theta, gamma=gamma,
                                                                                wave_roughness=wave_roughness))
        # Load the final concentration array and the bin depths
        counts = data_dict[data_dict['last_time_slice']]
        bin_midpoint = data_dict['bin_edges']
        total_number = np.nansum(counts)

        # Set the depth bins in question
        depth_bins = [(0, 2), (2, 5), (5, 10), (10, 15), (15, 20), (20, settings.max_depth)]

        for depth_range in depth_bins:
            # Selecting the bins of the concentrations with the given range
            selection = (bin_midpoint > depth_range[0]) & (bin_midpoint <= depth_range[1])
            # The percentage of total particles within the depth range
            within_depth_range = np.nansum(counts[selection]) / total_number * 100
            # Printing the depth range
            str_format = w_rise, w_10, within_depth_range, depth_range[0], depth_range[1]
            print("For w_r = {} and w_10 = {}. {:.2f}% are within z = {} - {}".format(*str_format))
