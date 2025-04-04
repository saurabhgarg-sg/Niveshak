import numpy as np
import pandas as pd
import streamlit as st

dataframe = pd.DataFrame(
    np.random.randn(10, 20), columns=("col %d" % i for i in range(20))
)
st.table(dataframe)
