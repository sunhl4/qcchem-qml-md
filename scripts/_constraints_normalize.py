"""Normalize pip-compile output for cross-platform constraint files."""

from __future__ import annotations

# ipython pulls appnope on macOS only; omit from shared Linux/macOS lockfiles.
_MAC_ONLY_PACKAGES = frozenset({"appnope==0.1.4"})


def normalize_constraints_text(text: str) -> str:
    """Strip local pip config noise and platform-specific pins."""
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("--index-url") or line.startswith("--trusted-host"):
            continue
        if line in _MAC_ONLY_PACKAGES:
            continue
        if line.startswith("qchem-stack @"):
            lines.append("qchem-stack @ file:.")
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def pip_compile_update_cmd(pip_compile_exe: str, output_file: str) -> list[str]:
    """Full upgrade resolve when refreshing committed lockfiles."""
    return [
        pip_compile_exe,
        "--output-file",
        output_file,
        "--upgrade",
        *_pip_compile_emit_flags(),
    ]


def pip_compile_check_cmd(
    pip_compile_exe: str, output_file: str, constraint_file: str
) -> list[str]:
    """Re-resolve under existing pins (cross-platform stable vs --upgrade)."""
    return [
        pip_compile_exe,
        "--output-file",
        output_file,
        "--constraint",
        constraint_file,
        *_pip_compile_emit_flags(),
    ]


def _pip_compile_emit_flags() -> list[str]:
    return [
        "--no-header",
        "--no-annotate",
        "--strip-extras",
        "--no-emit-index-url",
        "--no-emit-trusted-host",
        "--no-emit-options",
    ]


# Back-compat alias for update_constraints.py
def pip_compile_base_cmd(pip_compile_exe: str, output_file: str) -> list[str]:
    return pip_compile_update_cmd(pip_compile_exe, output_file)
