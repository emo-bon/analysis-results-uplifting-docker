# analysis-results-uplifting-docker

This repository provides a dockerised executor of the [sema.subyt](https://github.com/vliz-be-opsci/py-sema) uplifting for the analysis results of emobon.

## About

The packaged artefacts from this work are available at https://github.com/orgs/emo-bon/packages.
Or they can be built locally by following the steps in [the developer docs](docs/contribute.md).

## Usage

To use this one only needs

1. to decide what image to run
   1. either a published release package
   2. or a local build
2. to set the i/o for the process
   1. mainly the ro-crate folder to work on (mapped as docker-volume `/rocrateroot`)
   2. essential environment variables to pass
3. pass all of the above in a call to `docker run`

In detail:

### using one of the published packages (docker-image)

```sh
$ version="latest" # or pick an available release tag from https://github.com/orgs/emo-bon/packages

# (optionally) verify availability by manual pull
$ docker pull ghcr.io/emo-bon/emobon_arup:${version}  # should pull the image without errors

# variable setting to inject
### Path to the root directory where analysis results are stored  
$ rocrateroot="../path_to_analysis_results_repo/crate_results_folder_X"
### Base domain URL for the data repository
$ DOMAIN='https://data.emobon.embrc.eu'
### Name of the repository where the analysis results are stored
$ REPO_NAME='analysis-results-cluster01-crate'
### Unique identifier for the sample during analysis, assigned by emo-bon
$ REF_CODE='EMOBON00172'
### Accession number for the sample in the European Nucleotide Archive (ENA)
$ ENA_NR='test_ENAnummer'
### Identifier for the Observatory
$ OBS_ID='VB' 
### Environmental package ID, categorizing the type of environment sampled: Wa (water), Se (sediment)
$ ENVPACKAGE_ID='Wa' 
### Identifier for the material sample used in the analysis  
$ SOURCE_MAT_ID='test_source_mat_id'

# actually run it
$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot --env SOURCE_MAT_ID=${source_mat_id} ghcr.io/emo-bon/emobon_arup:${version}
```

### using the local build docker-image

Taking this route assumes you have this project checked out with git, and have built it locally.
You might want to check the "developer info" section below for how to do that.

```sh
# build the docker image
# first get/update the git submodules from this repo
$ git submodule update --init --recursive
$ docker build -t emobon_arup .

# (optionally) verify if you have the local image available
$ docker images |grep emobon_arup  # should return a matching image

# variable setting to inject
$ rocrateroot="../path_to_analysis_results_repo/crate_results_folder_X"
$ source_mat_id="YourRefHere"

# actually run it
$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot --env SOURCE_MAT_ID=${source_mat_id} emobon_arup:latest
```

### I/O and background

The way to interact with this process is by

1. providing actual content to work on by mapping some folder to the docker `VOLUME /rocrateroot`
2. providing specific environment variables that can be picked up during execution.

These are explained to more detail below.

#### other sources of information

In addition to the above the process is driven by extra files that are built into the docker-image under the `/arup` folder. In particular the `/arup/work.yml` that contains the central instructions to be executed. And the templates present in the `/arup/templates/` folder.

The sources for these are in the root of this project.

#### the `/rocrateroot` volume

The reading and writing of actual files happens in the folder that is mapped to this volume.

It is expected to reflect the top of a folder that is to make up the ro-crate of one so called `analysis-result` -- the shared output of one MetaGoFlow execution.

In this folder the process will look for and use the files listed as `in`put in the `work.yml` instructions. In return it will produce the ones mentioned as `out`put in the same folder.

See the [`work.yml` instructions](work.yml) to learn what actual `in` and `out` paths, relative to `/rocrateroot` are being refered to.

#### consumed environment variables and their intent

The content and values of the instructions in the `work.yml` file can be tuned by the usage of environment variables. Using the yaml tag `!resolve` string values can be made to replace occurences of `{ env_variable_name }` by the value of the environment variable with that name.

See the [`work.yml` instructions](work.yml) to learn what actual `{ env_variable_name }`s are being used.

Additionally the environment variable `ARUP_WORK` allows to specify a path to a custom `work.yml` file of your own. This path should be absolute (expressed in docker-image space) or relative to its `/rocrateroot`. This feature is mainly there to allow for testing our own build process, use with caution.

## Developer info

To build your own local image, or to get involved in furthering this work:
See [Contributors Guide](./docs/contribute.md)
