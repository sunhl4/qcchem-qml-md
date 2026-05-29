"""Toy surrogate models for experimentation.

Production MD/ML active-learning loops live in ``qchem_stack.md_bridge``
(``run_md_validation_loop``, QML-FF adapter). This package provides a minimal
Ridge surrogate and observation cache for demos only — not the main ML path.
"""

from qchem_stack.ml.active_learning import ActiveLearningLoop as ActiveLearningLoop
