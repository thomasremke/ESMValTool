#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculates the ETCCDI Climate Change Indices."""
import logging
import os
from pprint import pformat
import numpy as np
import iris

from esmvaltool.diag_scripts.shared import (group_metadata, run_diagnostic,
                                            select_metadata, sorted_metadata)
from esmvaltool.diag_scripts.shared._base import (
    ProvenanceLogger, get_diagnostic_filename, get_plot_filename)
from esmvaltool.diag_scripts.shared.plot import quickplot
import extreme_events_indices

logger = logging.getLogger(os.path.basename(__file__))


def get_provenance_record(attributes, ancestor_files):
    """Create a provenance record describing the diagnostic data and plot."""
    caption = ("Average {long_name} between {start_year} and {end_year} "
               "according to {dataset}.".format(**attributes))

    record = {
        'caption': caption,
        'statistics': ['mean'],
        'domains': ['global'],
        'plot_type': 'zonal',
        'authors': [
            'andela_bouwe',
            'righi_mattia',
        ],
        'references': [
            'acknow_project',
        ],
        'ancestors': ancestor_files,
    }
    return record

def _count_values_below(data, axis, threshold=273.15):
    return np.sum(data < threshold, axis=axis, dtype=int)

def _count_values(data, axis, threshold, logic):
    if logic == 'lower':
        return np.sum(data < threshold, axis=axis, dtype=int)
    elif logic == 'greater':
        return np.sum(data > threshold, axis=axis, dtype=int)
    else:
        raise Exception('Not implemented')

def _spell(data, axis, threshold, duration):
    pass

def _select_value_per_month(data, axis, extreme):
    pass

def _outlier(data, axis, quantile, threshold, logic):
    pass

def _mean_diff(data, axis):
    pass

def _count_calc(data, axis):
    pass

def _sum(data, axis):
    pass

def compute_indices(cubes):
    """Compute indices."""
    out = {}
    logger.debug("Computing frost days index for:")
    count_true = iris.analysis.Aggregator('_count_values_below',
            _count_values_below, units_func=lambda units: 1)
    cube_list = iris.cube.CubeList()
    for name in cubes.keys():
        logger.debug("%s", name)
        cube_list.append(cubes[name]['tasmin'].collapsed('time', count_true))
    out['frost_days'] = cube_list
    return out


def plot_diagnostic(cube, basename, provenance_record, cfg):
    """Create diagnostic data and plot it."""
    diagnostic_file = get_diagnostic_filename(basename, cfg)

    logger.info("Saving analysis results to %s", diagnostic_file)
    iris.save(cube, target=diagnostic_file)

    if cfg['write_plots'] and cfg.get('quickplot'):
        plot_file = get_plot_filename(basename, cfg)
        logger.info("Plotting analysis results to %s", plot_file)
        provenance_record['plot_file'] = plot_file
        quickplot(cube, filename=plot_file, **cfg['quickplot'])

    logger.info("Recording provenance of %s:\n%s", diagnostic_file,
                pformat(provenance_record))
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(diagnostic_file, provenance_record)


def main(cfg):
    """Compute the time average for each input dataset."""
    # Get the data that we will use as input.
    input_data = cfg.pop('input_data').values()
    logger.info("cfg:\n%s", pformat(cfg))

    # Grouped and sorted the data by alias.
    grouped_input_data = group_metadata(
        input_data, 'alias', sort='alias')

    # Loop over variables/datasets in alphabetical order of alias
    cubes = {}
    for alias in grouped_input_data:
        logger.info("Processing alias %s", alias)
        for attributes in grouped_input_data[alias]:
            logger.info("Processing dataset %s", attributes['dataset'])
            input_file = attributes['filename']
            cubes['{}_{}'.format(alias, attributes['short_name'])] = iris.load_cube(input_file)
        # log if all expected short_names are there
        # call compute idices for all cubes
        
    # TODO: include checks that variables fit to index
    logger.info(cubes)
    
    # get index function
    etccdi_index = getattr(extreme_events_indices, cfg['index'], None)
    
    # if there is no index available: report and break
    if etccdi_index is None:
        logger.info('There is no index available called: {}'.format(cfg['index']))
        logger.info('*** calculation failed ***')
        return
    
    # calculate 
    etccdi_cubes = {}
    for key, cube in cubes.items():
        logger.info(cube)
        etccdi_cubes[key] = etccdi_index(cube)
    logger.info("Finalized computation for %s", ": ".join(etccdi_cubes))
    #cube = compute_diagnostic(input_file)
    #output_basename = os.path.splitext(
    #        os.path.basename(input_file))[0] + '_mean'
    #provenance_record = get_provenance_record(
    #        attributes, ancestor_files=[input_file])
    #call plot idices
    #plot_diagnostic(cube, output_basename, provenance_record, cfg)


if __name__ == '__main__':

    with run_diagnostic() as config:
        main(config)
