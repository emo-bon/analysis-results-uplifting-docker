# analysis-results-uplifting-docker

dockerised executor of the sema.subyt uplifting for the analysis results

## Usage

### Info

- about available images (published at https://github.com/orgs/emo-bon/packages or locally build -- for people with some dev skills)
- about the io of this process --> `VOLUME /rocrateroot`
- todo check read-write access to that folder if any? (probably should not be an issue)

### Commands

#### using the published package

```sh
$ version="latest" # or pick an available release tag from https://github.com/orgs/emo-bon/packages

# (optionally) verify availability by manual pull
$ docker pull ghcr.io/emo-bon/emobon_arup:${version}  # should pull the image without errors

# variable setting to inject
$ rocrateroot="../path_to_analysis_results_repo/crate_results_folder_X"
$ source_mat_id="YourRefHere"

# actually run it
$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot --env SOURCE_MAT_ID=${source_mat_id} ghcr.io/emo-bon/emobon_arup:${version}
```

what is expected to be available in that folder
what you see as end result --> available new ttl files

#### using the local build

Taking this route assumes you have this project checked out with git, and have built it locally.
You might want to check the "developer info" section below for that.

```sh
# (optionally) verify if you have the local image available
$ docker images |grep emobon_arup  # should return a matching image

# variable setting to inject
$ rocrateroot="../path_to_analysis_results_repo/crate_results_folder_X"
$ source_mat_id="YourRefHere"

# actually run it
$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot --env SOURCE_MAT_ID=${source_mat_id} emobon_arup:latest
```

## Developer info

To build your own local image, or to get involved in furthering this work:
See [Contributors Guide](./docs/contribute.md)
