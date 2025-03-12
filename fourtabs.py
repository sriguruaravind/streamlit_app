from altair import to_values
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from datetime import datetime, timedelta

# Connection parameters for actual data
SRC_DB_CONFIG = {
    "server": "10.160.15.197,50000",
    "database": "Workupdb",
    "username": "GurubalajiDatauser",
    "password": "DataUsr@2025",
}

# Connection parameters for predicted data
DEST_DB_CONFIG = {
    "server": "10.160.15.198,50000",
    "database": "Ihmsdb",
    "username": "GurubalajiDatauser",
    "password": "DataUsr@2025",
}

# Function to connect to database and execute query
def connect_and_query(db_config, query):
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db_config['server']};DATABASE={db_config['database']};UID={db_config['username']};PWD={db_config['password']}"
    conn = pyodbc.connect(conn_str)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# SQL query for actual data
actual_query = """
    SELECT 
        visit_date AS date,
        PayopNew, PayopReview, FreeopNew, FreeopReview
    FROM 
        [Workupdb].[dbo].[Tbl_ptStatistics_Forecasting]
    WHERE 
        visit_date >= '2025-02-24';
"""

# SQL query for predicted data
predicted_query = """
    SELECT DISTINCT 
        F_DATE AS date,
        EXP_PAY_NEW, EXP_PAY_REV, EXP_FREE_NEW, EXP_FREE_REV
    FROM 
        [Ihmsdb].[dbo].[Tbl_PatientForecast]
    WHERE 
        F_DATE >= '2025-02-24';
"""

# Streamlit setup
st.set_page_config(layout="wide")
st.title('Actual vs Predicted Dashboard')

# Retrieve actual data
actual_df = connect_and_query(SRC_DB_CONFIG, actual_query)

# Retrieve predicted data
predicted_df = connect_and_query(DEST_DB_CONFIG, predicted_query)

# Merge actual and predicted data
merged_df = pd.merge(actual_df, predicted_df, on='date', how='inner')

# Sort data by date
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df = merged_df.sort_values(by='date')

# Sort data by date
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df = merged_df.sort_values(by='date')

# Sort data by date
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df = merged_df.sort_values(by='date')

# Calculate T-1 (previous day)
previous_day = merged_df['date'].max() - timedelta(days=1)

# --- Combined Bar Chart for T-1 Day ---
st.subheader('Actual vs Predicted for Last Day')

t_minus_1_data = merged_df[merged_df['date'].dt.date == previous_day.date()]  # Get T-1 day's data

if not t_minus_1_data.empty:
    t_minus_1_date = t_minus_1_data['date'].iloc[0].strftime('%Y-%m-%d')
    actual_values = [t_minus_1_data['PayopNew'].iloc[0], t_minus_1_data['PayopReview'].iloc[0], t_minus_1_data['FreeopNew'].iloc[0], t_minus_1_data['FreeopReview'].iloc[0]]
    predicted_values = [t_minus_1_data['EXP_PAY_NEW'].iloc[0], t_minus_1_data['EXP_PAY_REV'].iloc[0], t_minus_1_data['EXP_FREE_NEW'].iloc[0], t_minus_1_data['EXP_FREE_REV'].iloc[0]]
    categories = ['PayopNew', 'PayopReview', 'FreeopNew', 'FreeopReview']

    combined_df = pd.DataFrame({
        'Category': categories * 2,
        'Value': actual_values + predicted_values,
        'Type': ['Actual'] * 4 + ['Predicted'] * 4
    })

    fig_combined = px.bar(
        combined_df, x='Category', y='Value', color='Type',
        title=f'Actual vs Predicted for {t_minus_1_date}',
        barmode='group', color_discrete_sequence=['#FF6347', '#4682B4'],
        text_auto=True
    )
    fig_combined.update_traces(textposition='outside')
    st.plotly_chart(fig_combined, use_container_width=True)
else:
    st.info(f'No data available for {previous_day.strftime("%Y-%m-%d")}.')


# Tab selection for different columns
tab = st.radio("Select Tab", ["PayopNew", "PayopReview", "FreeopNew", "FreeopReview"], horizontal=True)

# Function to create and display the charts and metrics
def display_data_for_column(actual_col, predicted_col):
    # Filter data for the selected column
    column_data = merged_df[['date', actual_col, predicted_col]]

    # Bar chart section
    st.subheader(f'Actual vs Predicted (Bar Chart) ({actual_col} vs {predicted_col})')

    # Buttons to select data range for the bar chart
    selected_range_bar = 'Last 1 Week'
    col3, col4, col5 = st.columns([1, 1, 1])

    with col3:
        if st.button('Last 1 Week(Bar)'):
            filtered_data_bar = column_data.tail(7)
            selected_range_bar = 'Last 1 Week'

    with col4:
        if st.button('Last 1 Month(Bar)'):
            filtered_data_bar = column_data.tail(30)
            selected_range_bar = 'Last 1 Month'

    with col5:
        if st.button('Last 3 Months(Bar)'):
            filtered_data_bar = column_data.tail(90)
            selected_range_bar = 'Last 3 Months'

    if selected_range_bar == 'Last 1 Week':
        filtered_data_bar = column_data.tail(7)
    elif selected_range_bar == 'Last 1 Month':
        filtered_data_bar = column_data.tail(30)
    elif selected_range_bar == 'Last 3 Months':
        filtered_data_bar = column_data.tail(90)
    else:
        filtered_data_bar = column_data

    fig_bar = px.bar(
        filtered_data_bar, x='date', y=[actual_col, predicted_col],
        title=f'Actual vs Predicted ({selected_range_bar})',
        barmode='group', color_discrete_sequence=['#FF6347', '#4682B4'],
        text_auto=True
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Line chart section
    st.subheader(f'Actual vs Predicted (Line Chart) ({actual_col} vs {predicted_col})')

    # Buttons to select data range for the line chart
    selected_range_line = 'All Time'
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button('Last 1 Week(Line)'):
            filtered_data_line = column_data.tail(7)
            selected_range_line = 'Last 1 Week'

    with col2:
        if st.button('Last 1 Month(Line)'):
            filtered_data_line = column_data.tail(30)
            selected_range_line = 'Last 1 Month'

    if selected_range_line == 'Last 1 Week':
        filtered_data_line = column_data.tail(7)
    elif selected_range_line == 'Last 1 Month':
        filtered_data_line = column_data.tail(30)
    else:
        filtered_data_line = column_data

    fig_line = px.line(
        filtered_data_line, x='date', y=[actual_col, predicted_col],
        title=f'Actual vs Predicted ({selected_range_line})',
        color_discrete_sequence=['#FF6347', '#4682B4']
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Performance metrics section for last 7 days
    st.subheader('Performance Metrics (Last 7 Days)')
    last_7_days_data = filtered_data_bar.tail(7)
    avg_deviation_7d = round((abs(last_7_days_data[actual_col] - last_7_days_data[predicted_col]) / last_7_days_data[actual_col] * 100).mean(), 2)
    highest_deviation_day = last_7_days_data.loc[(abs(last_7_days_data[actual_col] - last_7_days_data[predicted_col]) / last_7_days_data[actual_col] * 100).idxmax()]
    lowest_deviation_day = last_7_days_data.loc[(abs(last_7_days_data[actual_col] - last_7_days_data[predicted_col]) / last_7_days_data[actual_col] * 100).idxmin()]
    within_threshold = len(last_7_days_data[(abs(last_7_days_data[actual_col] - last_7_days_data[predicted_col]) / last_7_days_data[actual_col] * 100) <= 10])
    total_days = len(last_7_days_data)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label='📊 Average Deviation (Last 7 Days)', value=f'{avg_deviation_7d}%')
    col2.metric(label='✅ Days Within Threshold', value=f'{within_threshold}/{total_days}')
    col3.metric(label='📉 Lowest Deviation Day', value=f'{round((abs(lowest_deviation_day[actual_col] - lowest_deviation_day[predicted_col]) / lowest_deviation_day[actual_col] * 100), 2)}%')
    col4.metric(label='📈 Highest Deviation Day', value=f'{round((abs(highest_deviation_day[actual_col] - highest_deviation_day[predicted_col]) / highest_deviation_day[actual_col] * 100), 2)}%')


    # Prediction accuracy pie chart
    st.subheader('Prediction Accuracy')
    within_range = len(filtered_data_bar[abs(filtered_data_bar[actual_col] - filtered_data_bar[predicted_col]) / filtered_data_bar[actual_col] * 100 <= 10])
    out_of_range = len(filtered_data_bar[abs(filtered_data_bar[actual_col] - filtered_data_bar[predicted_col]) / filtered_data_bar[actual_col] * 100 > 10])
    fig_pie = px.pie(
        names=['Within Threshold', 'Exceeded Threshold'],
        values=[within_range, out_of_range],
        title='Predictions Within vs Exceeded Threshold',
        color_discrete_sequence=['#FF6347', '#4682B4']
    )
    st.plotly_chart(fig_pie, use_container_width=True)


    # Specific date selection
    st.subheader('View Data for a Specific Date')
    date_to_view = st.date_input('Select a date', min_value=merged_df['date'].min().date(), max_value=merged_df['date'].max().date())

    if st.button('View'):
        specific_date_data = merged_df[merged_df['date'].dt.date == date_to_view]
        if not specific_date_data.empty:
            st.write(f"### Data for {date_to_view}:")
            st.write(specific_date_data[['date', actual_col, predicted_col]])
        else:
            st.info(f"No data available for {date_to_view}.")

# Call the display function based on selected tab
if tab == "PayopNew":
    display_data_for_column('PayopNew', 'EXP_PAY_NEW')
elif tab == "PayopReview":
    display_data_for_column('PayopReview', 'EXP_PAY_REV')
elif tab == "FreeopNew":
    display_data_for_column('FreeopNew', 'EXP_FREE_NEW')
elif tab == "FreeopReview":
    display_data_for_column('FreeopReview', 'EXP_FREE_REV')
