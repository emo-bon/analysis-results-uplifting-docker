#! /usr/bin/env python3
import os
from pathlib import Path

from sema.commons.glob import getMatchingGlobPaths


def _main(
    *,
    rocrateroot: str = "/rocrateroot",
    templateroot: str = "/arup/templates",
    resultsroot: str | None = None,
) -> None:
    resultsroot = resultsroot or rocrateroot
    sample_mat_id: str = os.environ.get("SAMPLE_MAT_ID")

    print("TODO actual implementation ...")
    print(f"0/ check available {sample_mat_id=} variable")
    print(f"1/ check {rocrateroot} content...")
    print(f"2/ check {templateroot} content...")
    print("3/ run the actual aruplifting via subyt...")
    print("4/ reporting on available sq. valid outputs...")

    # for now we dump the contents of the /rocrateroot
    print(f"Contents of {rocrateroot}:")
    print(getMatchingGlobPaths(Path(rocrateroot)))

    # as well as the /arup/templates
    print(f"Contents of {templateroot}:")
    print(getMatchingGlobPaths(Path(templateroot)))


def main():
    _main()  # simply use all defaults


if __name__ == "__main__":
    main()
