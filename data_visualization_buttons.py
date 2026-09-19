from sidebarmainbuttons import SidebarMainButtons
from data_visualization import Data_Visualization

class Data_Visualization_Buttons:
    def __init__(self,button:SidebarMainButtons,data:Data_Visualization):
        self.button = button
        self.data = data

    def render(self):
        if self.button.selected_data_visualization == "Description":
            self.data.description()
        if self.button.selected_data_visualization == "Line Plot":
            self.data.line_plot()
        if self.button.selected_data_visualization == "Scatter Plot":
            self.data.scatter_plot()
        if self.button.selected_data_visualization == "Bar Plot":
            self.data.bar_plot()
        if self.button.selected_data_visualization == "Pie Plot":
            self.data.pie_plot()
        if self.button.selected_data_visualization == "Histogram":
            self.data.histogram_plot()
        if self.button.selected_data_visualization == "HeatMap":
            self.data.heatmap_plot()
        if self.button.selected_data_visualization == "KDE Plot":
            self.data.kde_plot()
        if self.button.selected_data_visualization == "Pair Plot":
            self.data.pairplot_plot()
        if self.button.selected_data_visualization == "Box Plot":
            self.data.boxplot_plot()
        if self.button.selected_data_visualization == "Violin Plot":
            self.data.violin_plot()
