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

# --- 1. Graph showing yesterday's values ---
st.subheader('Actual vs Predicted for Last Day')

# Calculate T-1 (previous day)
previous_day = df['date'].max() - timedelta(days=1)
t_minus_1_data = df[df['date'] == previous_day]  # Get T-1 day's data

if not t_minus_1_data.empty:
    t_minus_1_date = t_minus_1_data['date'].iloc[0].strftime('%Y-%m-%d')

    # Default columns to display (PayopNew and EXP_PAY_NEW)
    actual_col = 'PayopNew'
    predicted_col = 'EXP_PAY_NEW'

    # Getting the actual and predicted values for the selected column
    actual_values = [
        t_minus_1_data[actual_col].iloc[0],  # Actual value for selected column
        t_minus_1_data[actual_col].iloc[0]  # Actual value for selected column
    ]
    predicted_values = [
        t_minus_1_data[predicted_col].iloc[0],  # Predicted value for selected column
        t_minus_1_data[predicted_col].iloc[0]  # Predicted value for selected column
    ]
    
    categories = [actual_col, predicted_col]  # This should have 2 elements for actual and predicted

    # Ensure that categories, actual_values, and predicted_values have the same length
    combined_df = pd.DataFrame({
        'Category': categories * 2,
        'Value': actual_values + predicted_values,
        'Type': ['Actual'] * 2 + ['Predicted'] * 2  # Length of 'Type' matches 'Value'
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

# --- 2. Radio Button to select column ---
tab = st.radio("Select the column to predict", ["PayopNew", "PayopReview", "FreeopNew", "FreeopReview"], horizontal=True)

# --- 3. Bar Chart ---
st.subheader(f'Actual vs Predicted Bar Chart ({tab})')

# Filter the data based on selected column
column_data = df[['date', tab, 'EXP_' + tab]]

# Select the range for bar chart
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

fig_bar = px.bar(
    filtered_data_bar, x='date', y=[tab, 'EXP_' + tab],
    title=f'Actual vs Predicted ({selected_range_bar})',
    barmode='group', color_discrete_sequence=['#FF6347', '#4682B4'],
    text_auto=True
)
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)

# --- 4. Line Chart ---
st.subheader(f'Actual vs Predicted Line Chart ({tab})')

# Radio button to select line chart range
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

fig_line = px.line(
    filtered_data_line, x='date', y=[tab, 'EXP_' + tab],
    title=f'Actual vs Predicted ({selected_range_line})',
    color_discrete_sequence=['#FF6347', '#4682B4']
)
st.plotly_chart(fig_line, use_container_width=True)

# --- 5. Performance Metrics ---
st.subheader('Performance Metrics (Last 7 Days)')

# Calculate last 7 days' performance
last_7_days_data = filtered_data_bar.tail(7)
avg_deviation_7d = round((abs(last_7_days_data[tab] - last_7_days_data['EXP_' + tab]) / last_7_days_data[tab] * 100).mean(), 2)
highest_deviation_day = last_7_days_data.loc[(abs(last_7_days_data[tab] - last_7_days_data['EXP_' + tab]) / last_7_days_data[tab] * 100).idxmax()]
lowest_deviation_day = last_7_days_data.loc[(abs(last_7_days_data[tab] - last_7_days_data['EXP_' + tab]) / last_7_days_data[tab] * 100).idxmin()]
within_threshold = len(last_7_days_data[(abs(last_7_days_data[tab] - last_7_days_data['EXP_' + tab]) / last_7_days_data[tab] * 100) <= 10])
total_days = len(last_7_days_data)

col1, col2, col3, col4 = st.columns(4)

col1.metric(label='📊 Average Deviation (Last 7 Days)', value=f'{avg_deviation_7d}%')
col2.metric(label='✅ Days Within Threshold', value=f'{within_threshold}/{total_days}')
col3.metric(label='📉 Lowest Deviation Day', value=f'{round((abs(lowest_deviation_day[tab] - lowest_deviation_day['EXP_' + tab]) / lowest_deviation_day[tab] * 100), 2)}%')
col4.metric(label='📈 Highest Deviation Day', value=f'{round((abs(highest_deviation_day[tab] - highest_deviation_day['EXP_' + tab]) / highest_deviation_day[tab] * 100), 2)}%')

# --- 6. Prediction Accuracy Pie Chart ---
st.subheader('Prediction Accuracy')

within_range = len(filtered_data_bar[abs(filtered_data_bar[tab] - filtered_data_bar['EXP_' + tab]) / filtered_data_bar[tab] * 100 <= 10])
out_of_range = len(filtered_data_bar[abs(filtered_data_bar[tab] - filtered_data_bar['EXP_' + tab]) / filtered_data_bar[tab] * 100 > 10])

fig_pie = px.pie(
    names=['Within Threshold', 'Exceeded Threshold'],
    values=[within_range, out_of_range],
    title='Predictions Within vs Exceeded Threshold',
    color_discrete_sequence=['#FF6347', '#4682B4']
)
st.plotly_chart(fig_pie, use_container_width=True)

# --- 7. View Data for a Specific Date ---
st.subheader('View Data for a Specific Date')
date_to_view = st.date_input('Select a date', min_value=df['date'].min().date(), max_value=df['date'].max().date())

if st.button('View'):
    specific_date_data = df[df['date'].dt.date == date_to_view]
    if not specific_date_data.empty:
        st.write(f"### Data for {date_to_view}:")
        st.write(specific_date_data[['date', tab, 'EXP_' + tab]])
    else:
        st.info(f"No data available for {date_to_view}.")
