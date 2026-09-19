from projectvars import ProjectVars
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# NOTE: every st.pyplot(fig) call below is followed by plt.close(fig).
# Streamlit reruns this whole script on every widget interaction, and
# without closing, matplotlib's global figure registry keeps growing for
# the entire session -- each rerun gets slower, and it can eventually
# stall or error out under the memory pressure (which looks like the page
# "not loading" / stuck showing the previous plot).

class Data_Insights:
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
                <h2 style="color:cyan; text-align:center;">📊 Dataset Insight</h2>
                <p style="color:cyan; font-size:16px;">
                    The Dataset Insight module helps you explore and understand the structure and quality of your dataset.
                    Each section provides a focused view:
                </p>
                <ul style="color:cyan; font-size:15px;">
                    <li><b>Dataset Preview</b> – View rows and columns interactively.</li>
                    <li><b>Summary Statistics</b> – Mean, median, min, max, and standard deviation.</li>
                    <li><b>Column Info</b> – Names, datatypes, and unique values.</li>
                    <li><b>Missing Value Check</b> – Identify nulls and NaNs.</li>
                    <li><b>Outlier Detection</b> – Spot unusual values using statistical methods.</li>
                    <li><b>Dataset Quality</b> – Evaluate completeness and consistency.</li>
                    <li><b>Data Distribution</b> – Visualize how values are spread.</li>
                    <li><b>Correlation</b> – Discover relationships between numeric features.</li>
                    <li><b>Dataset Balance Check</b> – Assess class distribution for supervised learning.</li>
                </ul>
                <p style="color:cyan; font-size:16px;">
                    🔍 Use these insights to decide preprocessing steps and guide visualization.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    def show_preview(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Dataset Preview</h2>", unsafe_allow_html=True)
            st.write("Total Columns in Dataset : ",self.df.shape[1])
            st.write("Total Rows in Dataset : ",self.df.shape[0])
            st.info("Please select the number of rows to be displayed")
            val = st.slider("Number of Rows",min_value=5,max_value=100,step=5)
            st.dataframe(self.df.head(val))
        else:
            st.warning("No file uploaded yet.")

    def summary_statistics(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Summary Statistics</h2>", unsafe_allow_html=True)
            st.dataframe(self.df.describe())
        else:
            st.warning("No file uploaded yet.")
    
    def column_info(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Column Info</h2>", unsafe_allow_html=True)
            # Create dtype table
            dtype_df = pd.DataFrame({
                "Column Name": self.df.columns,
                "Data Type": [str(dtype) for dtype in self.df.dtypes]
            })
            # Render styled table with centered container
            table_html = dtype_df.to_html(index=False, justify="left")
            styled_html = f"""
            <div style='display:flex; justify-content:center;'>
                <div style='font-family:Consolas, monospace; color:#fff;
                            background-color:rgba(0,0,0,0.6); padding:10px 20px; border-radius:8px;
                            box-shadow:0 0 10px rgba(0,0,0,0.4);'>
                    {table_html}
                </div>
            </div>
            """
            st.markdown(styled_html, unsafe_allow_html=True)
        else:
            st.warning("No file uploaded yet.")
    
    def missing_value_check(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Missing Value Check</h2>", unsafe_allow_html=True)
            if self.df.shape[0] == 0:
                st.warning("The dataset has no rows to check.")
                return
            st.write("Total Missing Values : ",self.df.isnull().sum().sum())
            missing_values = pd.DataFrame({
                "Column Name": [col for col in self.df.columns],
                "Number of Missing Values":[self.df[col].isnull().sum() for col in self.df.columns],
                "Null %":[str((self.df[col].isnull().sum())/(self.df.shape[0])*100)+" %" for col in self.df.columns],
            })
            st.dataframe(missing_values)
        else:
            st.warning("No file uploaded yet.")

    def outlier_detection(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Outlier Detection</h2>", unsafe_allow_html=True)
            st.info("This can be only applied on Numerical Columns.")
            options = [col for col in self.df.columns if self.df[col].dtype in ["float64","int64"]]
            if options != []:
                options.insert(0,"select a column")
                selected = st.selectbox("Choose a Column",options)
                colors = ["select a color","blue", "cyan", "red", "green", "orange", "purple", "pink", "grey"]
                chosen = st.selectbox("Choose a palette color:", colors)          
                if chosen == "select a color" or selected == "select a column":
                    pass
                else:
                    st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Box Plot for Visualization</h3>", unsafe_allow_html=True)
                    fig,axes = plt.subplots()
                    sns.boxplot(data=self.df,x=selected,ax=axes,color=chosen)
                    st.pyplot(fig)
                    plt.close(fig)

                    # Outlier Logic
                    Q1 = self.df[selected].quantile(0.25)
                    Q3 = self.df[selected].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outlier = self.df[(self.df[selected] > upper_bound) | (self.df[selected] < lower_bound)]
                    st.write(f"Total Number of Outliers in {selected} : ",len(outlier))
                    percent = (len(outlier)/self.df.shape[0])*100
                    st.write(f"Outlier % in {selected} : ",str(percent)+" %")
            else:
                st.info("There are no numerical columns in the dataset.")
        else:
            st.warning("No file uploaded yet.")

    def dataset_quality(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Dataset Quality</h2>", unsafe_allow_html=True)
            color_map = plt.colormaps()
            color_map.insert(0,"Choose a colormap")
            cmap = st.selectbox("Color Picking for Missing Values Heatmap",color_map)
            if cmap == "Choose a colormap":
                pass
            else:
                st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>HeatMap of Missing Values (Noise)</h3>", unsafe_allow_html=True)
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.heatmap(self.df.isnull(), cbar=False, cmap=cmap, ax=ax)
                st.pyplot(fig)
                plt.close(fig)
                st.info("The HeatMap shows missing values as colored blocks. Rows/columns with more missing values appear noisier.")
        else:
            st.warning("No file uploaded yet.")
    
    def data_distribution(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Data Distribution</h2>", unsafe_allow_html=True)
            st.info("This can be applied only on Numeric Columns.")
            numeric_cols = [col for col in self.df.columns if self.df[col].dtype in ["float64","int64"]]
            if numeric_cols != []:
                colors = ["select a color", "blue", "cyan", "red", "green", "orange", "purple", "pink", "black", "yellow", "gray"]
                chosen = st.selectbox("Choose a color", colors)
                if chosen == "select a color":
                    pass
                else:
                    st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Displots of all Numerical Columns</h3>", unsafe_allow_html=True)
                    for col in numeric_cols:
                        st.markdown(f"<h3 style='color: cyan; text-align: center;'>Distribution of {col}</h3>", unsafe_allow_html=True)
                        # displot returns a FacetGrid, so use .fig
                        g = sns.displot(self.df[col], kde=True, bins=20, color=chosen)
                        st.pyplot(g.figure)
                        # Closed inside the loop, not just once at the end --
                        # this loop creates one figure per numeric column on
                        # every rerun, so leaving them open even briefly adds
                        # up fast on wide datasets.
                        plt.close(g.figure)
            else:
                st.info("There are no numerical columns in the dataset.")
        else:
            st.warning("No file uploaded yet.")

    def correlation(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Correlation</h2>", unsafe_allow_html=True)
            st.info("This can be applied only on Numeric Columns.")
            color_map = plt.colormaps()
            color_map.insert(0,"Choose a colormap")
            numeric_cols = [col for col in self.df.columns if self.df[col].dtype in ["float64","int64"]]
            if numeric_cols != []:
                cmap = st.selectbox("Color Picking for Missing Values Heatmap",color_map)
                if cmap == "Choose a colormap":
                    pass
                else:
                    st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Correlation HeatMap</h3>", unsafe_allow_html=True)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.heatmap(self.df.select_dtypes(include=["float64","int64"]).corr(), annot=True, cmap=cmap, ax=ax)
                    st.pyplot(fig)
                    plt.close(fig)
                    st.info("The HeatMap helps detect redundant or noisy features (e.g., columns too highly correlated or irrelevant).")
            else:
                st.info("There are no numeric columns in the dataset.")
        else:
            st.warning("No file uploaded yet.")

    def dataset_balance_check(self):
        if self.df is not None:
            st.markdown("<h2 style='color: cyan; font-size: 50px; font-weight: 900; text-align: center;'>Data Balance</h2>", unsafe_allow_html=True)
            st.info("This is only for Categorical Columns.")
            st.info("Use only if a column is a categorical column or can be classified into a fixed number of categories.")
            colors = ["select a color", "blue", "cyan", "red", "green", "orange", "purple", "pink", "black", "yellow", "gray"]
            chosen = st.selectbox("Choose a color", colors)
            categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
            categorical_cols.insert(0,"select a column")
            selected = st.selectbox("Select Column",categorical_cols)
            if chosen == "select a color" or selected == "select a column":
                pass
            else:
                # Count values
                counts = self.df[selected].value_counts()

                st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Count Plot of Column Categories</h3>", unsafe_allow_html=True)
                # 🔹 Countplot
                fig1, ax1 = plt.subplots()
                sns.countplot(x=selected, data=self.df, color=chosen, ax=ax1)
                ax1.set_title("Class Distribution (Countplot)")
                st.pyplot(fig1)
                plt.close(fig1)

                st.markdown("<h3 style='color: cyan; font-size: 40px; font-weight: 900; text-align: center;'>Pie Chart of Column Categories</h3>", unsafe_allow_html=True)
                # 🔹 Pie Chart
                fig2, ax2 = plt.subplots()
                ax2.pie(counts, labels=counts.index, autopct="%1.1f%%", colors=sns.color_palette("Set2"))
                ax2.set_title("Class Distribution (Pie Chart)")
                st.pyplot(fig2)
                plt.close(fig2)
        else:
            st.warning("No file uploaded yet.")