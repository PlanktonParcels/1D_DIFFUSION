from datetime import timedelta
import os

server = 'local_machine'
machine_home_directory = os.path.expanduser('~')

# directories for the output files of the parcels simulations, concentration files, figures, and field data
root_direc = {'local_machine': machine_home_directory + '/Desktop/Bern Projects/Wind Mixing/'}
root_direc ='/leonardo_work/OGS23_PRACE_IT_0/plazzari/seamless-notebooks4PlanktonParcels/Wind-Mixing-Diffusion-1.2/'
output_dir = root_direc + 'parcels_output/'
conc_dir = root_direc + 'concentration_output/'
figure_dir = root_direc + 'Figures/'
data_dir = root_direc + 'Data/'

# Timesteps for integration and for printing to the output file
dt_out = timedelta(seconds=3 * 60)
dt_int = timedelta(seconds=30)

# Runtime for the entire simulation
hours = 12
spinup_time = timedelta(seconds=(hours - 1) * 3600)
runtime = timedelta(seconds=3600)

# Number of particles in a simulation
p_number = 100000
p_start_depth = 0.0                                         # starting depth of the particles
seed = 1

# The number of depth levels used in calculating the Kz profiles
depth_levels = 1000

# Some basic physical parameters
# Density of plastic polymers from Brignac et al. (2019) at https://pubs.acs.org/doi/abs/10.1021/acs.est.9b03561
rho_w = 1027                      # density sea water (kg/m^3)
rho_a = 1.22                      # density air (kg/m^3)
vk = 0.4                          # von Karman constant
wave_age = 35                     # assuming fully developed sea, Kukulka et al. (2012)
g = 9.81                          # acceleration due to gravity (m s^-2)
MLD = 20.                         # Ocean mixing layer depth (m)
max_depth = 100.                  # Maximum depth in our two layer model (m)
phi = 0.9                         # Stability function in Monin-Obukov boundary layer theory (Boufadel et al., 2019)
mu = 1e-3                         # dynamic viscosity
nu = 1.1e-6                       # kinematic viscosity of sea water (Enders et al., 2015)
rho_p_pp = 850                    # density polypropylene (kg/m^3)
rho_p_pe = 980                    # density high density polyethylene (kg/m^3)
bulk_diff = 3e-5                  # Dianeutral diffusion below MLD (m^2/s) (Waterhouse et al., 2014)

