# Contributions

This is a short guide for people seeking to contribute.

## Project Artefacts

The build-system and github workflow of this project is setup so it builds a docker image.
(What it actually does is explained in the main [ReadMe](../README.md))

This docker image-build can be executed locally by anyone having the source code of this repository checked-out.
Additionally the gh-actions workflow of this project will automatically build them and publish them.
This makes them generally available at https://github.com/orgs/emo-bon/packages

## Dependencies

This project relies on the use of:

- git
- make
- python3, including pip, and the venv module
- docker

You will need these (and some usage experience) to be able to participate

## Makefile usage

The central `Makefile` in this project functions as the prime interaction-interface for all development actions.
It ensures a relatively low entrypoint and assures all involved follow the same way of working.
It also allows for automating some of the process through github-workflow so that automated build reflects manual build as much as possible.

### General make-targets

To list what can be built:

```sh
$ make
$ make help  # default target
```

To remove any build results from the local repository and possibly start over.

```sh
$ make clean
```

Note: this will not remove locally build docker images. See section below to clean those.

### Python related make-targets

To setup your local python environment, including needed dependencies.

```sh
$ make init
```

Note: This tracks if it already happened to avoid needless execution.
To avoid this check and force-built one can either `make clean` or fake need by `touch requirements.txt`
The latter might be needed if one of the dependencies is known to have updates available

To test the general operation of the python code (without the docker context)

```sh
$ make test
```

To check the syntax is conform to py-code conventions

```sh
$ make check
```

To make the syntax be conform to py-code conventions

```sh
$ make lint-fix
```

### Docker related make-targets

```sh
$ make docker-build
```

Note:
? how can I verify after this?
currently always rebuilds -- can we avoid? do we want to?

To manage these locally build images, check the docker documentation.
In general the following commands could help out with at least listing and removing them

```sh
# list all images locally found
$ docker images
# limited to those matching this project
$ PRJ="emobon_arup"
$ docker images | grep ${PRJ}
# same in custom output format for further processing
$ docker images --format="{{.ID}}|{{.Repository}}" | grep ${PRJ}
# with the above trick, one can loop, substract the id and execute the actual delete
$ for iid in $(docker images --format="{{.ID}}|{{.Repository}}"|grep ${PRJ}|awk -F '|' '{print $1}'); do\
    docker rmi -f $iid && echo "  > removed ${iid}" || echo "  > removal failed.";\
  done

```

```sh
$ make docker-push
```

Note: this includes the build
typically not called locally as it requires special credentials -- intended use is left to the automated build at gh

```sh
$ make docker-test
```

Note: does not include new build to avoid needless updates use `make docker-build docker-test` to test on a fresh build

## Submitting contributions

We expect our 'main' branch to build at all times.
Therefor we recommend working either on your own fork, or on a dedicated branch first and present a PR (PullRequest) from there.

Before declring your PR as "ready for review", please run these commands and assure a positive outcome

```sh
$ make check                    # --> assure alignment with py-code style
$ make test                     # --> assure local (docker-less) operation
$ make docker-build docker-test # --> assure docker-wrapped operation
```
