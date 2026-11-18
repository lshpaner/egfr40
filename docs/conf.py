# Sphinx configuration for egfr40
import os
import shutil
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
    "myst_nb",
]

# Notebooks live in ../notebooks (committed without outputs). Copy the ones
# that run without external data into the docs tree; myst-nb executes them
# at build time so the published pages show outputs.
_NB_SRC = os.path.abspath("../notebooks")
_NB_DST = os.path.abspath("_notebooks")
os.makedirs(_NB_DST, exist_ok=True)
for _nb in ["00_quickstart.ipynb"]:
    shutil.copy2(os.path.join(_NB_SRC, _nb), os.path.join(_NB_DST, _nb))

nb_execution_mode = "force"
nb_execution_timeout = 120
nb_execution_raise_on_error = True
nb_merge_streams = True

napoleon_numpy_docstring = True
napoleon_google_docstring = False
autodoc_member_order = "bysource"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "jupyter_execute"]

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
