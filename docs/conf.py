# Sphinx configuration for egfr40
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

import egfr40  # noqa: E402

project = "egfr40"
author = "Leonid Shpaner"
copyright = "2026, Leonid Shpaner"
release = egfr40.__version__
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

napoleon_numpy_docstring = True
napoleon_google_docstring = False
autodoc_member_order = "bysource"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = f"egfr40 {release}"
html_theme_options = {"navigation_depth": 3, "collapse_navigation": False}

# copy buttons skip prompts and output markers
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

rst_epilog = f"""
.. |version_str| replace:: {release}
"""
