import streamlit as st
import pandas as pd
from layout import Layout


class ProjectVars:
    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.file = self.layout.uploaded_file
        self.df = None

        if self.file is not None:
            # Fingerprint the upload (name + size). The original code only
            # checked `"df" not in st.session_state`, so uploading a second,
            # different CSV after the first one was silently ignored -- the
            # old dataframe stuck around for the rest of the session. This
            # fingerprint makes sure a genuinely new file gets (re)loaded.
            file_id = (self.file.name, self.file.size)

            if st.session_state.get("_uploaded_file_id") != file_id:
                try:
                    st.session_state.df = pd.read_csv(self.file)
                    st.session_state._uploaded_file_id = file_id
                except Exception as e:
                    st.error(f"❌ Could not read the uploaded CSV file: {e}")
                    st.session_state.pop("df", None)
                    st.session_state.pop("_uploaded_file_id", None)

            self.df = st.session_state.get("df")
        else:
            # No file selected (or it was removed) -> clear any cached dataset
            # so stale data doesn't linger across reruns.
            st.session_state.pop("df", None)
            st.session_state.pop("_uploaded_file_id", None)
            self.df = None
