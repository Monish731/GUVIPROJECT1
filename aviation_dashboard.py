import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Flight Analytics Dashboard",
    page_icon="✈️",
    layout="wide"
)

# ----------------------------------
# DATABASE
# ----------------------------------

conn = sqlite3.connect("aviation.db")

airport_df = pd.read_sql_query(
    "SELECT * FROM airport",
    conn
)

flights_df = pd.read_sql_query(
    "SELECT * FROM flights",
    conn
)

aircraft_df = pd.read_sql_query(
    "SELECT * FROM aircraft",
    conn
)

delays_df = pd.read_sql_query(
    "SELECT * FROM airport_delays",
    conn
)

# ----------------------------------
# SIDEBAR
# ----------------------------------

st.sidebar.title("✈️ Flight Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Flights",
        "Airport Details",
        "Delay Analysis",
        "Route Leaderboard",
        "Raw Tables"
    ]
)

# ==================================
# DASHBOARD
# ==================================

if page == "Dashboard":

    st.title("✈️ Flight Analytics Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Airports",
        len(airport_df)
    )

    c2.metric(
        "Total Flights",
        len(flights_df)
    )

    c3.metric(
        "Total Aircraft",
        len(aircraft_df)
    )

    c4.metric(
        "Delay Records",
        len(delays_df)
    )

    st.divider()

    st.subheader("Top Airlines")

    airline_counts = (
        flights_df["airline"]
        .value_counts()
        .reset_index()
    )

    airline_counts.columns = [
        "Airline",
        "Flights"
    ]

    fig = px.bar(
        airline_counts.head(10),
        x="Airline",
        y="Flights",
        title="Top 10 Airlines"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================
# FLIGHTS PAGE
# ==================================

elif page == "Flights":

    st.title("🔍 Search Flights")

    airline = st.selectbox(
        "Airline",
        ["All"] +
        sorted(
            flights_df["airline"]
            .dropna()
            .unique()
        )
    )

    status = st.selectbox(
        "Status",
        ["All"] +
        sorted(
            flights_df["status"]
            .dropna()
            .unique()
        )
    )

    origin = st.selectbox(
        "Origin Airport",
        ["All"] +
        sorted(
            flights_df["origin_airport"]
            .dropna()
            .unique()
        )
    )

    filtered = flights_df.copy()

    if airline != "All":
        filtered = filtered[
            filtered["airline"] == airline
        ]

    if status != "All":
        filtered = filtered[
            filtered["status"] == status
        ]

    if origin != "All":
        filtered = filtered[
            filtered["origin_airport"] == origin
        ]

    st.write(
        f"Flights Found: {len(filtered)}"
    )

    st.dataframe(filtered)

# ==================================
# AIRPORT DETAILS
# ==================================

elif page == "Airport Details":

    st.title("🛫 Airport Details Viewer")

    airport = st.selectbox(
        "Choose Airport",
        sorted(
            airport_df["iata_code"]
        )
    )

    details = airport_df[
        airport_df["iata_code"] == airport
    ]

    st.subheader("Airport Information")

    st.dataframe(details)

    linked = flights_df[
        (flights_df["origin_airport"] == airport)
        |
        (flights_df["destination_airport"] == airport)
    ]

    st.subheader(
        f"Flights Linked To {airport}"
    )

    st.dataframe(linked)

# ==================================
# DELAY ANALYSIS
# ==================================

elif page == "Delay Analysis":

    st.title("⏳ Delay Analysis")

    st.dataframe(delays_df)

    if len(delays_df) > 0:

        fig = px.bar(
            delays_df,
            x="airport_iata",
            y="delayed_flights",
            title="Delayed Flights"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = px.pie(
            delays_df,
            names="airport_iata",
            values="delayed_flights",
            title="Delay Share"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ==================================
# ROUTE LEADERBOARD
# ==================================

elif page == "Route Leaderboard":

    st.title("🔥 Route Leaderboard")

    routes = (
        flights_df
        .groupby(
            [
                "origin_airport",
                "destination_airport"
            ]
        )
        .size()
        .reset_index(name="Flights")
        .sort_values(
            "Flights",
            ascending=False
        )
    )

    st.subheader("Top 10 Routes")

    st.dataframe(
        routes.head(10)
    )

    fig = px.bar(
        routes.head(10),
        x="origin_airport",
        y="Flights",
        color="destination_airport",
        title="Busiest Routes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================
# RAW TABLES
# ==================================

elif page == "Raw Tables":

    st.title("📄 Database Tables")

    with st.expander(
        "Airport Table"
    ):
        st.dataframe(
            airport_df
        )

    with st.expander(
        "Flights Table"
    ):
        st.dataframe(
            flights_df
        )

    with st.expander(
        "Aircraft Table"
    ):
        st.dataframe(
            aircraft_df
        )

    with st.expander(
        "Airport Delays Table"
    ):
        st.dataframe(
            delays_df
        )

conn.close()