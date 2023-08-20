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




st.title('Assumptions')
st.write(ASSUMPTIONS)