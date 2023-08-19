import streamlit as st

ASSUMPTIONS = {
    "tonne.km/hr": {
      "air": "213000000",
      "rail": "180",
      "road_interstate": "1500",
      "road_urban": "180"
    },
    "gco2/tonne.mk": {
      "air": "800",
      "rail": "307",
      "road_interstate": "57",
      "road_urban": "307"
    }
}


st.title('Assumptions')
st.write(ASSUMPTIONS)