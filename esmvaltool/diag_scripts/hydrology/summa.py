"""summa diagnostic."""
import logging
from pathlib import Path
import warnings
import numpy as np

# import dask.array as da
import iris

from esmvaltool.diag_scripts.shared import (ProvenanceLogger,
                                            get_diagnostic_filename,
                                            group_metadata, run_diagnostic)
from esmvaltool.cmorizers.obs import utilities as utils

logger = logging.getLogger(Path(__file__).name)


def get_provenance_record(dataset):
    """Create a provenance record."""
    record = {
        'caption': "Forcings for the SUMMA hydrological model.",
        'domains': ['global'],
        'authors': [
            # 'kalverla_peter',
            # 'alidoost_sarah',
            'camphuijsen_jaro',
        ],
        'projects': [
            'ewatercycle',
        ],
        'references': [
            'acknow_project',
        ],
        'dataset': [dataset],
    }
    return record


def _rename_var(input_dict, output_name):
    """Change the cmor names for SUMMA"""
    variables = {}
    for key in output_name:
        if key in input_dict:
            cube = input_dict[key]
            cube.var_name = output_name[key]
            variables[key] = cube
    return variables


def compute_windspeed(u_component, v_component):
    """ Compute wind speed magnitude based on vector components """
    wind_speed = (u_component**2 + v_component**2)**.5
    return wind_speed


def windspeed_conversion(windspeed_z, measurement_height):
    """ Convert wind speed from input height to 2m with logarithmic profile """
    warnings.warn('This version of the logarithmic wind profile is violating\
                  general principles of transparancy. Better replace it with\
                  a more general formula incorporating friction velocity or\
                  roughness length')
    disp_height = 5.42 / 67.8
    rough_length = 1 / 67.8
    windspeed_2m = windspeed_z * np.log((2 - disp_height) / rough_length) 
                   / np.log((measurement_height - disp_height) / rough_length)
    return windspeed_2m

def compute_specific_humidity(dewpoint_temperature, surface_pressure):
    # source 1: https://www.eoas.ubc.ca/books/Practical_Meteorology/prmet/PracticalMet_WholeBook-v1_00b.pdf page 96
    
    surface_pressure = surface_pressure/1000.
    # to convert between celsius and kelvin
    kelvin = 273.15
    # ratio of gas constants for dry air and water vapor in g/g 
    epsilon = 0.62196351 #from metsim python package
    sat_vap_pres = 611 # saturated vapor pressure in Pa

    vapour_pressure = sat_vap_pres * np.exp((17.76 * (dewpoint_temperature - kelvin)) / 
                      (dewpoint_temperature - kelvin + 243.5))
    vapour_pressure = vapour_pressure / 1000.
    mix_rat = epsilon * vapour_pressure / (surface_pressure - vapour_pressure)
    spechum = mix_rat / (1 + mix_rat)
    return spechum


def _fix_cube(cube, var_name):
    """Fixing attributes for new cube"""
    if var_name == 'windspd':
        # remove the height_0 coordinate (10m)
        cube.remove_coord(cube.coord('height'))
        # add the height coordinate (2m)
        utils.add_scalar_height_coord(cube, 2.)
        cube.var_name = var_name
        cube.standard_name = 'wind_speed'
    if var_name == 'spechum':
        cube.var_name = var_name
        cube.standard_name = 'specific_humidity'
        cube.unit = 'g/g'
    return cube


def main(cfg):
    """Process data for use as input to the summa hydrological model """
    input_data = cfg['input_data'].values()
    logger.info(input_data)
    grouped_input_data = group_metadata(input_data,
                                        'standard_name',
                                        sort='dataset')
    variables = {}
    # output variable's name in SUMMA
    output_var_name = {
        'tas':'airtemp',
        'rsds':'SWRadAtm',
        'windspd':'windspd',
        'strd':'LWRadAtm',
        'pr':'pptrate',
        'spechum':'spechum',
        'ps':'airpres'
    }
    for standard_name in grouped_input_data:
        # get the dataset name to use in save function later
        # TODO add support multiple dataset in one diagnostic
        dataset = grouped_input_data[standard_name][0]['alias']
        logger.info("Processing variable %s", standard_name)
        cube_list_all_years = iris.cube.CubeList()
        for attributes in grouped_input_data[standard_name]:
            logger.info("Processing dataset %s", attributes['dataset'])
            input_file = attributes['filename']
            cube = iris.load_cube(input_file)
            cube_list_all_years.append(cube)
        cube_all_years = cube_list_all_years.concatenate_cube()
        key = grouped_input_data[standard_name][0]['short_name']
        variables[key] = cube_all_years

        # Do stuff
        # The data need to be aggregated for each HRU (subcatchment)
        # Inti's `decomposed` function in extract_shape should add
        # this as a dimension to the cubes, so it's just a matter of
        # aggregating latitude and longitude. The resulting cubes
        # will have dimensions 'time' and 'hru'.
        #
        # Unit conversion:
        # - precip: kg m-2 s-1
        # - radiation: w m-2
        # - temperature: K
        # - wind speed: m s-1
        # - pressure: Pa
        # - specific humidity: g g-1
        #
        # example output file can also be found on jupyter server.

    # Extract wind component variables from the cube list
    u_component = variables['uas']
    v_component = variables['vas']

    # compute wind speed and convert to 2m
    wind_speed = compute_windspeed(u_component, v_component)
    wind_speed_2m = windspeed_conversion(wind_speed, 10)

    # Fix cube attributes
    variables['windspd'] = _fix_cube(wind_speed_2m, 'windspd')

    # Specific humidity calculation from dewpoint temp and surface pressure 
    dewpoint_temperature = variables['tdps']
    surface_pressure = variables['ps']
    specific_humidity = compute_specific_humidity(dewpoint_temperature,
                                                     surface_pressure)
    # Fix cube attributes
    variables['spechum'] = _fix_cube(specific_humidity, 'spechum')

    # Select and rename the desired variables
    variables = _rename_var(variables, output_var_name)

    # Make a list from all cubes in dictionary
    cube_list_all_vars = iris.cube.CubeList()
    for key in variables:
        cube_list_all_vars.append(variables[key])
    # Save data
    basename = dataset + '_summa'
    output_file = get_diagnostic_filename(basename, cfg)
    iris.save(cube_list_all_vars, output_file, fill_value=1.e20)

    # Store provenance
    provenance_record = get_provenance_record(dataset)
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(output_file, provenance_record)


if __name__ == '__main__':

    with run_diagnostic() as config:
        main(config)