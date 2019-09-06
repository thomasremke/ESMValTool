# ESMValTool

[![Documentation Status](https://readthedocs.org/projects/esmvaltool/badge/?version=latest)](https://esmvaltool.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3401363.svg)](https://doi.org/10.5281/zenodo.3401363)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ESMValGroup?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![CircleCI](https://circleci.com/gh/ESMValGroup/ESMValTool.svg?style=svg)](https://circleci.com/gh/ESMValGroup/ESMValTool)
[![Codacy Coverage Badge](https://api.codacy.com/project/badge/Coverage/79bf6932c2e844eea15d0fb1ed7e415c)](https://www.codacy.com/app/ESMValGroup/ESMValTool?utm_source=github.com&utm_medium=referral&utm_content=ESMValGroup/ESMValTool&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/79bf6932c2e844eea15d0fb1ed7e415c)](https://www.codacy.com/app/ESMValGroup/ESMValTool?utm_source=github.com&utm_medium=referral&utm_content=ESMValGroup/ESMValTool&utm_campaign=Badge_Grade)
[![Docker Build Status](https://img.shields.io/docker/build/esmvalgroup/esmvaltool.svg)](https://hub.docker.com/r/esmvalgroup/esmvaltool/)
[![Anaconda-Server Badge](https://anaconda.org/esmvalgroup/esmvaltool/badges/installer/conda.svg)](https://conda.anaconda.org/esmvalgroup)

ESMValTool: A community diagnostic and performance metrics tool for routine evaluation of Earth system models in CMIP

# Getting started

This is the development branch for version 2 of ESMValTool. ESMValTool version 2 is under rapid development, an installation from source is recommended at the moment.

## Installing from source [recommended]

Please see [CONTRIBUTING.md](https://github.com/ESMValGroup/ESMValTool/blob/version2_development/CONTRIBUTING.md) for instructions on installing ESMValTool from source.

## Installing from Anaconda

The Anaconda package can be found on [ESMValGroup Anaconda Channel.](https://anaconda.org/ESMValGroup)

First [install Julia](https://julialang.org/downloads/) version 1 or greater, because this cannot be installed from conda.

If you already installed Anaconda, you can install ESMValTool by running:

    conda install -c esmvalgroup -c conda-forge esmvaltool

## Running ESMValTool

-   Review `config-user.yml`. To customize for your system, create a copy, edit and use the command line option `-c` to instruct `esmvaltool` to use your custom configuration.
-   Available recipes are located in the directory `esmvaltool/recipes`.
-   Run e.g. \`esmvaltool -c ~/config-user.yml examples/recipe_python.yml

## Getting help

The easiest way to get help if you cannot find the answer in the documentation on [readthedocs](https://esmvaltool.readthedocs.io), is to open an [issue on GitHub](https://github.com/ESMValGroup/ESMValTool/issues).

## Contributing

If you would like to contribute a new diagnostic or feature, please have a look at [CONTRIBUTING.md](https://github.com/ESMValGroup/ESMValTool/blob/version2_development/CONTRIBUTING.md).
