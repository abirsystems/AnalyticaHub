from projectvars import ProjectVars
import streamlit as st
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from functools import wraps
import io


def requires_data(func):
    """Skip the plot body and show a warning when no dataframe is loaded.
    Replaces the `if self.df is not None: ... else: st.warning(...)` block
    that was copy-pasted into every plotting method.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.df is None:
            st.warning("No file uploaded yet.")
            return None
        return func(self, *args, **kwargs)
    return wrapper


class Data_Visualization:
    def __init__(self, project: ProjectVars):
        self.project = project
        # Always sync with session_state
        if "df" in st.session_state:
            self.df = st.session_state.df
        else:
            self.df = self.project.df
            if self.df is not None:
                st.session_state.df = self.df

    # ------------------------------------------------------------------
    # Cached, expensive-to-recompute resources
    # ------------------------------------------------------------------
    @staticmethod
    def _get_colormaps():
        """plt.colormaps() rebuilds the full registry list on every call.
        Every plot method called it at least once (some twice) on every
        Streamlit rerun. Compute it once per session and reuse it.
        """
        if "_dv_colormaps" not in st.session_state:
            st.session_state._dv_colormaps = plt.colormaps()
        return st.session_state._dv_colormaps

    @staticmethod
    def _get_css4_colors():
        """Same idea for the CSS4 color name list."""
        if "_dv_css4_colors" not in st.session_state:
            st.session_state._dv_css4_colors = list(matplotlib.colors.CSS4_COLORS.keys())
        return st.session_state._dv_css4_colors

    # ------------------------------------------------------------------
    # Shared UI building blocks (pure helpers, no caching needed)
    # ------------------------------------------------------------------
    @staticmethod
    def _section_title(text, size=50):
        st.markdown(
            f"<h2 style='color: cyan; font-size: {size}px; font-weight: 900; "
            f"text-align: center;'>{text}</h2>",
            unsafe_allow_html=True
        )

    def _numeric_cols(self):
        return list(self.df.select_dtypes(include="number").columns)

    def _object_cols(self):
        return list(self.df.select_dtypes(include="object").columns)

    def _col_options(self, dtype=None, placeholder="Select a column"):
        """Column list (optionally filtered by dtype) with a placeholder prepended."""
        cols = list(self.df.select_dtypes(include=dtype).columns) if dtype else list(self.df.columns)
        return [placeholder] + cols

    def _group_col_selectbox(self, label="Optional grouping column", index=0, key=None):
        return st.selectbox(label, [None] + self._object_cols(), index=index, key=key)

    @staticmethod
    def _size_inputs(w_default=12, h_default=7, w_range=(10, 50), h_range=(7, 50), key_prefix=None):
        width = st.number_input(
            "Enter width of plot", min_value=w_range[0], max_value=w_range[1], value=w_default,
            key=f"{key_prefix}_width" if key_prefix else None
        )
        height = st.number_input(
            "Enter height of plot", min_value=h_range[0], max_value=h_range[1], value=h_default,
            key=f"{key_prefix}_height" if key_prefix else None
        )
        return width, height

    def _colormap_selectbox(self, label="Select colormap", index=0, placeholder="Select a colormap", key=None):
        """Colormap picker that defaults to a placeholder instead of
        silently pre-selecting a real colormap (it used to default to
        whatever _get_colormaps() returns first, e.g. "magma"). Returns
        None while the placeholder is showing; matplotlib/seaborn treat a
        None cmap/palette as "use my own default", so callers can pass the
        result straight through.
        """
        selected = st.selectbox(label, [placeholder] + self._get_colormaps(), index=index, key=key)
        return None if selected == placeholder else selected

    def _color_or_palette(self, group_col, index=0, color_placeholder="Select a color", key_prefix=None):
        """Returns (color, color_pall). Exactly one is populated, depending on
        whether a grouping column is selected. Replaces the block that was
        repeated in line_plot, scatter_plot, bar_plot, boxplot_plot,
        violin_plot and kde_plot.

        The plain-color picker defaults to a placeholder rather than a real
        color (it used to silently pre-select "aliceblue"). While the
        placeholder is showing, color is None, so callers just pass it
        straight to matplotlib/seaborn, which falls back to its own default.
        """
        if group_col is not None:
            return None, self._colormap_selectbox(
                index=index, key=f"{key_prefix}_colormap" if key_prefix else None
            )
        selected = st.selectbox(
            "Select color", [color_placeholder] + self._get_css4_colors(), index=index,
            key=f"{key_prefix}_color" if key_prefix else None
        )
        return (None if selected == color_placeholder else selected), None

    # ------------------------------------------------------------------
    # Plot download helper
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_figure(fig_or_grid):
        """pairplot/clustermap/displot return a Grid (PairGrid/ClusterGrid/
        FacetGrid), not a plain Figure. Grids expose the underlying Figure
        via .figure; plain Figures don't have that indirection. Resolving
        here means callers (and plt.close) always get a real Figure."""
        return getattr(fig_or_grid, "figure", fig_or_grid)

    @staticmethod
    def _fig_to_png_bytes(fig, dpi=150):
        """Render any matplotlib Figure (or seaborn Grid, which exposes the
        same .savefig interface) to PNG bytes."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        return buf.getvalue()

    def _offer_plot_download(self, fig, title):
        """Show a 'download this plot' button right under the chart, then
        close the figure. Every plotting method routes its figure through
        here right after st.pyplot(), so this is also the one place that
        needs to release it -- st.pyplot() keeps its own copy for
        rendering, but the Figure object itself is never freed from
        matplotlib's global registry unless something calls plt.close()."""
        real_fig = self._resolve_figure(fig)
        png_bytes = self._fig_to_png_bytes(real_fig)
        safe_name = title.lower().replace(" ", "_")

        st.download_button(
            "⬇️ Download this plot (PNG)",
            data=png_bytes,
            file_name=f"{safe_name}.png",
            mime="image/png",
            key=f"dl_png_{safe_name}",
        )
        plt.close(real_fig)

    def description(self):
        st.markdown(
            """
            <div style="background-color:black; padding:20px; border-radius:10px;">
                <h2 style="color:cyan; text-align:center;">🎨 Data Visualization</h2>
                <p style="color:cyan; font-size:16px;">
                    The Data Visualization module transforms your dataset into meaningful charts and plots.
                    Each option provides a different perspective:
                </p>
                <ul style="color:cyan; font-size:15px;">
                    <li><b>Line Plot</b> – Show trends over time.</li>
                    <li><b>Scatter Plot</b> – Explore relationships between variables.</li>
                    <li><b>Bar Plot</b> – Compare categorical values.</li>
                    <li><b>Pie Plot</b> – Display proportions of categories.</li>
                    <li><b>Histogram</b> – Visualize frequency distributions.</li>
                    <li><b>HeatMap</b> – Show correlations or intensity patterns.</li>
                    <li><b>KDE Plot</b> – Smooth distribution curves.</li>
                    <li><b>Pair Plot</b> – Multi-variable relationships in one view.</li>
                    <li><b>Box Plot</b> – Highlight medians and outliers.</li>
                    <li><b>Violin Plot</b> – Combine box plot with distribution density.</li>
                </ul>
                <p style="color:cyan; font-size:16px;">
                    📈 Use these visuals to uncover hidden patterns and communicate insights effectively.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @requires_data
    def line_plot(self):
        self._section_title("Line Plot")

        # Column selectors
        x_col = st.selectbox("Select X-axis column", self._col_options(), key="line_x_col")
        y_col = st.selectbox("Select Y-axis column", self._col_options(dtype="number"), key="line_y_col")
        group_col = self._group_col_selectbox(key="line_group_col")

        # Plot style options
        style = st.selectbox("Line style", ["select style", "solid", "dashed", "dotted"], key="line_style")
        error_option = st.selectbox("Error bars", ["select error option", "None", "ci", "pi", "se", "sd"], key="line_error_option")

        # Setting size
        width, height = self._size_inputs(w_default=10, h_default=7, key_prefix="line")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="line")

        # Marker
        marker = st.checkbox("Show markers", key="line_marker")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column" and y_col != "Select a column" and style != "select style" and error_option != "select error option":
            self._section_title("Plot", size=40)
            sns.lineplot(
                data=self.df,
                x=x_col,
                y=y_col,
                hue=group_col if group_col else None,
                style=group_col if group_col else None,
                marker="o" if marker else None,
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                linestyle=style,
                errorbar=None if error_option == "None" else error_option,
                ax=ax
            )

            ax.set_title(f"Line Plot of {y_col} vs {x_col}")
            ax.legend(
                title=group_col if group_col else "Legend",
                loc="upper right",
                bbox_to_anchor=(1.05, 1),
                fontsize=10,
                title_fontsize=12,
                frameon=True
            )
            st.pyplot(fig)
            self._offer_plot_download(fig, "Line Plot")

    @requires_data
    def scatter_plot(self):
        self._section_title("Scatter Plot")

        # Column selectors
        x_options = self._col_options()
        y_options = self._col_options(dtype="number")
        x_col = st.selectbox("Select X-axis column", x_options, key="scatter_x_col")
        y_col = st.selectbox("Select Y-axis column", y_options, key="scatter_y_col")
        group_col = self._group_col_selectbox(key="scatter_group_col")

        # Scatter style options
        marker = st.selectbox("Marker style", ["o", "s", "^", "*", "X", "D"], key="scatter_marker")
        size_option = st.selectbox("Point size column (optional)", [None] + self._numeric_cols(), key="scatter_size_option")
        alpha = st.slider("Transparency (alpha)", 0.1, 1.0, 0.7, key="scatter_alpha")

        # Setting size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="scatter")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="scatter")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column" and y_col != "Select a column":
            sns.scatterplot(
                data=self.df,
                x=x_col,
                y=y_col,
                hue=group_col if group_col else None,
                style=group_col if group_col else None,
                size=size_option if size_option else None,
                marker=marker,
                alpha=alpha,
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                ax=ax
            )

            ax.set_title(f"Scatter Plot of {y_col} vs {x_col}")
            ax.legend(title=group_col if group_col else "Legend", loc="best")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Scatter Plot")

    @requires_data
    def bar_plot(self):
        self._section_title("Bar Plot")

        # Column selectors
        x_options = self._col_options()
        y_options = self._col_options(dtype="number")
        x_col = st.selectbox("Select X-axis column", x_options, key="bar_x_col")
        y_col = st.selectbox("Select Y-axis column", y_options, key="bar_y_col")
        group_col = self._group_col_selectbox(key="bar_group_col")

        # Bar style options
        orient = st.selectbox("Orientation", ["vertical", "horizontal"], index=0, key="bar_orient")
        estimator_option = st.selectbox("Estimator", ["mean", "median", "sum", "count"], index=0, key="bar_estimator")
        error_option = st.selectbox("Error bars", ["None", "ci", "pi", "se", "sd"], index=0, key="bar_error_option")

        # Setting size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="bar")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="bar")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column" and y_col != "Select a column":
            sns.barplot(
                data=self.df,
                x=x_col if orient == "vertical" else None,
                y=y_col if orient == "vertical" else None,
                hue=group_col if group_col else None,
                estimator=getattr(np, estimator_option),
                errorbar=None if error_option == "None" else error_option,
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                orient="v" if orient == "vertical" else "h",
                ax=ax
            )

            ax.set_title(f"Bar Plot of {y_col} vs {x_col}")
            ax.legend(title=group_col if group_col else "Legend", loc="best")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Bar Plot")

    @requires_data
    def pie_plot(self):
        self._section_title("Pie Plot")

        # Column selectors
        label_options = self._col_options(dtype="object")
        value_options = self._col_options(dtype="number")
        label_col = st.selectbox("Select label column", label_options, key="pie_label_col")
        value_col = st.selectbox("Select value column", value_options, key="pie_value_col")

        # Size
        width, height = self._size_inputs(w_default=10, h_default=7, w_range=(7, 30), h_range=(7, 30), key_prefix="pie")

        # Color options
        color_pall = self._colormap_selectbox(key="pie_colormap")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if label_col != "Select a column" and value_col != "Select a column":
            values = self.df[value_col].value_counts() if label_col == "Select a column" else self.df.groupby(label_col)[value_col].sum()
            labels = values.index

            ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                # Colormaps are indexed by a float in [0, 1], not by raw
                # position -- passing range(len(values)) (0, 1, 2, ...)
                # sampled only the colormap's first few, nearly-identical
                # entries, so every sector came out looking the same color.
                # np.linspace spreads the samples across the full colormap.
                colors=plt.get_cmap(color_pall)(np.linspace(0, 1, len(values)))
            )
            ax.set_title(f"Pie Plot of {value_col} by {label_col}")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Pie Plot")

    @requires_data
    def histogram_plot(self):
        self._section_title("Histogram")

        # Column selector
        col_options = self._col_options(dtype="number")
        col = st.selectbox("Select numeric column", col_options, key="hist_col")

        # Histogram options
        bins = st.number_input("Number of bins", min_value=5, max_value=100, value=20, key="hist_bins")
        orientation = st.selectbox("Orientation", ["vertical", "horizontal"], index=0, key="hist_orientation")
        density = st.checkbox("Show density (probability)", value=False, key="hist_density")
        cumulative = st.checkbox("Show cumulative", value=False, key="hist_cumulative")

        # Size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="hist")

        # Color
        color_placeholder = "Select a color"
        color = st.selectbox("Select color", [color_placeholder] + self._get_css4_colors(), index=0, key="hist_color")
        color = None if color == color_placeholder else color

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if col != "Select a column":
            sns.histplot(
                data=self.df,
                x=col if orientation == "vertical" else None,
                y=col if orientation == "horizontal" else None,
                bins=bins,
                color=color,
                stat="density" if density else "count",
                cumulative=cumulative,
                ax=ax
            )

            ax.set_title(f"Histogram of {col}")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Histogram")

    @requires_data
    def heatmap_plot(self):
        self._section_title("Heatmap")

        # Column selector (numeric only for correlation)
        num_cols = self.df.select_dtypes(include="number").columns
        if len(num_cols) < 2:
            st.warning("Need at least two numeric columns for a heatmap.")
            return

        # Options
        annot = st.checkbox("Show values in cells", value=True, key="heatmap_annot")
        cmap = self._colormap_selectbox(key="heatmap_colormap")
        show_colorbar = st.checkbox("Show colorbar", value=True, key="heatmap_colorbar")
        linewidths = st.number_input("Cell border width", min_value=0.0, max_value=5.0, value=0.5, key="heatmap_linewidths")
        mask_upper = st.checkbox("Mask upper triangle (for correlation)", value=False, key="heatmap_mask_upper")

        # Size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="heatmap")

        # Compute correlation matrix
        corr = self.df[num_cols].corr()

        # Mask if selected
        mask = np.triu(np.ones_like(corr, dtype=bool)) if mask_upper else None

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        sns.heatmap(
            corr,
            annot=annot,
            cmap=cmap,
            cbar=show_colorbar,
            linewidths=linewidths,
            mask=mask,
            ax=ax
        )

        ax.set_title("Correlation Heatmap")
        st.pyplot(fig)
        self._offer_plot_download(fig, "Heatmap")

    @requires_data
    def kde_plot(self):
        self._section_title("KDE Plot")

        # Column selector
        num_cols = self._col_options(dtype="number")
        x_col = st.selectbox("Select column", num_cols, key="kde_x_col")
        group_col = self._group_col_selectbox(label="Optional grouping column", key="kde_group_col")

        # KDE options
        fill = st.checkbox("Fill area under curve", value=True, key="kde_fill")
        bw_adjust = st.slider("Bandwidth adjustment", 0.1, 2.0, 1.0, step=0.1, key="kde_bw_adjust")

        # Size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="kde")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="kde")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column":
            sns.kdeplot(
                data=self.df,
                x=x_col,
                hue=group_col if group_col else None,
                fill=fill,
                bw_adjust=bw_adjust,
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                ax=ax
            )

            ax.set_title(f"KDE Plot of {x_col}")
            st.pyplot(fig)
            self._offer_plot_download(fig, "KDE Plot")

    @requires_data
    def pairplot_plot(self):
        self._section_title("Pairplot")

        # Numeric columns
        num_cols = self._numeric_cols()
        if len(num_cols) < 2:
            st.warning("Need at least two numeric columns for a pairplot.")
            return

        # Options
        selected_vars = st.multiselect("Select variables (optional)", num_cols, default=num_cols[:3], key="pair_vars")
        group_col = self._group_col_selectbox(label="Optional grouping column (hue)", key="pair_group_col")
        kind = st.selectbox("Plot kind", ["scatter", "kde"], index=0, key="pair_kind")
        diag_kind = st.selectbox("Diagonal plot type", ["auto", "hist", "kde"], index=0, key="pair_diag_kind")
        palette = self._colormap_selectbox(label="Select colormap/palette", key="pair_palette")
        height = st.number_input("Plot height per facet", min_value=2, max_value=6, value=3, key="pair_height")

        # Plotting
        vars_to_use = selected_vars if selected_vars else num_cols
        fig = sns.pairplot(
            data=self.df,
            vars=vars_to_use,
            hue=group_col if group_col else None,
            kind=kind,
            diag_kind=diag_kind,
            palette=palette,
            height=height
        )

        st.pyplot(fig)
        self._offer_plot_download(fig, "Pair Plot")

    @requires_data
    def boxplot_plot(self):
        self._section_title("Box Plot")

        # Column selectors
        x_options = self._col_options()
        y_options = self._col_options(dtype="number")
        x_col = st.selectbox("Select X-axis column (categorical)", x_options, key="box_x_col")
        y_col = st.selectbox("Select Y-axis column (numeric)", y_options, key="box_y_col")
        group_col = self._group_col_selectbox(label="Optional grouping column (hue)", key="box_group_col")

        # Boxplot options
        orient = st.selectbox("Orientation", ["vertical", "horizontal"], index=0, key="box_orient")
        showfliers = st.checkbox("Show outliers", value=True, key="box_showfliers")
        notch = st.checkbox("Notched box", value=False, key="box_notch")

        # Size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="box")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="box")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column" and y_col != "Select a column":
            sns.boxplot(
                data=self.df,
                x=x_col if orient == "vertical" else None,
                y=y_col if orient == "vertical" else None,
                hue=group_col if group_col else None,
                orient="v" if orient == "vertical" else "h",
                showfliers=showfliers,
                notch=notch,
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                ax=ax
            )

            ax.set_title(f"Box Plot of {y_col} by {x_col}")
            ax.legend(title=group_col if group_col else "Legend", loc="best")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Box Plot")

    @requires_data
    def violin_plot(self):
        self._section_title("Violin Plot")

        # Column selectors
        x_options = self._col_options()
        y_options = self._col_options(dtype="number")
        x_col = st.selectbox("Select X-axis column (categorical)", x_options, key="violin_x_col")
        y_col = st.selectbox("Select Y-axis column (numeric)", y_options, key="violin_y_col")
        group_col = self._group_col_selectbox(label="Optional grouping column (hue)", key="violin_group_col")

        # Violin options
        orient = st.selectbox("Orientation", ["vertical", "horizontal"], index=0, key="violin_orient")
        split = st.checkbox("Split violins (for hue)", value=False, key="violin_split")
        inner = st.selectbox("Inner representation", ["box", "quartile", "stick", "point", "None"], index=0, key="violin_inner")

        # Size
        width, height = self._size_inputs(w_default=12, h_default=7, key_prefix="violin")

        # Color or Color Palette
        color, color_pall = self._color_or_palette(group_col, key_prefix="violin")

        # Plotting
        fig, ax = plt.subplots(figsize=(width, height))
        if x_col != "Select a column" and y_col != "Select a column":
            sns.violinplot(
                data=self.df,
                x=x_col if orient == "vertical" else None,
                y=y_col if orient == "vertical" else None,
                hue=group_col if group_col else None,
                split=split if group_col else False,
                inner=None if inner == "None" else inner,
                orient="v" if orient == "vertical" else "h",
                color=color if group_col is None else None,
                palette=color_pall if group_col is not None else None,
                ax=ax
            )

            ax.set_title(f"Violin Plot of {y_col} by {x_col}")
            ax.legend(title=group_col if group_col else "Legend", loc="best")
            st.pyplot(fig)
            self._offer_plot_download(fig, "Violin Plot")