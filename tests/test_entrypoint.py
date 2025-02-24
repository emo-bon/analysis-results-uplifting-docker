import filecmp
from pathlib import Path
from conftest import entrypoint, root, tempdir_path
from rdflib import Graph
from sema.commons.glob import getMatchingGlobPaths


def verify_build(outdir: Path) -> None:
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


def test_basics():
    assert entrypoint._main

    def build_and_verify(outdir: Path) -> None:
        entrypoint._main(
            workfile=root / "tests/test-work.yml",
            rocrateroot=root / "tests/data",
            templateroot=root / "tests/templates",
            resultsroot=outdir,
        )
        verify_build(outdir)

    with tempdir_path() as tmpdir:
        build_and_verify(tmpdir)
