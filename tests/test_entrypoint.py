import filecmp
import os
import tempfile
from pathlib import Path

from conftest import entrypoint, log
from dotenv import load_dotenv
from rdflib import Graph
from sema.commons.glob import getMatchingGlobPaths


def test_cli():
    assert entrypoint._main
    root = Path(entrypoint.__file__).parent

    def build_and_verify(outdir: str | Path) -> None:
        outdir = Path(outdir)  # ensure Path type
        entrypoint._main(
            workfile=root / "tests/test-work.yml",
            rocrateroot=root / "tests/data",
            templateroot=root / "tests/templates",
            resultsroot=outdir,
        )
        # verify results
        resultfiles = getMatchingGlobPaths(
            outdir, includes=["*.ttl"], makeRelative=False
        )
        assert len(resultfiles) == 2
        # compare the ttl files, should be exactly the same
        assert filecmp.cmp(resultfiles[0], resultfiles[1], shallow=True)
        # try parsing the ttl files too
        for rf in resultfiles:
            assert rf.exists()
            assert rf.stat().st_size > 0
            Graph().parse(str(rf), format="ttl")

    load_dotenv()
    tmpdir = os.getenv("TEST_OUTFOLDER")
    if tmpdir:
        tmpdir = Path(tmpdir)
        tmpdir.mkdir(exist_ok=True, parents=True)
        log.info(
            f"Configured outfolder {tmpdir=} "
            "allows the output to be manually verified."
        )
        build_and_verify(tmpdir)
    else:
        log.info(
            "Temporary outfolder removed at end of test. "
            "Use environment TEST_OUTFOLDER to specify a permanent one."
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            build_and_verify(tmpdir)
