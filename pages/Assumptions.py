import pandas as pd
import streamlit as st

# GCO2: https://www.ecta.com/wp-content/uploads/2021/03/ECTA-CEFIC-GUIDELINE-FOR-MEASURING-AND-MANAGING-CO2-ISSUE-1.pdf

ASSUMPTIONS = {
    "tonne.km/hr": {
      "air": "100000",
      "rail": "300000",
      "road_interstate": "1500",
      "road_urban": "180"
    },
    "gco2/tonne.km": {
      "air": "602",
      "rail": "22",
      "road_interstate": "62",
      "road_urban": "50"
    }
}

assumptions_df = pd.DataFrame(ASSUMPTIONS)
assumptions_df.columns = ["(Tonne KM) / Hour", "GCO2 / (Tonne KM)"]
assumptions_df.index = ["Air", "Rail", "Road (Interstate)", "Road (Urban)"]

if __name__ == "__main__": 
  st.title('Assumptions')
  st.dataframe(assumptions_df, use_container_width=True)

