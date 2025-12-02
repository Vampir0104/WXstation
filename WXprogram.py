import requests
import streamlit as st
import time


def stinit():
    if "url" not in st.session_state:
        st.session_state.url = []
    if "input" not in st.session_state:
        st.session_state.input = ""
    if "taf" not in st.session_state:
        st.session_state.taf = "No"
    if "report" not in st.session_state:
        st.session_state.report = []
    if "toggle_input" not in st.session_state:
        st.session_state.toggle_input = "No"  # Default to "No"

class Station:
    def __init__(self):
        self.station = []
        self.url = []

    def setStation(self):
        self.station = st.session_state.input
        self.station = [station.strip() for station in self.station.split(',')]
        self.url = [
            f'https://aviationweather.gov/api/data/taf?ids={station}&format=raw&metar=true&time=valid'
            for station in self.station
        ]

    def setURL(self):
        st.session_state.url = self.url

class Report:
    def __init__(self):
        self.url = []
        self.report = []
        self.metar_data = ""
        self.taf = "No"
        self.taf_data = []

    def report_setter(self):
        self.url = st.session_state.url
        self.taf = st.session_state.taf

    def getreport(self):
        self.report = []
        for url in self.url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                self.metar_data = response.text

                if not self.metar_data.strip():
                    self.report.append(f"Failed to retrieve data for: {url}")
                    self.report.append("")
                else:
                    lines = self.metar_data.split('\n')
                    if len(lines) > 1:
                        self.report.append("METAR Data:")
                        self.report.append(lines[0])
                        if self.taf == "Yes":
                            self.report.append("TAF Data:")
                            self.report.extend(lines[1:])
                    else:
                        self.report.append("Unexpected response format.")
            except requests.exceptions.RequestException as e:
                self.report.append(f"An error occurred: {e}")
        st.session_state.report = self.report

class Timer:
    def __init__(self):
        self.time = 60
        self.count = 0

    def countdown(self):
        self.count = self.time
        while st.session_state.timer == True:
            while self.count > 0:
                self.count = self.count - 1
                time.sleep(1)
            st.experimental_rerun()



def wxpage():
    # Ensure session state variables are initialized
    stinit()

    st.markdown(
        """
        <style>
        .dataframe th, .dataframe td {
            max-width: 1200px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        input = st.text_input("Enter stations here", key="sidebar_input")

        # Slider for toggle (Yes = True, No = False)
        toggle_input = st.selectbox(
            "Tafs?",
            options=["No", "Yes"],
            index=0 if st.session_state.get("toggle_input", "No") == "No" else 1,  # Default to "No"
            key="slider_toggle",
        )

        # Map "Yes" to True and "No" to False
        toggle_bool = toggle_input

        if st.sidebar.button("Set Station(s)"):
            st.session_state.input = input
            st.session_state.toggle_input = toggle_input
            st.session_state.taf = toggle_bool  # Set TAF flag based on toggle
            station.setStation()
            station.setURL()
            report.report_setter()
            report.getreport()



    # Safeguard: Always check if the session state variable exists before accessing
    if st.session_state.report:
        for line in st.session_state.report:
            if "METAR Data:" in line or "TAF Data:" in line:
                st.markdown(f"### {line}")  # Use header style for section titles
            else:
                st.write(line)  # Use regular text for data
    else:
        st.write("No data to display yet.") 

if __name__ == "__main__":
    station = Station()
    report = Report()
    timer = Timer()
    wxpage()

