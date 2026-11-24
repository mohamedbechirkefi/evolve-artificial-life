# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Explicit error types. Every failure path raises one of these."""


class EvolveError(Exception):
    """Base class for all EVOLVE errors."""


class ConfigError(EvolveError, ValueError):
    """A configuration is malformed or violates a design rule (for example unequal budgets)."""


class InvariantError(EvolveError, RuntimeError):
    """A simulation invariant failed (for example consumed food does not match the grid)."""


class SchemaError(EvolveError, ValueError):
    """A result document does not match its versioned schema."""


class ProtocolNotFrozenError(EvolveError, PermissionError):
    """A confirmatory run was requested while the protocol is not frozen (gate G-FREEZE)."""
