from layout import Layout
import streamlit as st
from streamlit_option_menu import option_menu

class SidebarMainButtons:
    def __init__(self,layout:Layout):
        self.layout = layout
        self.selected_dataset_insight = None
        self.selected_data_preprocessing = None
        self.selected_data_visualization = None
    
    def render(self):
        if self.layout.selected_main == "Home":
            st.markdown(
                """
                <div style="background-color:black; padding:20px; border-radius:10px;">
                    <h1 style="color:cyan; text-align:center;">🏠 Welcome to the Data Analytics Workspace</h1>
                    <p style="color:cyan; font-size:16px;">
                        This platform is your one-stop environment for exploring, cleaning, and visualizing datasets. 
                        Each section in the sidebar is designed to guide you through the full analytics pipeline:
                    </p>
                    <ul style="color:cyan; font-size:15px;">
                        <li><b>Home</b> – Quick introduction to the workspace and navigation.</li>
                        <li><b>Dataset Insight</b> – Explore dataset details: description, preview, summary statistics, 
                            column info, missing values, outliers, quality checks, distributions, correlations, and balance.</li>
                        <li><b>Data Preprocessing</b> – Prepare your data: rename/remove columns, manage datatypes, 
                            impute missing values, remove outliers/duplicates, and apply feature scaling.</li>
                        <li><b>Data Visualization</b> – Transform data into visuals: line, scatter, bar, pie, histogram, 
                            heatmap, KDE, pair, box, and violin plots.</li>
                    </ul>
                    <p style="color:cyan; font-size:16px;">
                        ✨ Upload your dataset, explore its structure, preprocess it for accuracy, and visualize it to uncover meaningful patterns.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        if self.layout.selected_main == "Dataset Insight":
            with st.sidebar:
                self.selected_dataset_insight = option_menu(
                    menu_title = "Dataset Insight",
                    options = ["Description","Dataset Preview","Summary Statistics","Column Info","Missing Value Check","Outlier Detection","Dataset Quality","Data Distribution","Correlation","Dataset Balance Check"],
                    key="dataset_insight_menu",
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
        if self.layout.selected_main == "Data Preprocessing":
            with st.sidebar: 
                self.selected_data_preprocessing = option_menu(
                    menu_title = "Data Preprocessing",
                    options = ["Description","Column Name Change","Column Removal","DataType Management","Statistical Value Imputation","Custom Value Imputation","Other Imputation","Outlier Removal","Duplicate Value Removal","Feature Scaling"],
                    key="data_preprocessing_menu",
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
        if self.layout.selected_main == "Data Visualization":
            with st.sidebar:
                self.selected_data_visualization = option_menu(
                    menu_title = "Data Visualization",
                    options = ["Description","Line Plot","Scatter Plot","Bar Plot","Pie Plot","Histogram","HeatMap","KDE Plot","Pair Plot","Box Plot","Violin Plot"],
                    key="data_visualization_menu",
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