import streamlit as st

st.title("Datasets Used")
st.markdown("""
    1. Freight Vehicle Congestion
        - https://data.gov.au/data/dataset/freight-vehicle-congestion-in-australia-s-5-major-cities 
        - Used to show local roads data on maps.
    2. National Key Freight Routes Map
        - https://catalogue.data.infrastructure.gov.au/dataset/national-key-freight-routes-map 
        - Used to show national rail and road freight routes on maps.
    3. Forecasted commodity demand
        - https://www.transport.nsw.gov.au/system/files/media/documents/2018/NSW%20Freight%20Commodity%20Demand%20Forecasts%202016-56%5Baccessible%5D_0.pdf
        - Used to generate forecast slider values
    4. CO2 produced from hydrogen generation techniques
        - https://www.iea.org/reports/towards-hydrogen-definitions-based-on-their-emissions-intensity
        - Used to predict CO2 emissions from hydrogen generation sources
    5. CO2 emissions from freight transport
        - https://www.ecta.com/wp-content/uploads/2021/03/ECTA-CEFIC-GUIDELINE-FOR-MEASURING-AND-MANAGING-CO2-ISSUE-1.pdf
        - Used for baseline emissions
    6. Current production of hydrogen from different sources 
        - https://iea.blob.core.windows.net/assets/9e3a3493-b9a6-4b7d-b499-7ca48e357561/The_Future_of_Hydrogen.pdf
        - Used for baseline hydrogen production
""")