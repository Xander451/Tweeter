import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread

# Create a scheduler instance
scheduler = BackgroundScheduler()

# Function to post tweet with image
def post_tweet_with_image(bearer_token, tweet_text, image_path):
    try:
        # Twitter API v2 endpoint URL
        api_url = 'https://api.twitter.com/2/tweets'

        # Upload media
        media_upload_url = f"{api_url}/media/upload"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        files = {
            'media': open(image_path, 'rb')
        }
        response = requests.post(media_upload_url, headers=headers, files=files)
        response.raise_for_status()
        media_id = response.json()['media_id']

        # Create tweet with media
        tweet_create_url = f"{api_url}/tweets"
        tweet_data = {
            "text": tweet_text,
            "media_ids": [media_id]
        }
        response = requests.post(tweet_create_url, headers=headers, json=tweet_data)
        response.raise_for_status()
        st.success("Tweet posted successfully!")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        st.error(f"Error posting tweet: {e}")

# Schedule tweet function
def schedule_tweet_wrapper(bearer_token, tweet_text, image_path, schedule_time):
    def job():
        post_tweet_with_image(bearer_token, tweet_text, image_path)

    scheduler.add_job(job, 'date', run_date=schedule_time)

# Start the scheduler
def start_scheduler():
    scheduler.start()

def main():
    st.title("Tweet with Image Posting")

    # User input for Twitter API credentials
    st.write("### Twitter API Authentication")
    bearer_token = st.text_input("Enter your Twitter API Bearer Token:")

    # User input for tweet details
    st.write("### Tweet Details")
    tweet_text = st.text_input("Enter your tweet text:")
    uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"], accept_multiple_files=False)

    # Scheduling inputs
    st.write("### Schedule Tweet")
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Time")
    end_date = st.date_input("End Date")
    frequency = st.selectbox("Frequency", ["Once", "Daily", "Weekly"])

    if st.button("Schedule Tweet"):
        if tweet_text and uploaded_file and bearer_token:
            try:
                # Save the uploaded file to a temporary directory
                with open("temp_image.jpg", "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Calculate the first schedule time based on user inputs
                schedule_time = datetime.combine(start_date, start_time)

                if frequency == "Daily":
                    # For daily frequency, schedule for every day until end_date
                    while schedule_time <= end_date:
                        schedule_tweet_wrapper(bearer_token, tweet_text, "temp_image.jpg", schedule_time)
                        schedule_time += timedelta(days=1)
                elif frequency == "Weekly":
                    # For weekly frequency, schedule for every week until end_date
                    while schedule_time <= end_date:
                        schedule_tweet_wrapper(bearer_token, tweet_text, "temp_image.jpg", schedule_time)
                        schedule_time += timedelta(weeks=1)
                else:
                    # For once frequency, schedule only once
                    schedule_tweet_wrapper(bearer_token, tweet_text, "temp_image.jpg", schedule_time)

                st.success("Tweet scheduled successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter tweet text, choose an image, and provide the Twitter API Bearer Token.")

if __name__ == "__main__":
    # Start the scheduler in a separate thread
    scheduler_thread = Thread(target=start_scheduler)
    scheduler_thread.start()

    # Run the Streamlit app
    main()
