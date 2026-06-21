"""Schema v1 -> v2 migration implementation."""

from __future__ import annotations

import logging
from typing import Any

from qchem_stack.config.migrations import ConfigMigration, MigrationError

logger = logging.getLogger(__name__)


class MigrationV1ToV2(ConfigMigration):
    """Migration from schema v1 (flat YAML) to v2 (nested YAML).

    This migration handles legacy configurations that used a flat structure
    with underscore-prefixed keys (e.g., 'quantum_algorithm') and converts
    them to the nested structure (e.g., 'quantum.algorithm').

    Changes:
    - Moves flat keys into nested sections
    - Adds schema_version field set to "2"
    - Renames deprecated fields
    """

    from_version = "1"
    to_version = "2"
    description = "Convert flat YAML structure to nested YAML format"

    # Mapping from old flat keys to new nested paths
    KEY_MAPPINGS = {
        # Quantum section
        "quantum_algorithm": ("quantum", "algorithm"),
        "quantum_algorithm_factory": ("quantum", "algorithm_factory"),
        "quantum_ansatz": ("quantum", "variational", "ansatz"),
        "quantum_vqe_depth": ("quantum", "vqe", "depth"),
        "quantum_vqe_maxiter": ("quantum", "vqe", "maxiter"),
        "quantum_adapt_max_iter": ("quantum", "adapt", "max_iter"),
        "quantum_iqeb_max_rounds": ("quantum", "iqeb", "max_rounds"),
        # Backend section
        "backend_name": ("backend", "name"),
        "backend_provider": ("backend", "provider"),
        "backend_shots_per_circuit": ("backend", "shots_per_circuit"),
        "backend_qiskit_mode": ("backend", "qiskit_mode"),
        # Active space section
        "active_space_strategy": ("active_space", "strategy"),
        "active_space_n_orbitals": ("active_space", "manual", "n_orbitals"),
        "active_space_n_electrons": ("active_space", "manual", "n_electrons"),
        # Mitigation section
        "mitigation_zne_enabled": ("mitigation", "zne", "enabled"),
        "mitigation_zne_scales": ("mitigation", "zne", "scales"),
        "mitigation_pmsv_enabled": ("mitigation", "pmsv", "enabled"),
        "mitigation_pmsv_stabilizers": ("mitigation", "pmsv", "stabilizers"),
        # SCF section
        "scf_driver": ("scf", "driver"),
        "scf_method": ("scf", "method"),
        "scf_max_cycle": ("scf", "max_cycle"),
    }

    def migrate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply v1 to v2 migration."""
        if config.get("schema_version") == "2":
            logger.info("Config already at v2, skipping migration")
            return config

        migrated = {}
        unmapped_keys = []

        # Process each key in the original config
        for key, value in config.items():
            if key in self.KEY_MAPPINGS:
                # Map to nested structure
                target_path = self.KEY_MAPPINGS[key]
                self._set_nested_value(migrated, target_path, value)
            elif key == "schema_version":
                # Will be set at the end
                continue
            else:
                # Keep unmapped keys as-is (might be top-level fields like experiment_id)
                unmapped_keys.append(key)
                migrated[key] = value

        # Set schema version to 2
        migrated["schema_version"] = "2"

        if unmapped_keys:
            logger.warning(
                f"Migration v1->v2: {len(unmapped_keys)} keys were not mapped and kept as-is: "
                f"{unmapped_keys[:5]}{'...' if len(unmapped_keys) > 5 else ''}"
            )

        return migrated

    def rollback(self, config: dict[str, Any]) -> dict[str, Any]:
        """Reverse v2 to v1 migration (flatten nested structure)."""
        if config.get("schema_version") != "2":
            raise MigrationError("Rollback only supported for v2 configs")

        rolled_back = {}

        # Reverse the key mappings
        for flat_key, nested_path in self.KEY_MAPPINGS.items():
            value = self._get_nested_value(config, nested_path)
            if value is not None:
                rolled_back[flat_key] = value

        # Copy top-level fields that weren't part of the mapping
        for key, value in config.items():
            if key not in (
                "schema_version",
                "quantum",
                "backend",
                "active_space",
                "mitigation",
                "scf",
                "chemistry_extended",
            ):
                rolled_back[key] = value

        # Remove schema_version for v1
        rolled_back.pop("schema_version", None)

        return rolled_back

    @staticmethod
    def _set_nested_value(config: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
        """Set a value in a nested dictionary using a path tuple."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    @staticmethod
    def _get_nested_value(config: dict[str, Any], path: tuple[str, ...]) -> Any:
        """Get a value from a nested dictionary using a path tuple."""
        current = config
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current
