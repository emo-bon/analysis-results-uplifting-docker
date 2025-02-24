from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


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
