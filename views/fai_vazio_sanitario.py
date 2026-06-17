from __future__ import annotations

import runpy
import os
from pathlib import Path

import streamlit as st


def render_fai_vazio_sanitario() -> None:
    current_set_page_config = st.set_page_config
    current_cwd = Path.cwd()

    def noop_set_page_config(*args, **kwargs) -> None:
        return None

    app_path = Path(__file__).resolve().parents[2] / "fai vegetal" / "app.py"
    if not app_path.exists():
        st.error(f"Nao encontrei o app FAI em: {app_path}")
        return

    st.set_page_config = noop_set_page_config
    try:
        os.chdir(app_path.parent)
        runpy.run_path(str(app_path), run_name="__fai_vazio_sanitario__")
    finally:
        os.chdir(current_cwd)
        st.set_page_config = current_set_page_config
