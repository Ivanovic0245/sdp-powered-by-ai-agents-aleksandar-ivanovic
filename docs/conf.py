"""Sphinx configuration file for Social Network Kata documentation."""

# -- Project information -----------------------------------------------------
project = "Social Network Kata"
copyright = "2026, Aleksandar Ivanovic"
author = "Aleksandar Ivanovic"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx_wagtail_theme",
    "myst_parser",
    "sphinx_new_tab_link",
]

new_tab_link_show_external_link_icon = True

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_wagtail_theme"

html_theme_options = {
    "project_name": "Social Network Kata",
    "github_url": (
        "https://github.com/Ivanovic0245/"
        "sdp-powered-by-ai-agents-aleksandar-ivanovic/blob/master/docs/"
    ),
    "footer_links": "",
}

html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"
html_show_sphinx = False

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]

# Don't fail the build on missing cross-references in markdown headings that
# contain emoji/check marks (used throughout arc42 + user-stories docs).
myst_heading_anchors = 3
suppress_warnings = ["myst.header"]
