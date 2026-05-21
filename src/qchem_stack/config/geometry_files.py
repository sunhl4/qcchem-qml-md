"""Load Cartesian molecular geometry from external structure files.

Supported today:

- **XYZ** (suffix ``.xyz``): first line = atom count, second = comment, then one
  ``symbol x y z`` row per atom (extra columns, as in extended XYZ, are ignored).

Paths in ``molecule.geometry_file`` are resolved relative to the experiment YAML
directory when using :func:`~qchem_stack.config.io.load_experiment_config`.

**Coordinate units (user-facing):** XYZ rows are copied verbatim into
``molecule.coordinates``; they are **not** converted to Bohr in this module.
``molecule.coordinate_unit`` (default ``angstrom`` on :class:`~qchem_stack.config.molecule.MoleculeSpec`)
defines how those numbers are interpreted; :meth:`~qchem_stack.config.molecule.MoleculeSpec.coordinates_in_bohr`
performs Å→Bohr when needed. Standard ``.xyz`` files are usually in ångströms—do not set
``coordinate_unit: bohr`` unless the file values are already in Bohr.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from qchem_stack.exceptions import ConfigurationError

if TYPE_CHECKING:
    from collections.abc import Mapping

GeometryFileFormat = Literal["xyz"]


def parse_xyz(text: str) -> tuple[list[str], list[list[float]]]:
    """Parse XYZ text into element symbols and Cartesian rows (Å by convention)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3:
        raise ConfigurationError(
            "XYZ structure needs at least three non-empty lines "
            "(atom count, comment, one atom row)."
        )
    first = lines[0].split()
    try:
        n = int(first[0])
    except (IndexError, ValueError) as exc:
        raise ConfigurationError(
            f"XYZ first line must begin with an integer atom count (got {lines[0]!r})."
        ) from exc
    if n <= 0:
        raise ConfigurationError(f"XYZ atom count must be positive (got {n}).")
    if len(lines) < 2 + n:
        raise ConfigurationError(
            f"XYZ expected {n} atom rows after the comment line, "
            f"but only {max(0, len(lines) - 2)} non-empty lines follow."
        )
    symbols: list[str] = []
    coordinates: list[list[float]] = []
    for i in range(2, 2 + n):
        parts = lines[i].split()
        if len(parts) < 4:
            raise ConfigurationError(
                f"XYZ atom line {i - 1}: need at least symbol + three floats, got {lines[i]!r}."
            )
        sym = str(parts[0])
        try:
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        except ValueError as exc:
            raise ConfigurationError(
                f"XYZ atom line {i - 1}: could not parse three Cartesian floats from {lines[i]!r}."
            ) from exc
        symbols.append(sym)
        coordinates.append([x, y, z])
    return symbols, coordinates


def load_cartesian_geometry_file(
    path: Path,
    *,
    file_format: GeometryFileFormat | None = None,
) -> tuple[list[str], list[list[float]]]:
    """Read a structure file from disk and return symbols + Cartesian coordinates."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Geometry file not found: {path}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Could not read geometry file {path}: {exc}") from exc

    fmt = file_format or _infer_geometry_format(path)
    if fmt == "xyz":
        return parse_xyz(text)
    raise ConfigurationError(f"Unsupported geometry file format {fmt!r} ({path}).")


def _infer_geometry_format(path: Path) -> GeometryFileFormat:
    suf = path.suffix.lower()
    if suf == ".xyz":
        return "xyz"
    raise ConfigurationError(
        f"Cannot infer geometry format for {path} (suffix {path.suffix!r}). "
        "Supported: .xyz — or pass file_format='xyz' when calling load_cartesian_geometry_file."
    )


def resolve_geometry_file_path(path_str: str, *, base_dir: Path) -> Path:
    """Resolve ``path_str`` to an absolute path (absolute inputs ignore ``base_dir``)."""
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (base_dir / p).resolve()


def merge_molecule_dict_from_geometry_file(
    molecule: Mapping[str, Any],
    *,
    base_dir: Path,
) -> dict[str, Any]:
    """Expand ``geometry_file`` into ``symbols`` and ``coordinates``; drop loader-only keys.

    ``coordinate_unit`` is passed through unchanged. This function does **not** convert
    units; :meth:`~qchem_stack.config.molecule.MoleculeSpec.coordinates_in_bohr` applies
    ``coordinate_unit`` later. For typical ``.xyz`` files use ``coordinate_unit: angstrom``
    in YAML (see ``docs/说明_molecule配置与自旋多重度.md`` §1.1).
    """
    if "geometry_file" not in molecule or molecule["geometry_file"] is None:
        return dict(molecule)
    path_raw = molecule["geometry_file"]
    if not isinstance(path_raw, str) or not path_raw.strip():
        raise ConfigurationError("molecule.geometry_file must be a non-empty string path.")

    conflicts = [k for k in ("coordinates", "zmatrix") if molecule.get(k)]
    if conflicts:
        raise ConfigurationError(
            "molecule.geometry_file cannot be used together with inline geometry fields "
            f"{conflicts!r}; remove those keys or omit geometry_file."
        )

    fmt_raw = molecule.get("geometry_file_format")
    file_format: GeometryFileFormat | None
    if fmt_raw is None or fmt_raw == "":
        file_format = None
    elif fmt_raw == "xyz":
        file_format = "xyz"
    else:
        raise ConfigurationError(
            f"molecule.geometry_file_format must be 'xyz' or omitted (got {fmt_raw!r})."
        )

    gpath = resolve_geometry_file_path(path_raw.strip(), base_dir=base_dir)
    symbols, coordinates = load_cartesian_geometry_file(gpath, file_format=file_format)

    yaml_symbols = molecule.get("symbols")
    if yaml_symbols is not None:
        if not isinstance(yaml_symbols, list) or any(not isinstance(s, str) for s in yaml_symbols):
            raise ConfigurationError("molecule.symbols must be a list of strings when provided.")
        if list(yaml_symbols) != symbols:
            raise ConfigurationError(
                "molecule.symbols disagrees with symbols from geometry_file "
                f"(YAML has {list(yaml_symbols)!r}, file has {symbols!r})."
            )

    out = dict(molecule)
    out.pop("geometry_file", None)
    out.pop("geometry_file_format", None)
    out["symbols"] = symbols
    out["coordinates"] = coordinates
    return out


def preprocess_experiment_dict_geometry_files(data: dict[str, Any], *, base_dir: Path) -> None:
    """In-place: if ``molecule.geometry_file`` is set, merge file geometry before Pydantic."""
    mol = data.get("molecule")
    if not isinstance(mol, dict):
        return
    data["molecule"] = merge_molecule_dict_from_geometry_file(mol, base_dir=base_dir)
