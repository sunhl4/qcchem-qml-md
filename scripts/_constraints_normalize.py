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


def pip_compile_base_cmd(pip_compile_exe: str, output_file: str) -> list[str]:
    """Shared pip-compile flags for update + freshness check."""
    return [
        pip_compile_exe,
        "--output-file",
        output_file,
        "--upgrade",
        "--no-header",
        "--no-annotate",
        "--strip-extras",
        "--no-emit-index-url",
        "--no-emit-trusted-host",
        "--no-emit-options",
    ]
