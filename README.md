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
$ rocrateroot="../path_to_analysis_results_folder"

$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot ghcr.io/...:${version}
```

what is expected to be available in that folder
what you see as end result --> available new ttl files

#### using the local build

```sh
$ rocrateroot="../path_to_analysis_results_folder"
$ docker run --rm --name "emo-bon_arup" --volume ${rocrateroot}:/rocrateroot emobon_arup:latest
```

Note: This assumes you have a local build --> check the developer info for that

## Developer info

To build your own local image, or to get involved in furthering this work:
See [Contributors Guide](./docs/contribute.md)
