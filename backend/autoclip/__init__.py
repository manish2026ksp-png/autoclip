"""AutoClip — open-source, local-first AI video clipper."""

__version__ = "0.1.0.dev0"

from .paths import configure_cache_environment as _configure_cache_environment

_configure_cache_environment()

__all__ = ["__version__"]
