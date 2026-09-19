import base64
import os
import streamlit as st
from streamlit_option_menu import option_menu


class Layout:
    def __init__(self):
        self.title = "AnalyticaHub"
        self.sidebar_title = "Data Analytics ToolBar"
        # Resolve the image relative to this file, not the process's current
        # working directory -- a relative path like "bg_image.png" breaks as
        # soon as the app is launched from a different working directory
        # (very common on deployment platforms).
        self.background_image = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "bg_image.png"
        )
        self.uploaded_file = None
        self.selected_main = None
        self._encoded_bg = self._load_background()

    def _load_background(self):
        """Read + base64-encode the background image once. Returns None
        (instead of crashing the whole app) if the image is missing."""
        try:
            with open(self.background_image, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except (FileNotFoundError, OSError):
            st.warning("⚠️ Background image not found. Continuing without it.")
            return None

    def set_background(self):
        if not self._encoded_bg:
            return
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{self._encoded_bg}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                height : 100vh;
                width : 100vw;
                margin: 0;
                padding: 0;
                overflow-y : auto;     /* enable vertical scrolling */
                overflow-x : hidden;   /* hide horizontal overflow */
            }}

            /* Hide Streamlit's default top padding */
            [data-testid="stHeader"] {{
                background: transparent;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    def sidebar_options(self):
        st.sidebar.title(self.sidebar_title)

        sidebar_bg_rule = (
            f'background-image : url("data:image/png;base64,{self._encoded_bg}");'
            if self._encoded_bg else ""
        )
        st.markdown(
            f"""
            <style>
            /* Sidebar Container */
            [data-testid="stSidebar"] {{
                {sidebar_bg_rule}
            }}
            /* Sidebar heading styling */
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2 {{
                font-size: 40px;       /* bigger font */
                font-weight: 800;      /* bold */
                color: #00ffff;        /* cyan glow effect */
                text-align: center;    /* center align */
                margin-top: -45px;     /* shift upwards */
                overflow-y : auto;     /* enable vertical scrolling */
                overflow-x : hidden;   /* hide horizontal overflow */
            }}
            </style>
            """, unsafe_allow_html=True
        )
        with st.sidebar:
            self.selected_main = option_menu(
                menu_title="Tool Type",
                options=["Home", "Dataset Insight", "Data Preprocessing", "Data Visualization"],
                key="main_tool_menu",  # explicit unique key avoids duplicate-widget-id issues
                styles={
                    "container": {
                        "padding": "5px",
                        "background-color": "black",
                        "font-color": "cyan",     # heading font color
                        "font-weight": "bold",    # heading bold
                        "font-size": "10px",      # heading size
                    },
                    "icon": {"color": "cyan", "font-size": "20px"},                  # icon color
                    "nav-link": {
                        "font-size": "15px",
                        "text-align": "left",
                        "margin": "5px",
                        "color": "cyan",                                            # default font color
                        "background-color": "transparent",
                    },
                    "nav-link-selected": {
                        "background-color": "#1E90FF",                              # blue background when clicked
                        "color": "white",                                           # white font when clicked
                    },
                },
            )

    def main_area(self):
        st.markdown(f"<h1 style='color: cyan; font-size: 90px; font-weight: 900; text-align: center;margin-top: -130px'>{self.title}</h1>", unsafe_allow_html=True)
        self.uploaded_file = st.file_uploader(
            "Upload Dataset to be Analyzed", type=["csv"], key="dataset_uploader"
        )
