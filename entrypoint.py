#! /usr/bin/env python3
import os
from logging import Logger, getLogger
from pathlib import Path

import yaml
from sema.commons.glob import getMatchingGlobPaths
from sema.commons.yml import LoaderBuilder
from sema.subyt import Subyt

log: Logger = getLogger(__name__)


class SubytJobs:
    """Helper class executing the Subyt jobs as per the instructionsi
    in the workfile."""

    def __init__(
        self,
        workfile: Path,
        rocrateroot: Path,
        templateroot: Path,
        resultsroot: Path,
    ) -> None:
        """Initialises the SubytJobs object with the given paths.
        Errors are raised if the paths are invalid or the workfile is empty."""
        self._rocrateroot = rocrateroot
        if not self._rocrateroot.is_dir():
            raise FileNotFoundError(
                f"{self._rocrateroot !s} is not a directory",
            )
        if len(getMatchingGlobPaths(self._rocrateroot)) == 0:
            raise FileNotFoundError(f"{self._rocrateroot !s} is empty")

        self._templateroot = templateroot
        if not self._templateroot.is_dir():
            raise FileNotFoundError(
                f"{self._templateroot !s} is not a directory",
            )
        if len(getMatchingGlobPaths(self._templateroot)) == 0:
            raise FileNotFoundError(f"{self._templateroot !s} is empty")

        self._resultsroot = resultsroot
        if not self._resultsroot.is_dir():
            raise FileNotFoundError(
                f"{self._resultsroot !s} is not a directory",
            )
        if not os.access(self._resultsroot, os.W_OK):
            raise PermissionError(f"{self._resultsroot !s} is not writeable")

        self._jobs = self.load_jobs(workfile)
        if len(self._jobs) == 0:
            raise ValueError(f"no jobs found in {workfile !s}")

    def run(self):
        """Runs the jobs in the workfile."""
        log.debug("running the jobs...")
        job: dict
        for job in self._jobs:
            log.debug(f"running job {job !s}")
            subyt = Subyt(**job)
            subyt.process()

        log.debug("TODO reporting on available sq. valid outputs...")

    @staticmethod
    def load_instructions(workfile: Path) -> dict:
        log.debug(
            f"loading instructions from {workfile !s}"
            "using ENVIRONMENT as resolve context",
        )
        env: dict = os.environ.copy()
        loader = LoaderBuilder().to_resolve(env).build()
        with workfile.open("r") as yml:
            return yaml.load(yml, Loader=loader)

    def _input_location(self, input: str) -> str:
        return str((self._rocrateroot / input).absolute())

    def _output_location(self, output: str) -> str:
        return str((self._resultsroot / output).absolute())

    def load_jobs(self, workfile: Path) -> list[dict]:
        """Converts the instructions in the workfile into a list of jobs.
        These jobs are actually argument-dicts that can
        simply be passed to the Subyt constructor."""
        instructions: dict = SubytJobs.load_instructions(workfile)
        # todo grab the vars from the instructions
        vars = {
            var["name"]: var["value"] for var in instructions.get("vars", {})
        }
        log.debug(f"found {vars=} @instructions")
        jobs: list[dict] = []
        # run over the subyt instructions, assemble into jobs
        for subyt in instructions.get("subyt", {}):
            if not {"template_name", "sink"} <= set(
                subyt.keys()
            ):  # minimal required keys
                log.warning(
                    f"subyt instruction {subyt !s} must have at least"
                    "a source, template_name and sink. Skipping...",
                )
                continue
            # just copy cover all settings from the yml (grow as needed)
            job = subyt.copy()
            # then additionally:
            # 1: add fixed stuff from the arup processing
            job["template_folder"] = str(self._templateroot.absolute())
            job["variables"] = vars
            # 2: resolve paths relative to their respective roots
            job["source"] = self._input_location(job.get("source"))
            job["extra_sources"] = {
                name: self._input_location(inp)
                for name, inp in job.get("extra_sources", {}).items()
            }
            job["sink"] = self._output_location(job.get("sink"))
            jobs.append(job)
        return jobs


def _main(
    *,
    workfile: str = None,
    rocrateroot: str = "/rocrateroot",
    templateroot: str = "/arup/templates",
    resultsroot: str | None = None,
) -> None:
    rocrateroot = Path(rocrateroot)

    # allow env var to be relative to rocrateroot or absolute
    workfile = workfile or os.environ.get("ARUP_WORK", "/arup/work.yml")
    workfile = rocrateroot / Path(workfile)

    templateroot = Path(templateroot)
    resultsroot = resultsroot or rocrateroot

    uplifting = SubytJobs(workfile, rocrateroot, templateroot, resultsroot)
    uplifting.run()


def main():
    _main()  # simply use all defaults


if __name__ == "__main__":
    main()
