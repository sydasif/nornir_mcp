"""Constants and enumerations for the Nornir MCP server.

This module contains all constant values used throughout the application
to ensure consistency and prevent typos.
"""

from enum import StrEnum


class ErrorType(StrEnum):
    """Error type identifiers for MCP error responses."""

    NO_HOSTS = "no_hosts"
    INVALID_PARAMETERS = "invalid_parameters"
    INVALID_GETTER = "invalid_getter"
    INVALID_COMMAND = "invalid_command"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_ERROR = "execution_error"
    CONFIG_MISSING = "config_missing"
    INVENTORY_RETRIEVAL_FAILED = "inventory_retrieval_failed"
    GETTERS_RETRIEVAL_FAILED = "getters_retrieval_failed"
    GETTERS_NOT_FOUND = "getters_not_found"
    NETMIKO_COMMANDS_RETRIEVAL_FAILED = "netmiko_commands_retrieval_failed"
    NETMIKO_COMMANDS_NOT_FOUND = "netmiko_commands_not_found"
    RELOAD_FAILED = "reload_failed"
    TOOL_ERROR = "tool_error"


class Backend(StrEnum):
    """Automation backend identifiers."""

    NAPALM = "napalm"
    NETMIKO = "netmiko"
    PARAMIKO = "paramiko"


class TargetType(StrEnum):
    """Target type identifiers for device filtering."""

    ALL = "all"
    HOST = "host"
    GROUP = "group"


class ConfigKey(StrEnum):
    """Configuration file keys."""

    GETTERS = "getters"
    NETMIKO_COMMANDS = "netmiko_commands"


class EnvVar(StrEnum):
    """Environment variable names."""

    NORNIR_CONFIG_FILE = "NORNIR_CONFIG_FILE"


class DefaultValue(StrEnum):
    """Default values for configuration."""

    CONFIG_FILENAME = "config.yaml"
    CAPABILITIES_FILENAME = "capabilities.yaml"
