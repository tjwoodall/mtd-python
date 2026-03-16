from typing import Callable, TypeVar, Any

_F = TypeVar("_F", bound=Callable[..., Any])

def typechecked(fn: _F) -> _F: ...
