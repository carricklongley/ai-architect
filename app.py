import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import base64

# Function to generate a download link for the report
def get_download_link(report_content, filename, text):
    b64 = base64.b64encode(report_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Function to fetch URL content and parse text
def fetch_and_parse_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.RequestException as e:
        st.error(f"Error fetching {url}: {e}")
        return None

# Updated GPT-4 function
def get_gpt4_recommendations(url, keyword, idea, text_content):
    prompt = f"URL: {url}\nKeyword: {keyword}\nSuggestion: {idea}\n\nBased on the content and the suggestion, what specific changes should be made to improve SEO? Provide examples when possible"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in GPT-4 API call: {e}")
        return "No recommendation could be generated."

# Centering the title and logo using HTML and CSS
st.markdown("""
    <style>
    .centered {
        text-align: center;
    }
    </style>
    <div class="centered">
        <h1>AI SEO Architect</h1>
        <img src="https://onedrive.live.com/embed?resid=3ED8F1B295D8A30%21263321&authkey=%21AEak1JovybPJPaw&width=320&height=320" alt="App logo" style="width:320px;height:320px;">
        <p>
    </div>
    """, unsafe_allow_html=True)

# Description of the app's functionality
st.write("""
    This app generates detailed SEO recommendations using GPT-4. 
    It processes CSV files exported from Semrush. 
    Please ensure your CSV file includes the following columns:
    - `Priority`: Indicates the importance or priority of the recommendation.
    - `Url`: The specific URL for which the recommendation is made.
    - `Keyword`: The target keyword for the SEO recommendation.
    - `Idea`: A brief description or idea for SEO improvement.
""")
OPENAI_API_KEY = st.text_input("Enter your OpenAI API Key", type="password")

# Initialize an empty string to store the report content
report_content = ""

# Initialize an empty string to store the report content in HTML format
html_report_content = "<html><head><title>AI SEO Architect Report</title></head><body>"

# File uploader
# Check if the API key is entered before allowing file upload
if OPENAI_API_KEY:
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")


    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:", data)

        # Process each URL
        for url in data['Url'].unique():
            st.write(f"## Recommendations for URL: {url}")
            # Fetch and parse URL content
            text_content = fetch_and_parse_url(url)
            if text_content:
                st.text_area("URL Text Content (truncated)", text_content[:500], height=100, key=f"text_{url}")

                # Generate and display recommendations for each idea
                for _, row in data[data['Url'] == url].iterrows():
                    recommendation = get_gpt4_recommendations(url, row['Keyword'], row['Idea'], text_content)
                    report_section = f"### Recommendation for '{row['Idea']}'\n{recommendation}\n\n---\n\n"
                    report_content += report_section
                    # Display the recommendation in the app
                    st.write(report_section)
    
    # Place this at the end of your Streamlit app
    markdown_download_link = get_download_link(report_content, "AI_SEO_Report.md", "Download Report as Markdown")
    st.markdown(markdown_download_link, unsafe_allow_html=True)

else:
    st.warning("Please enter your OpenAI API Key to proceed.")
    

            
