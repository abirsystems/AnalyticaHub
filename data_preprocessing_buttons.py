from sidebarmainbuttons import SidebarMainButtons
from data_preprocessing import Data_Preprocessing

class Data_Preprocessing_Buttons:
    def __init__(self,button:SidebarMainButtons,data:Data_Preprocessing):
        self.button = button
        self.data = data
    
    def render(self):
        if self.button.selected_data_preprocessing == "Description":
            self.data.description()
        if self.button.selected_data_preprocessing == "Column Name Change":
            self.data.column_name_change()
        if self.button.selected_data_preprocessing == "Column Removal":
            self.data.column_removal()
        if self.button.selected_data_preprocessing == "DataType Management":
            self.data.datatype_management()
        if self.button.selected_data_preprocessing == "Statistical Value Imputation":
            self.data.statistical_value_imputation()
        if self.button.selected_data_preprocessing == "Custom Value Imputation":
            self.data.custom_value_imputation()
        if self.button.selected_data_preprocessing == "Other Imputation":
            self.data.other_imputation()
        if self.button.selected_data_preprocessing == "Outlier Removal":
            self.data.outlier_removal()
        if self.button.selected_data_preprocessing == "Duplicate Value Removal":
            self.data.duplicate_value_removal()
        if self.button.selected_data_preprocessing == "Feature Scaling":
            self.data.feature_scaling()

        # Always available once a dataset is loaded, regardless of which
        # sub-page is open, so the user can grab the dataset at any point.
        self.data.download_dataset()
