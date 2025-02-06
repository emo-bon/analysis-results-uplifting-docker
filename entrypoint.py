#! /usr/bin/env python3
import os
from pathlib import Path

from sema.commons.glob import getMatchingGlobPaths
from sema.commons.yml import LoaderBuilder
from sema.subyt import Subyt
import yaml
from logging import Logger, getLogger


log: Logger = getLogger(__name__)


class ArupLifting:
    def __init__(self, workfile: Path, rocrateroot: Path, templateroot: Path, resultsroot: Path) -> None:
        self._rocrateroot = rocrateroot
        log.debug(
            f"{self._rocrateroot !s} content...\n"
            f"{getMatchingGlobPaths(self._rocrateroot)}"
        )

        self._templateroot = templateroot
        log.debug(
            f"{self._templateroot !s} content...\n"
            f"{getMatchingGlobPaths(self._templateroot)}"
        )

        self._resultsroot = resultsroot
        log.debug(
            f"{self._resultsroot !s} is...\n"
            f" - isdir: {self._resultsroot.is_dir()}\n"
            f" - writeable: {os.access(self._resultsroot, os.W_OK)}"
        )

        self._work = self.load_work(workfile)
        log.debug(f"jobs to do is #{len(self._work)}")

    def run(self):
        sample_mat_id: str = os.environ.get("SAMPLE_MAT_ID")
        log.debug(f"demo test of {sample_mat_id=} variable")

        log.debug("running the jobs...")
        for job in self._work:
            log.debug(f"running job {job}")
            subyt = Subyt(**job)
            subyt.run()

        log.debug("TODO reporting on available sq. valid outputs...")

    @staticmethod
    def load_instructions(workfile: Path) -> dict:
        log.debug(f"loading instructions from {workfile !s} using ENVIRONMENT as resolve context")
        env: dict = os.environ.copy()
        loader = LoaderBuilder().to_resolve(env).build()
        with workfile.open("r") as yml:
            return yaml.load(yml, Loader=loader)

    def load_work(self, workfile: Path) -> list[dict]:
        """Converts the instructions in the workfile into a list of jobs.
        These jobs are argument-dicts that can be passed to the Subyt constructor."""
        instructions: dict = ArupLifting.load_instructions(workfile)
        # todo grab the vars from the instructions
        vars = {var['name']: var['value'] for var in instructions.get("vars", {})}
        log.debug(f"found {vars=} @instructions")
        jobs: list[dict] = []
        # run over the subyt instructions, assemble into jobs
        # each job to include:
        #  - template_name: str
        #  - template_folder: str,
        #  - source: str | None = None,
        #  - extra_sources: Dict[str, str] | None = None,
        #  - sink: str | None = None,
        #  - overwrite_sink: bool | str = True,
        #  - allow_repeated_sink_paths: bool | str = False,
        #  - conditional: bool | str = False,
        #  - break_on_error: bool | str = False,
        #  - variables: Dict[str, str] = {},
        #  - mode: str = "it",
        return jobs


def _main(
    *,
    workfile: str = "/arup/work.yml",
    rocrateroot: str = "/rocrateroot",
    templateroot: str = "/arup/templates",
    resultsroot: str | None = None,
) -> None:
    workfile = Path(workfile)
    rocrateroot = Path(rocrateroot)
    templateroot = Path(templateroot)
    resultsroot = resultsroot or rocrateroot

    arup = ArupLifting(workfile, rocrateroot, templateroot, resultsroot)
    arup.run()


def main():
    _main()  # simply use all defaults


if __name__ == "__main__":
    main()
