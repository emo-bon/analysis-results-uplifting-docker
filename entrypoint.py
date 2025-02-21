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

        self._preparations = []
        self._jobs = []
        self._location_mappings = dict()

        self.load_jobs(workfile)
        if len(self._jobs) == 0:
            raise ValueError(f"no jobs found in {workfile !s}")

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
        abs_input: str = str((self._rocrateroot / input).absolute())
        # if this desired input is in the prepout mappings, then return that!
        return self._location_mappings.get(abs_input, abs_input)

    def _prepout_location(self, output: str) -> str:
        # prepouts need to go to the resultsroot
        abs_output: str = str((self._resultsroot / output).absolute())
        # but they will be referenced in the subyt jobs as input
        abs_input: str = str((self._rocrateroot / output).absolute())
        # so we add them to the mapping
        self._location_mappings[abs_input] = abs_output
        return abs_output

    def _output_location(self, output: str) -> str:
        return str((self._resultsroot / output).absolute())

    def load_jobs(self, workfile: Path) -> None:
        """Converts the instructions in the workfile into a list of jobs.
        These jobs are grouped into 'preparation' and 'subyt' jobs.
        The preparation jobs are expressing text/csv manipulations to allow
        file copy and header inclusion.
        The subyt jobs are expressing semantic-uplifting tasks producing ttl.
        These jobs are all actually argument-dicts that can
        simply be passed to an exuting methos."""
        instructions: dict = SubytJobs.load_instructions(workfile)
        # todo grab the vars from the instructions
        vars: dict = {
            var["name"]: var["value"] for var in instructions.get("vars", {})
        }
        log.debug(f"found {vars=} @instructions")
        self._load_prep_jobs(instructions)
        self._load_subyt_jobs(instructions, vars)

    def _load_prep_jobs(self, instructions: dict) -> None:
        # run over the prepare instructions, assemble into jobs
        for prep in instructions.get("prepare", {}):
            # minimal required keys in job
            if not {"input", "output"} <= set(prep.keys()):
                log.warning(
                    f"prepare instruction {prep !s} must have at least"
                    "an input and output. Skipping...",
                )
                continue
            # just copy cover all settings from the yml (grow as needed)
            prepjob = prep.copy()
            # then additionally:
            # resolve paths relative to their respective roots
            prepjob["input"] = self._input_location(prep.get("input"))
            prepjob["output"] = self._prepout_location(prep.get("output"))
            self._preparations.append(prepjob)

    def _load_subyt_jobs(self, instructions: dict, vars: dict) -> None:
        # run over the subyt instructions, assemble into jobs
        for subyt in instructions.get("subyt", {}):
            # minimal required keys in job
            if not {"template_name", "sink"} <= set(subyt.keys()):
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
            self._jobs.append(job)

    @staticmethod
    def _prepare_file(
        *, input: str, output: str, header: str | None = None
    ) -> None:
        """Copies the input file to the output file.
        If a header is provided, it is prepended to the output file."""
        log.debug(f"preparing file {input !s} -> {output !s}")
        with open(output, "w") as outf:
            if header:
                outf.write(header.strip() + "\n")
            with open(input, "r") as inf:
                # streamingly for large files - move line by line
                for line in inf:
                    outf.write(line)

    def _prepare(self):
        """Executes the prepare-file-jobs in the workfile."""
        log.debug("running the uplifting jobs...")
        prepjob: dict
        for prepjob in self._preparations:
            log.debug(f"running job {prepjob !s}")
            SubytJobs._prepare_file(**prepjob)

    def _subyt(self):
        log.debug("running the uplifting jobs...")
        job: dict
        for job in self._jobs:
            log.debug(f"running job {job !s}")
            subyt = Subyt(**job)
            subyt.process()

        log.debug("TODO reporting on available sq. valid outputs...")

    def run(self):
        """Runs the jobs in the workfile."""
        self._prepare()
        self._subyt()


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
