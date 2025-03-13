import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

# Function to create synthetic data for 1 month
def create_synthetic_data_for_one_month():
    # Date range for the last month (30 days)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Randomized data for actual and predicted columns
    data = {
        'date': date_range,
        'PayopNew': np.random.randint(50, 100, size=len(date_range)),
        'PayopReview': np.random.randint(10, 50, size=len(date_range)),
        'FreeopNew': np.random.randint(100, 200, size=len(date_range)),
        'FreeopReview': np.random.randint(20, 80, size=len(date_range)),
        'EXP_PAY_NEW': np.random.randint(50, 100, size=len(date_range)),
        'EXP_PAY_REV': np.random.randint(10, 50, size=len(date_range)),
        'EXP_FREE_NEW': np.random.randint(100, 200, size=len(date_range)),
        'EXP_FREE_REV': np.random.randint(20, 80, size=len(date_range)),
    }
    
    return pd.DataFrame(data)

# Generate synthetic data for the last month (30 days)
df = create_synthetic_data_for_one_month()

# Streamlit setup
st.set_page_config(layout="wide")
st.title('Actual vs Predicted Dashboard')

# --- Radio Button for Selecting the Category ---
selected_column = st.radio("Select Column to View Prediction", ["PayopNew", "PayopReview", "FreeopNew", "FreeopReview"], index=0, horizontal=True)

# Mapping for the selected column to the respective predicted column
column_mapping = {
    "PayopNew": "EXP_PAY_NEW",
    "PayopReview": "EXP_PAY_REV",
    "FreeopNew": "EXP_FREE_NEW",
    "FreeopReview": "EXP_FREE_REV"
}

actual_col = selected_column
predicted_col = column_mapping[selected_column]

# Function to create and display the charts and metrics for a selected category
def display_data_for_column(actual_col, predicted_col):
    # Filter data for the selected column
    column_data = df[['date', actual_col, predicted_col]]

    # --- Bar Chart Section ---
    st.subheader(f'Actual vs Predicted (Bar Chart) ({actual_col} vs {predicted_col})')

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

    # --- Line Chart Section ---
    st.subheader(f'Actual vs Predicted (Line Chart) ({actual_col} vs {predicted_col})')

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

    # --- Prediction Accuracy Pie Chart ---
    st.subheader('Prediction Accuracy')
    within_range = len(column_data[abs(column_data[actual_col] - column_data[predicted_col]) / column_data[actual_col] * 100 <= 10])
    out_of_range = len(column_data[abs(column_data[actual_col] - column_data[predicted_col]) / column_data[actual_col] * 100 > 10])
    fig_pie = px.pie(
        names=['Within Threshold', 'Exceeded Threshold'],
        values=[within_range, out_of_range],
        title='Predictions Within vs Exceeded Threshold',
        color_discrete_sequence=['#FF6347', '#4682B4']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- Performance Metrics ---
    st.subheader('Performance Metrics (Last 7 Days)')
    last_7_days_data = column_data.tail(7)
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

# Display all charts and metrics for the selected column
display_data_for_column(actual_col, predicted_col)
