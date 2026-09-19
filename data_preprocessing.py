from projectvars import ProjectVars
from data_insights import Data_Insights
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer,IterativeImputer
from sklearn.preprocessing import StandardScaler,MinMaxScaler,Normalizer,RobustScaler,MaxAbsScaler
import streamlit as st
import pandas as pd
import seaborn as sns

class Data_Preprocessing:
    def __init__(self,project:ProjectVars):
        self.project = project
        # ✅ Always sync with session_state
        if "df" in st.session_state:
            self.df = st.session_state.df
        else:
            self.df = self.project.df
            if self.df is not None:
                st.session_state.df = self.df

    def description(self):
        st.markdown(
            """
            <div style="background-color:black; padding:20px; border-radius:10px;">
                <h2 style="color:cyan; text-align:center;">⚙️ Data Preprocessing</h2>
                <p style="color:cyan; font-size:16px;">
                    The Data Preprocessing module prepares your dataset for accurate analysis and modeling.
                    Each tool focuses on cleaning and transforming data:
                </p>
                <ul style="color:cyan; font-size:15px;">
                    <li><b>Column Name Change</b> – Rename columns for clarity.</li>
                    <li><b>Column Removal</b> – Drop irrelevant or redundant columns.</li>
                    <li><b>DataType Management</b> – Adjust column datatypes.</li>
                    <li><b>Statistical Value Imputation</b> – Fill missing values with mean/median/mode.</li>
                    <li><b>Custom Value Imputation</b> – Replace missing values with user-defined inputs.</li>
                    <li><b>Other Imputation</b> – Advanced methods like forward/backward fill.</li>
                    <li><b>Outlier Removal</b> – Eliminate extreme values.</li>
                    <li><b>Duplicate Value Removal</b> – Remove repeated rows.</li>
                    <li><b>Feature Scaling</b> – Normalize or standardize features.</li>
                </ul>
                <p style="color:cyan; font-size:16px;">
                    ⚡ These steps ensure your dataset is clean, consistent, and ready for visualization or modeling.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    def column_name_change(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Column Name Change</h2>", unsafe_allow_html=True)
            columns = self.df.columns.to_list()
            selected = st.multiselect("Please select column(s)", columns)
            rename_dict = {}   # ✅ dictionary mapping old → new

            if selected:
                for i in selected:
                    new_column_name = st.text_input(
                        f"Type the new name for column '{i}'",
                        key=f"rename_{i}"   # unique key per input
                    )
                    if new_column_name:   # only add if user typed something
                        rename_dict[i] = new_column_name

                st.write("Do you want to confirm the change? If yes, check the box below.")
                confirm = st.checkbox("Yes, I confirm the change")

                if confirm and rename_dict:   
                    # ✅ apply all mappings at once
                    self.df.rename(columns=rename_dict, inplace=True)
                    st.session_state.df = self.df   # persist change
                    st.success("Change Applied.")
            else:
                pass
        else:
            st.warning("No file uploaded yet.")

    def column_removal(self):
        if self.df is not None:
            st.markdown(
                "<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Column Removal</h2>",
                unsafe_allow_html=True
            )
            columns = self.df.columns.to_list()
            st.info("Select one or more columns to remove. Once confirmed, they will be deleted together.")
            st.info("Unchecking the checkbox after a complete deletion of column/columns will lead to reset of the dropdown menu with the remaining columns name.")

            # ✅ Allow multiple selections
            selected = st.multiselect("Please select column(s)", columns)

            if not selected:
                pass
            else:
                # ✅ Prevent deleting all columns
                if len(selected) == len(self.df.columns):
                    st.error("Cannot remove all columns. At least one column must remain.")
                else:
                    st.write("Do you want to confirm the change? If yes, check the checkbox to apply the change.")
                    confirm = st.checkbox("Yes I confirm the change to be applied", key="confirm_remove_multiple")
                    if confirm:
                        try:
                            self.df.drop(columns=selected, inplace=True)
                            st.session_state.df = self.df   # persist change
                            st.success(f"Columns {selected} removed successfully.")
                        except Exception as e:
                            st.error(f"❌ Error while removing columns {selected}: {e}")
        else:
            st.warning("No file uploaded yet.")
    
    def datatype_management(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>DataType Management</h2>", unsafe_allow_html=True)
            info = st.checkbox("Do you want to view Column Info here")
            d = Data_Insights(project=self.project)
            if info:
                d.column_info()
            columns = self.df.columns.to_list()
            selected_columns = st.multiselect("Select column/columns",options=columns)
            if selected_columns is not None:
                datatypes = ["select a dtype","int64","float64","object","bool","datetime64[ns]","category"]
                for i in selected_columns:
                    # ✅ unique key per column
                    select = st.selectbox(
                        f"Select new DataType for {i}",
                        datatypes,
                        key=f"select_dtype_{i}"
                    )
                    if select != "select a dtype":
                        try:
                            # Attempt conversion
                            self.df[i] = self.df[i].astype(select)
                            st.session_state.df = self.df  # persist change
                            st.success(f"{i} column's datatype changed to {select}")
                        except Exception as e:
                            # Handle invalid conversion gracefully
                            st.error(f"❌ Could not convert column '{i}' to {select}. Error: {e}")
                    else:
                        pass
                st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Updated DataTypes</h2>", unsafe_allow_html=True)
                st.info("All your Changes will be reflected here.")
                d.column_info()
            else:
                pass
        else:
            st.warning("No file uploaded yet.")

    def statistical_value_imputation(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Statistical Value Imputation</h2>", unsafe_allow_html=True)
            st.info("Here Missing Value Imputation takes place by replacing with statistical parameters. Here only columns with missing values will be listed.")
            
            columns = [col for col in self.df.columns if self.df[col].isnull().sum() > 0]
            selected_columns = st.multiselect("Select Column/Columns", options=columns)

            # Define valid methods per dtype
            numeric_methods = ["Mean", "Median", "Mode", "Forward Fill (ffill)", "Backward Fill (bfill)"]
            categorical_methods = ["Mode", "Forward Fill (ffill)", "Backward Fill (bfill)"]
            datetime_methods = ["Forward Fill (ffill)", "Backward Fill (bfill)"]
            timedelta_methods = ["Forward Fill (ffill)", "Backward Fill (bfill)"]

            # Dictionary to store chosen methods
            chosen_methods = {}

            if selected_columns:
                for i in selected_columns:
                    dtype = self.df[i].dtype
                    if pd.api.types.is_numeric_dtype(dtype):
                        valid_methods = numeric_methods
                    elif isinstance(dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
                        valid_methods = categorical_methods
                    elif pd.api.types.is_datetime64_any_dtype(dtype):
                        valid_methods = datetime_methods
                    elif pd.api.types.is_timedelta64_dtype(dtype):
                        valid_methods = timedelta_methods
                    else:
                        valid_methods = ["Forward Fill (ffill)", "Backward Fill (bfill)"]

                    methods_copy = valid_methods.copy()
                    methods_copy.insert(0, "select a method")
                    method = st.selectbox(f"Choose imputation method for {i} ({dtype})", methods_copy, key=f"select_column_{i}")
                    chosen_methods[i] = method

                # ✅ Apply all chosen methods together
                if st.button("Apply All Imputations"):
                    try:
                        for col, method in chosen_methods.items():
                            if method == "Mean":
                                self.df[col] = self.df[col].fillna(self.df[col].mean())
                            elif method == "Median":
                                self.df[col] = self.df[col].fillna(self.df[col].median())
                            elif method == "Mode":
                                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
                            elif method == "Forward Fill (ffill)":
                                self.df[col] = self.df[col].ffill()
                            elif method == "Backward Fill (bfill)":
                                self.df[col] = self.df[col].bfill()

                        st.session_state.df = self.df
                        st.success(f"Imputation applied on columns {list(chosen_methods.keys())}.")
                    except Exception as e:
                        st.error(f"❌ Error applying imputation: {e}")
        else:
            st.warning("No file uploaded yet.")
   
    def custom_value_imputation(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Custom Value Imputation</h2>", unsafe_allow_html=True)
            columns = [col for col in self.df.columns if self.df[col].isnull().sum() > 0]
            selected_columns = st.multiselect("Select Column/Columns", options=columns)

            # Dictionary to store user inputs
            custom_values = {}

            if selected_columns:
                for i in selected_columns:
                    dtype = self.df[i].dtype
                    val = None

                    if pd.api.types.is_numeric_dtype(dtype):
                        val = st.number_input(f"Enter numeric value for {i}", key=f"num_{i}")
                    elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
                        val = st.text_input(f"Enter text value for {i}", key=f"text_{i}")
                    elif pd.api.types.is_datetime64_any_dtype(dtype):
                        val = st.text_input(f"Enter datetime value (YYYY-MM-DD) for {i}", key=f"dt_{i}")
                        if val:
                            val = pd.to_datetime(val, errors="coerce")

                    custom_values[i] = val

                # ✅ Apply all imputations together
                if st.button("Apply All Custom Imputations"):
                    try:
                        for col, val in custom_values.items():
                            if val not in [None, ""]:
                                self.df[col] = self.df[col].fillna(value=val)
                        st.session_state.df = self.df
                        st.success(f"Custom imputation applied on columns {list(custom_values.keys())}.")
                    except Exception as e:
                        st.error(f"❌ Error applying imputation: {e}")
        else:
            st.warning("No file uploaded yet.")
    
    def other_imputation(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Other Imputation</h2>", unsafe_allow_html=True)
            st.info("These imputation methods apply only for numerical columns and apply over the entire dataset.")
            numeric_column = [col for col in self.df.columns if  self.df[col].dtype in ["int64","float64"] and self.df[col].isnull().sum()>0]
            numerical_data = self.df[numeric_column]
            numerical_data_options = numeric_column
            st.markdown("<h2 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Statistics Before Applying Imputation</h2>", unsafe_allow_html=True)
            st.dataframe(self.df.describe())
            if len(numeric_column) != 0:
                methods = st.selectbox("Please select one of the methods",options=["select a method","knn-imputer","iterative-imputer"])
                if methods == "select a method":
                    pass

                if methods == "knn-imputer":
                    neighbors = st.slider("Select no. of neighbours",min_value=5,max_value=50,key="neighbors")
                    if st.button("Confirm"):
                        knn_imp = KNNImputer(n_neighbors=neighbors)
                        numerical_data_knn = knn_imp.fit_transform(numerical_data)
                        self.df[numeric_column] = pd.DataFrame(numerical_data_knn, columns=numeric_column, index=self.df.index)
                        st.session_state.df = self.df
                        st.success("Applied Successfully")
                        st.markdown("<h2 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Statistics After Applying KNN Imputation</h2>", unsafe_allow_html=True)
                        st.dataframe(self.df.describe())

                if methods == "iterative-imputer":
                    max_iter = st.slider("Select no. of iterations",min_value=5,max_value=50,key="iter")
                    if st.button("Confirm"):
                        iter_imp = IterativeImputer(max_iter=max_iter,random_state=42)
                        numerical_data_iter = iter_imp.fit_transform(numerical_data)
                        self.df[numeric_column] = pd.DataFrame(numerical_data_iter, columns=numeric_column, index=self.df.index)
                        st.session_state.df = self.df
                        st.success("Applied Successfully")
                        st.markdown("<h2 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Statistics After Applying Iterative Imputation</h2>", unsafe_allow_html=True)
                        st.dataframe(self.df.describe())
            else:
                st.info("No numeric columns with missing values found.")
        else:
            st.warning("No file uploaded yet.")
    
    def outlier_removal(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Outlier Removal</h2>", unsafe_allow_html=True)
            st.info("Here fence value extensions are 1.5 for both upper and lower fence (as standard)")
            numeric_columns = [col for col in self.df.columns if self.df[col].dtype in ["int64","float64"]]
            selected_column = st.multiselect("Select a Column",options=numeric_columns)
            if selected_column:
                outlier_index = set()
                for col in selected_column:
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR  
                    outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)] 
                    outlier_index.update(outliers.index) 
                st.write("Total Distinct Rows that will be removed after the Outlier Removal Operation : ",len(outlier_index))
                st.write("% Removal of Data : ",str((len(outlier_index)/self.df.shape[0])*100)+" %")
                st.info("If you want to proceed then click on proceed")  
                proceed = st.button("Proceed")
                if proceed:
                    self.df = self.df.drop(index=outlier_index)
                    st.session_state.df = self.df
                    st.success("Successful")
                else:
                    pass
        else:
            st.warning("No file uploaded yet.")

    def duplicate_value_removal(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Dupliacte Value Removal</h2>", unsafe_allow_html=True)
            before = self.df.shape[0]
            df = self.df.drop_duplicates()
            after = df.shape[0]
            st.write("Before Removal Rows : ",before)
            st.write("After Removal Rows : ",after)
            st.write("% Removal of Rows : ",str(((before-after)/before)*100)+" %")
            if st.button("Confirm"):
                self.df = self.df.drop_duplicates()
                st.session_state.df = self.df
                st.success(f"Removed {before - after} duplicate row(s).")
            else:
                pass
        else:
            st.warning("No file uploaded yet.")

    def feature_scaling(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Feature Scaling</h2>", unsafe_allow_html=True)
            st.info("These feature scaling methods apply only for numerical columns and apply over the entire dataset.")
            
            st.markdown("<h2 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Statistics Before Feature Scaling</h2>", unsafe_allow_html=True)
            st.dataframe(self.df.describe())
            
            numeric_columns = [col for col in self.df.columns if self.df[col].dtype in ["int64","float64"]]
            numeric_data = self.df[numeric_columns]
            
            if numeric_columns:
                select = st.selectbox("Select the scaling method", options=["select a method","standard","min-max","robust","normalizer","max-abs"])
                
                if select == "standard":
                    scaler = StandardScaler()
                    label = "Standard Scaler"
                elif select == "min-max":
                    scaler = MinMaxScaler(feature_range=(0, 1))
                    label = "MinMax Scaler"
                elif select == "robust":
                    scaler = RobustScaler()
                    label = "Robust Scaler"
                elif select == "normalizer":
                    scaler = Normalizer()
                    label = "Normalizer (row-wise)"
                elif select == "max-abs":
                    scaler = MaxAbsScaler()
                    label = "MaxAbs Scaler"
                else:
                    scaler = None
                
                if scaler:
                    numeric_data_scaled = scaler.fit_transform(numeric_data)
                    self.df[numeric_columns] = pd.DataFrame(numeric_data_scaled, columns=numeric_columns, index=self.df.index)
                    st.session_state.df = self.df
                    st.success("Applied Successfully")
                    st.markdown(f"<h2 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Statistics After Applying {label}</h2>", unsafe_allow_html=True)
                    st.dataframe(self.df.describe())
            else:
                st.info("No Numerical Column")
        else:
            st.warning("No file uploaded yet.")

    def download_dataset(self):
        """Lets the user download the dataset in its current state --
        i.e. after whichever cleaning/imputation/scaling steps they've
        applied so far this session. Shown under every preprocessing
        sub-page (see Data_Preprocessing_Buttons.render)."""
        if self.df is not None:
            st.markdown("---")
            st.markdown(
                "<h3 style='color: cyan; font-size: 30px; font-weight: 900; text-align: center;'>Download Processed Dataset</h3>",
                unsafe_allow_html=True
            )
            st.caption(f"Current shape: {self.df.shape[0]} rows x {self.df.shape[1]} columns.")
            csv_bytes = self.df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Dataset as CSV",
                data=csv_bytes,
                file_name="processed_dataset.csv",
                mime="text/csv",
                key="dl_processed_csv",
            )
