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

# Radio Button to Select Column
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

# --- 1. Graph showing yesterday's values ---
st.subheader('Actual vs Predicted for Last Day')

# Calculate T-1 (previous day)
previous_day = df['date'].max() - timedelta(days=1)
t_minus_1_data = df[df['date'] == previous_day]  # Get T-1 day's data

if not t_minus_1_data.empty:
    t_minus_1_date = t_minus_1_data['date'].iloc[0].strftime('%Y-%m-%d')
    actual_values = [
        t_minus_1_data[actual_col].iloc[0],
        t_minus_1_data[selected_column].iloc[0],
    ]
    predicted_values = [
        t_minus_1_data[predicted_col].iloc[0],
        t_minus_1_data[selected_column].iloc[0],
    ]
    categories = [selected_column]

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

# --- 2. Radio Button to Select Graph Type for Bar Chart ---
st.subheader(f'{selected_column} vs {predicted_col} Bar Chart')
show_bar_chart = st.radio("Show Bar Chart for " + selected_column, ['Yes', 'No'])

if show_bar_chart == 'Yes':
    column_data = df[['date', actual_col, predicted_col]]
    fig_bar = px.bar(
        column_data, x='date', y=[actual_col, predicted_col],
        title=f'Actual vs Predicted ({actual_col} vs {predicted_col})',
        barmode='group', color_discrete_sequence=['#FF6347', '#4682B4'],
        text_auto=True
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 3. Radio Button to Select Graph Type for Line Chart ---
st.subheader(f'{selected_column} vs {predicted_col} Line Chart')
show_line_chart = st.radio("Show Line Chart for " + selected_column, ['Yes', 'No'])

if show_line_chart == 'Yes':
    column_data = df[['date', actual_col, predicted_col]]
    fig_line = px.line(
        column_data, x='date', y=[actual_col, predicted_col],
        title=f'Actual vs Predicted ({actual_col} vs {predicted_col})',
        color_discrete_sequence=['#FF6347', '#4682B4']
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- 4. Radio Button to Select Graph Type for Metrics ---
st.subheader(f'{selected_column} vs {predicted_col} Performance Metrics')
show_metrics = st.radio("Show Metrics for " + selected_column, ['Yes', 'No'])

if show_metrics == 'Yes':
    column_data = df[['date', actual_col, predicted_col]]
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

# --- 5. Radio Button to Select Graph Type for Pie Chart ---
st.subheader(f'{selected_column} vs {predicted_col} Pie Chart')
show_pie_chart = st.radio("Show Pie Chart for " + selected_column, ['Yes', 'No'])

if show_pie_chart == 'Yes':
    column_data = df[['date', actual_col, predicted_col]]
    within_range = len(column_data[abs(column_data[actual_col] - column_data[predicted_col]) / column_data[actual_col] * 100 <= 10])
    out_of_range = len(column_data[abs(column_data[actual_col] - column_data[predicted_col]) / column_data[actual_col] * 100 > 10])
    fig_pie = px.pie(
        names=['Within Threshold', 'Exceeded Threshold'],
        values=[within_range, out_of_range],
        title='Predictions Within vs Exceeded Threshold',
        color_discrete_sequence=['#FF6347', '#4682B4']
    )
    st.plotly_chart(fig_pie, use_container_width=True)
