## Project structure

```
app.py                          # entry point
layout.py                       # page/background/sidebar shell
projectvars.py                  # CSV upload -> session-state dataframe
sidebarmainbuttons.py           # top-level + sub-menu navigation
data_insights.py / _buttons.py  # "Dataset Insight" tab
data_preprocessing.py / _buttons.py  # "Data Preprocessing" tab
data_visualization.py / _buttons.py  # "Data Visualization" tab
bg_image.png                    # background art
requirements.txt
.streamlit/config.toml
```