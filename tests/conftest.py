from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from logging import Logger, getLogger
import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv

log: Logger = getLogger("tests")


def load_source(modname, filename):
    loader = SourceFileLoader(modname, filename)
    spec = spec_from_file_location(modname, filename, loader=loader)
    module = module_from_spec(spec)
    # The module is always executed and not cached in sys.modules.
    # Uncomment the following line to cache the module.
    # sys.modules[module.__name__] = module
    loader.exec_module(module)
    return module


entrypoint = load_source("entrypoint", "entrypoint.py")
root = Path(entrypoint.__file__).parent


@contextmanager
def tempdir_path():
    load_dotenv()
    tmpdir = os.getenv("TEST_OUTFOLDER")
    if tmpdir:
        tmpdir = Path(tmpdir)
        tmpdir.mkdir(exist_ok=True, parents=True)
        log.info(
            f"Configured outfolder {tmpdir=} "
            "allows the output to be manually verified."
        )
        yield tmpdir
    else:
        log.info(
            "Temporary outfolder removed at end of test. "
            "Use environment TEST_OUTFOLDER to specify a permanent one."
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
