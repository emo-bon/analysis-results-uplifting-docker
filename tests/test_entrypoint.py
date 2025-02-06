from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_source(modname, filename):
    loader = SourceFileLoader(modname, filename)
    spec = spec_from_file_location(modname, filename, loader=loader)
    module = module_from_spec(spec)
    # The module is always executed and not cached in sys.modules.
    # Uncomment the following line to cache the module.
    # sys.modules[module.__name__] = module
    loader.exec_module(module)
    return module


def test_cli():
    entrypoint = load_source("entrypoint", "entrypoint.py")
    assert entrypoint._main
    root = Path(entrypoint.__file__).parent

    print(f"root={root !s}")
    entrypoint._main(
        workfile=root / "tests/test-work.yml",
        rocrateroot=root / "tests/data",
        templateroot=root / "templates",
        resultsroot=Path("/tmp"),  # todo use an actual temp folder
    )
    print("todo write test to verify results...")
