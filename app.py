import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

def parse_session_times(data):
    session_intervals = []
    presence_counts = {}
    drop_counts = {}

    # Define the session start time and 5-minute intervals
    session_start_time = datetime.strptime('1/9/2024, 4:50:00 pm', '%d/%m/%Y, %I:%M:%S %p')
    interval = timedelta(minutes=5)
    
    # Generate time intervals
    current_time = session_start_time
    for _ in range(40):  # Generating 40 intervals to cover up to 200 minutes
        session_intervals.append(current_time)
        presence_counts[current_time] = 0
        drop_counts[current_time] = 0
        current_time += interval

    # Process each user's session data
    for _, row in data.iterrows():
        session_list = str(row['Sessions']).split('\n')
        for session in session_list:
            if not session.strip():
                continue
            start_time_str, end_time_str = session.split(' - ')
            start_time = datetime.strptime(start_time_str.strip(), '%d/%m/%Y, %I:%M:%S %p')
            end_time = datetime.strptime(end_time_str.strip(), '%d/%m/%Y, %I:%M:%S %p')

            # Count presence and drops in each 5-minute interval
            for interval_start in session_intervals:
                interval_end = interval_start + interval
                if start_time <= interval_start < end_time:
                    presence_counts[interval_start] += 1
                if interval_start <= end_time < interval_end:
                    drop_counts[interval_start] += 1

    return presence_counts, drop_counts

def main():
    st.title("User Session Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file is not None:
        # Read the uploaded file
        data = pd.read_csv(uploaded_file)
        
        # Calculate presence and drop counts
        presence_counts, drop_counts = parse_session_times(data)

        # Prepare data for DataFrame
        intervals = list(presence_counts.keys())
        presence_values = list(presence_counts.values())
        drop_values = list(drop_counts.values())
        
        # Create a DataFrame
        interval_data = pd.DataFrame({
            'Time Interval': [interval.strftime('%I:%M %p') for interval in intervals],
            'Users Present': presence_values,
            'Users Dropped': drop_values
        })

        # Display the DataFrame
        st.write("User Presence and Drop-Off Data:")
        st.dataframe(interval_data)

        # Downloadable CSV
        csv = interval_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='User_Presence_and_Drop_Intervals.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
