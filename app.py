# IMPORTANT: matplotlib's backend must be set before anything else imports
# pyplot (data_insights / data_preprocessing / data_visualization all do).
# Without this, deployment on a headless server (Streamlit Cloud, Docker,
# most CI/CD hosts) can crash with "no display name" errors.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st

# Streamlit re-executes this entire script on every widget interaction
# (switching plot type, moving a slider, etc.). None of the plotting
# modules ever call plt.close() on the figures they create, so without
# this, matplotlib's global figure registry grows without bound for the
# whole session -- every rerun gets a little slower, and eventually a
# rerun can stall/error out under the memory pressure, which looks like
# the page "not loading" and being stuck on the previous plot. Clearing
# out any figures left over from the previous run, right at the start of
# this one, keeps the registry bounded to at most one run's worth.
plt.close("all")

# st.set_page_config must be the first Streamlit command executed.
st.set_page_config(
    page_title="AnalyticaHub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from layout import Layout
from projectvars import ProjectVars
from data_insights import Data_Insights
from data_preprocessing import Data_Preprocessing
from sidebarmainbuttons import SidebarMainButtons
from data_insight_buttons import Data_Insight_Buttons
from data_preprocessing_buttons import Data_Preprocessing_Buttons
from data_visualization import Data_Visualization
from data_visualization_buttons import Data_Visualization_Buttons

layout = Layout()
layout.set_background()
layout.sidebar_options()
layout.main_area()

sidebar_main_buttons = SidebarMainButtons(layout=layout)
sidebar_main_buttons.render()

project = ProjectVars(layout=layout)
data_insight_functions = Data_Insights(project=project)
data_insight_buttons = Data_Insight_Buttons(button=sidebar_main_buttons, data=data_insight_functions)
data_insight_buttons.render()
data_preprocessing_functions = Data_Preprocessing(project=project)
data_preprocessing_buttons = Data_Preprocessing_Buttons(button=sidebar_main_buttons, data=data_preprocessing_functions)
data_preprocessing_buttons.render()
data_visualization_functions = Data_Visualization(project=project)
data_visualization_buttons = Data_Visualization_Buttons(button=sidebar_main_buttons, data=data_visualization_functions)
data_visualization_buttons.render()
