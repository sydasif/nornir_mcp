"""Result type implementation for Nornir MCP server.

This module provides a Result type that explicitly separates success and error paths,
improving type safety and making error handling more predictable throughout the codebase.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Success(Generic[T]):
    """Represents a successful operation result."""

    value: T

    def is_success(self) -> bool:
        """Check if this is a success result."""
        return True

    def is_error(self) -> bool:
        """Check if this is an error result."""
        return False

    def unwrap(self) -> T:
        """Extract the success value. Raises ValueError if this is an error."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Return the success value or the default."""
        return self.value

    def map(self, func: Callable[[T], T]) -> "Result[T, E]":
        """Apply function to success value, returning a new Result."""
        try:
            return Success(func(self.value))
        except Exception as e:
            # Return Error with consistent error_type and message
            return Error("mapping_error", str(e))

    def map_error(self, func: Callable[[E], E]) -> "Result[T, E]":
        """Apply function to error value (no-op for Success)."""
        return self


@dataclass
class Error(Generic[E]):
    """Represents a failed operation result."""

    error_type: str
    message: str

    def is_success(self) -> bool:
        """Check if this is a success result."""
        return False

    def is_error(self) -> bool:
        """Check if this is an error result."""
        return True

    def unwrap(self) -> E:
        """Raise exception on error. This method is kept for consistency but will raise."""
        raise ValueError(f"{self.error_type}: {self.message}")

    def unwrap_or(self, default: T) -> T:
        """Return the default value for error case."""
        return default

    def map(self, func: Callable[[T], T]) -> "Result[T, E]":
        """Apply function to success value (no-op for Error)."""
        return self

    def map_error(self, func: Callable[[str], str]) -> "Result[T, E]":
        """Apply function to error message, returning a new Result."""
        try:
            new_message = func(self.message)
            return Error(self.error_type, str(new_message))
        except Exception as e:
            return Error("mapping_error", str(e))


# Type alias for convenience
Result = Success[T] | Error[E]


def success(value: T) -> Success[T]:
    """Create a Success result with the given value."""
    return Success(value)


def error(error_type: str, message: str) -> Error[str]:
    """Create an Error result with the given error type and message."""
    return Error(error_type, message)
