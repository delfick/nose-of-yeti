extensions = ["sphinx.ext.autodoc", "sphinx_rtd_theme"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/extra.css"]

exclude_patterns = ["_build/**", ".sphinx-build/**", "README.rst"]

master_doc = "index"
source_suffix = ".rst"

pygments_style = "pastie"

copyright = "2020, delfick"
project = "noseOfYeti"

version = "0.1"
release = "0.1"
