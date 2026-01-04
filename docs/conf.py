import os
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

current_path = Path(__file__).parent.parent.resolve()
sys.path.append(str(current_path))

project = "litestar-email"
version = metadata.version("litestar-email")
copyright = "2025, Litestar-Org"  # noqa: A001
author = "Litestar-Org"
release = os.getenv("_LITESTAR_EMAIL_DOCS_BUILD_VERSION", version.rsplit(".")[0])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "litestar": ("https://docs.litestar.dev/latest/", None),
}

napoleon_google_docstring = True
autoclass_content = "class"
autodoc_default_options = {
    "special-members": "__init__",
    "show-inheritance": True,
    "members": True,
}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
autosectionlabel_prefix_document = True
# Suppress warnings from duplicate object descriptions (caused by Napoleon extracting
# Attributes sections while autodoc also documents dataclass fields)
suppress_warnings = [
    "app.add_node",
    "ref.python",
    "autodoc",
    "duplicate",  # Generic duplicate warnings
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "litestar_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["style.css"]
html_title = "Litestar Email"
html_favicon = "_static/favicon.ico"
html_context = {
    "source_type": "github",
    "source_user": "litestar-org",
    "source_repo": "litestar-email",
}

html_theme_options: dict[str, Any] = {
    "logo_target": "/",
    "github_repo_name": "litestar-email",
    "github_url": "https://github.com/litestar-org/litestar-email",
    "navigation_with_keys": True,
}
