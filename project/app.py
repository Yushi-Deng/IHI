import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
# Load data
data = pd.read_csv('Outbreak_240817.csv',encoding='ISO-8859-1')

# Create a list of country choices from your data
country_choices = ['All Countries'] + sorted(data['country'].unique())

# Convert 'reportingDate' column to datetime
data['reportingDate'] = pd.to_datetime(data['reportingDate'])

# Streamlit application
st.title('2017 Bird Flu Trend Visualization')

#Selection dropdowns 
with st.sidebar.form(key="my_form"):
    selectbox_country = st.selectbox("Choose a country", country_choices)
    # Default date is set to the earliest reporting date
    date_range = st.date_input("Select reporting date range",
                               value =(datetime.date(2015,1,9),
                                       datetime.date(2017, 12, 7)),
                               min_value= datetime.date(2015,1,9),
                               max_value=datetime.date(2017,12,7))
                            #    value=(data['reportingDate'].min(), data['reportingDate'].max())
    submit_button = st.form_submit_button("Filter Map")
# If form is submitted, use filtered data; otherwise, default to  data.
if submit_button:
    if selectbox_country == 'All Countries':
        filtered_data = data
    else:
        filtered_data = data[data['country'] == selectbox_country]
    
    # Convert selected dates to datetime and then to "mm/dd/yyyy" strings for display
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    start_date_str = start_date.strftime("%m/%d/%Y")
    end_date_str = end_date.strftime("%m/%d/%Y")
    # # (Optional) Display the formatted date range to the user
    # st.write(f"Filtering data from {start_date_str} to {end_date_str}")

    # Define start and end dates from the selected date range
    # start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
     
    # Filter data within the selected date range
    filtered_data = filtered_data[(filtered_data['reportingDate'] >= start_date) & (filtered_data['reportingDate'] <= end_date)]
else:
    filtered_data = data

     
# Create a map using the filtered (or full) dataset
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=filtered_data['latitude'].mean(),
        longitude=filtered_data['longitude'].mean(),
        zoom=2,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_data,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=50000,
            pickable=True
        ),
    ],
))

# Convert the filtered DataFrame to CSV format without the index
csv_data = filtered_data.to_csv(index=False)
 
# Create a download button for exporting the filtered data as a CSV file
st.download_button(
    label="Export Data",
    data=csv_data,
    file_name="filtered_data.csv",
    mime="text/csv"
)

#Total case count metric
total_observations = data['country'].count()
st.write("Total case observations:", total_observations)        

#Top country table
country_counts = data.groupby('country').size().reset_index(name='cases')
top_countries = country_counts.sort_values(by='cases', ascending=False).head(3)

#Top dates table - Yijun
date_counts = data.groupby('reportingDate').size().reset_index(name='observation_counts')
top_dates = date_counts.sort_values(by='observation_counts', ascending=False).head(3)


# Create two columns for side-by-side display
col1, col2 = st.columns(2)

with col1:
    st.header("Countries with most cases")
    html_table = top_countries.to_html(index=False)
    st.markdown(html_table, unsafe_allow_html=True)
    
with col2:
    st.header("Dates with most new cases")
    html_table = top_dates.to_html(index=False)
    st.markdown(html_table, unsafe_allow_html=True)




st.write(data)  # Display the data as a table below the map
