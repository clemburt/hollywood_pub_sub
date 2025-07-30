# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# Add the src directory to sys.path so autodoc can find your modules
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'hollywood_pub_sub'
copyright = '2025, Clement Burtscher'
author = 'Clement Burtscher'
release = '0.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',            # Enables automatic doc generation from docstrings
    'sphinx.ext.napoleon',           # Supports NumPy and Google style docstrings
    'sphinx_autodoc_typehints',      # Shows type hints in function/method signatures
]

# Include both class and __init__ docstrings
autoclass_content = 'both'

# Settings for autodoc
autodoc_default_options = {
    'members': True,                # Include documented members
    'undoc-members': True,          # Include members without docstrings
    'private-members': False,       # Don't include _private members
    'special-members': '__init__',  # Include __init__ method
    'inherited-members': True,      # Include members from base classes
    'show-inheritance': True,       # Show class inheritance info
}

# -- Paths for templates and static files (optional) -------------------------
templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Settings for Napoleon to support NumPy docstrings
napoleon_numpy_docstring = True
napoleon_google_docstring = False  # You can enable this if needed
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# -- Pydantic-specific settings ----------------------------------------------
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_field_show_constraints = False
autodoc_pydantic_model_signature_prefix = "class"
autodoc_pydantic_field_show_required = True
autodoc_pydantic_model_member_order = "bysource"
