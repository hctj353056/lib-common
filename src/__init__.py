# -*- coding: utf-8 -*-
"""lib-common: reusable Python utilities for AI and application development."""
__version__ = "0.2.0"
__author__ = "蜉蝣 / FSG contributors"
from . import ai, cache, concurrency, config, logging, network, nlp, ssh, utils, vm
__all__ = ["ai", "cache", "concurrency", "config", "logging", "network", "nlp", "ssh", "utils", "vm", "version"]
def version():
    """Return the installed lib-common version."""
    return __version__
