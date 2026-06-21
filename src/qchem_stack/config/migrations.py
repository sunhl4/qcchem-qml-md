"""Configuration schema migration framework.

This module provides infrastructure for migrating experiment configurations
between schema versions. Migrations are applied sequentially and idempotently.

Usage:
    from qchem_stack.config.migrations import migrate_config, list_migrations

    # List all available migrations
    migrations = list_migrations()

    # Migrate a config dict to the latest version
    migrated = migrate_config(old_config_dict)

    # Or migrate a file
    from pathlib import Path
    import yaml
    config_path = Path("configs/old_experiment.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    migrated = migrate_config(config)
    with open(config_path, 'w') as f:
        yaml.dump(migrated, f)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Current schema version
SCHEMA_VERSION_CURRENT = "2"


class MigrationError(Exception):
    """Raised when a migration fails."""

    pass


class ConfigMigration(ABC):
    """Base class for configuration migrations.

    Each migration transforms a configuration from one schema version
    to the next. Migrations should be:
    - Idempotent: running the same migration twice should be safe
    - Atomic: either fully succeed or leave the config unchanged
    - Reversible: provide a rollback method if possible

    Attributes:
        from_version: Source schema version (e.g., "1")
        to_version: Target schema version (e.g., "2")
        description: Human-readable description of the migration
    """

    from_version: str
    to_version: str
    description: str

    @abstractmethod
    def migrate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply the migration to a configuration dict.

        Args:
            config: Configuration dictionary in the source schema version

        Returns:
            Migrated configuration dictionary in the target schema version

        Raises:
            MigrationError: If the migration fails
        """
        pass

    def rollback(self, config: dict[str, Any]) -> dict[str, Any]:
        """Reverse the migration (optional).

        Args:
            config: Configuration dictionary in the target schema version

        Returns:
            Configuration dictionary in the source schema version

        Raises:
            NotImplementedError: If rollback is not supported
        """
        raise NotImplementedError(f"Rollback not implemented for {self.__class__.__name__}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(v{self.from_version} -> v{self.to_version})"


from qchem_stack.config.migrations_v1_to_v2 import MigrationV1ToV2
from qchem_stack.config.migrations_v2_to_v3 import MigrationV3ToV2

# Migration registry - add new migrations here in order
_MIGRATIONS: list[type[ConfigMigration]] = [
    MigrationV1ToV2,
    MigrationV3ToV2,
]


def list_migrations() -> list[ConfigMigration]:
    """List all available migrations.

    Returns:
        List of migration instances in order
    """
    return [cls() for cls in _MIGRATIONS]


def get_schema_version(config: dict[str, Any]) -> str:
    """Get the schema version of a configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Schema version string, or "0" if not specified
    """
    version = config.get("schema_version", "0")
    return str(version).strip()


def migrate_config(
    config: dict[str, Any],
    from_version: str | None = None,
    to_version: str | None = None,
) -> dict[str, Any]:
    """Migrate a configuration to a target schema version.

    Applies migrations sequentially from the source version to the target
    version. If no versions are specified, migrates from the detected
    version to the current version.

    Args:
        config: Configuration dictionary to migrate
        from_version: Source schema version (auto-detected if None)
        to_version: Target schema version (defaults to current)

    Returns:
        Migrated configuration dictionary

    Raises:
        MigrationError: If migration fails or target version is unreachable
    """
    if from_version is None:
        from_version = get_schema_version(config)
    # Legacy flat YAML without schema_version is treated as v1 (pre-nested).
    if from_version == "0":
        from_version = "1"

    if to_version is None:
        to_version = SCHEMA_VERSION_CURRENT

    logger.info(f"Migrating config from v{from_version} to v{to_version}")

    # Build migration chain
    migrations = list_migrations()
    migration_chain: list[ConfigMigration] = []

    current_version = from_version
    while current_version != to_version:
        # Find next migration
        next_migration = None
        for migration in migrations:
            if migration.from_version == current_version:
                next_migration = migration
                break

        if next_migration is None:
            raise MigrationError(
                f"No migration path from v{current_version} to v{to_version}. "
                f"Available migrations: {[f'v{m.from_version}->v{m.to_version}' for m in migrations]}"
            )

        migration_chain.append(next_migration)
        current_version = next_migration.to_version

        # Prevent infinite loops
        if len(migration_chain) > len(migrations):
            raise MigrationError("Migration chain too long, possible cycle detected")

    # Apply migrations
    migrated = config.copy()
    for migration in migration_chain:
        logger.info(f"Applying migration: {migration.description}")
        try:
            migrated = migration.migrate(migrated)
        except Exception as e:
            raise MigrationError(f"Migration {migration} failed: {e}") from e

    return migrated


def migrate_config_file(
    config_path: str | Path,
    output_path: str | Path | None = None,
    backup: bool = True,
) -> Path:
    """Migrate a configuration file in place.

    Args:
        config_path: Path to the configuration file
        output_path: Output path (defaults to overwriting input)
        backup: Whether to create a backup before overwriting

    Returns:
        Path to the migrated configuration file

    Raises:
        MigrationError: If migration fails
    """
    import yaml

    config_path = Path(config_path)
    if not config_path.exists():
        raise MigrationError(f"Config file not found: {config_path}")

    output_path = config_path if output_path is None else Path(output_path)

    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise MigrationError(f"Config file must contain a YAML mapping, got {type(config)}")

    # Detect version and migrate
    from_version = get_schema_version(config)
    if from_version == SCHEMA_VERSION_CURRENT:
        logger.info(f"Config already at v{SCHEMA_VERSION_CURRENT}, no migration needed")
        return config_path

    migrated = migrate_config(config)

    # Backup original file
    if backup and output_path == config_path:
        backup_path = config_path.with_suffix(config_path.suffix + ".bak")
        logger.info(f"Creating backup: {backup_path}")
        backup_path.write_text(config_path.read_text())

    # Write migrated configuration
    with open(output_path, "w") as f:
        yaml.dump(migrated, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Migrated config written to: {output_path}")
    return output_path
