from sidebarmainbuttons import SidebarMainButtons
from data_insights import Data_Insights

class Data_Insight_Buttons:
    def __init__(self,button:SidebarMainButtons,data:Data_Insights):
        self.button = button
        self.data = data
    
    def render(self):
        if self.button.selected_dataset_insight == "Description":
            self.data.description()
        if self.button.selected_dataset_insight == "Dataset Preview":
            self.data.show_preview()
        if self.button.selected_dataset_insight == "Summary Statistics":
            self.data.summary_statistics()
        if self.button.selected_dataset_insight == "Column Info":
            self.data.column_info()
        if self.button.selected_dataset_insight == "Missing Value Check":
            self.data.missing_value_check()
        if self.button.selected_dataset_insight == "Outlier Detection":
            self.data.outlier_detection()
        if self.button.selected_dataset_insight == "Dataset Quality":
            self.data.dataset_quality()
        if self.button.selected_dataset_insight == "Data Distribution":
            self.data.data_distribution()
        if self.button.selected_dataset_insight == "Correlation":
            self.data.correlation()
        if self.button.selected_dataset_insight == "Dataset Balance Check":
            self.data.dataset_balance_check()