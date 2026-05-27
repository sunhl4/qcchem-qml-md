"""End-to-end smoke for ``qchem_stack.md_bridge.qchem_labeler`` on H2.

Requires PySCF (cold-start runs the full pipeline). Marked ``l1_md_ml`` and
``pyscf`` so it is skipped on the no-chemistry CI lane.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.l1_md_ml, pytest.mark.pyscf]

pytest.importorskip("pyscf")


_REPO_ROOT = Path(__file__).resolve().parents[1]
_H2_YAML = _REPO_ROOT / "configs" / "example_h2.yaml"


@pytest.fixture(scope="module")
def h2_yaml() -> Path:
    if not _H2_YAML.is_file():
        pytest.skip(f"missing {_H2_YAML}")
    return _H2_YAML


def test_label_base_geometry_only_returns_one_frame(h2_yaml) -> None:
    from qchem_stack.md_bridge import label_base_geometry_only

    result = label_base_geometry_only(
        h2_yaml,
        energy_reference="scf",  # cheapest path
        include_hf_nuclear_gradient=True,
    )
    assert result.dataset.frames, "base labeling produced zero frames"
    fr = result.dataset.frames[0]
    assert fr.atomic_numbers == [1, 1], f"expected H2 (Z=1,1); got {fr.atomic_numbers}"
    assert len(fr.positions_bohr) == 2
    assert fr.energy_hartree < 0, "H2 RHF energy should be negative"
    # Force attachment was requested; PySCF gradient should succeed for H2.
    assert len(fr.forces_hartree_bohr) == 2
    assert result.primary_repro_config_sha256_prefix


def test_label_geometries_with_pipeline_hf_scf_path(h2_yaml) -> None:
    from qchem_stack.md_bridge import label_geometries_with_pipeline

    extras = [
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.30]],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.50]],
    ]
    res = label_geometries_with_pipeline(
        h2_yaml,
        extra_coordinates_bohr=extras,
        energy_reference="scf",
        theory_level="hf_scf",
        include_hf_nuclear_gradient=False,
        failure_isolation=False,
    )
    # Always: 1 base + 2 extras.
    assert len(res.dataset.frames) == 3
    assert all(fr.atomic_numbers == [1, 1] for fr in res.dataset.frames)
    # Energies should differ between bond lengths
    energies = [fr.energy_hartree for fr in res.dataset.frames]
    assert len({round(e, 6) for e in energies}) >= 2, (
        f"expected distinct energies across H2 stretches, got {energies}"
    )


def test_label_geometries_failure_isolation_skips_broken_frames(h2_yaml, tmp_path) -> None:
    """If one geometry blows up PySCF, isolation must keep the good frames."""
    from qchem_stack.md_bridge import label_geometries_with_pipeline

    extras = [
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.35]],
        # Two H nuclei stacked at the same point ⇒ PySCF should error out.
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
    ]
    res = label_geometries_with_pipeline(
        h2_yaml,
        extra_coordinates_bohr=extras,
        energy_reference="scf",
        theory_level="hf_scf",
        include_hf_nuclear_gradient=False,
        failure_isolation=True,
    )
    assert res.dataset.frames, "should still have base frame after isolation"
    # We can't strictly assert 1 failure here because some PySCF versions tolerate
    # degenerate geometries; we only check the isolation path executed at all.
    if res.failures:
        assert res.failures[0].index == 1
