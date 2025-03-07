import filecmp
from pathlib import Path
from conftest import entrypoint, root, tempdir_path, log
from rdflib import Graph


def verify_build(outdir: Path, workfile: Path) -> None:
    # load the workfile, grab the expected outputs
    log.debug(f"Verifying build in {outdir}")
    log.debug(f"Using workfile {workfile}")
    workdict = entrypoint.SubytJobs.load_instructions(workfile)
    log.debug(f"Workfile loaded and subyt tasks found: {workdict['subyt']}")
    expectedfiles: list[Path] = [
        outdir / job.get('sink')
        for job in workdict["subyt"]
    ]

    for ef in expectedfiles:
        assert ef.exists()
        assert ef.stat().st_size > 0
        Graph().parse(str(ef), format="ttl")


def test_basics():
    log.debug("test_basics")
    assert entrypoint._main

    def build_and_verify(outdir: Path) -> None:
        workfile = root / "tests/test-work.yml"
        entrypoint._main(
            workfile=workfile,
            rocrateroot=root / "tests/data",
            templateroot=root / "tests/templates",
            resultsroot=outdir,
        )
        verify_build(outdir, workfile)
        assert filecmp.cmp(
            outdir / "test-output.ttl",
            outdir / "test-output2.ttl",
        )

    with tempdir_path() as tmpdir:
        build_and_verify(tmpdir)


def test_arup_templating():
    log.debug("test_arup_templating")
    assert entrypoint._main

    def build_and_verify(outdir: Path) -> None:
        workfile = root / "work.yml"
        entrypoint._main(
            workfile=workfile,
            rocrateroot=root / "tests/data",
            templateroot=root / "templates",
            resultsroot=outdir,
        )
        verify_build(outdir, workfile)
        # TODO: verify the templating more extensively

    with tempdir_path() as tmpdir:
        build_and_verify(tmpdir)