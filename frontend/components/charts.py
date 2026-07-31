import pandas as pd
import streamlit as st


# ==========================================================
# Bar Chart
# ==========================================================

def bar_chart(
    data,
    x,
    y,
    title="Bar Chart"
):
    """
    Display a bar chart.
    """

    st.subheader(title)

    if not data:
        st.info("No data available.")
        return

    df = pd.DataFrame(data)

    st.bar_chart(
        data=df.set_index(x)[y],
        use_container_width=True
    )


# ==========================================================
# Line Chart
# ==========================================================

def line_chart(
    data,
    x,
    y,
    title="Line Chart"
):
    """
    Display a line chart.
    """

    st.subheader(title)

    if not data:
        st.info("No data available.")
        return

    df = pd.DataFrame(data)

    st.line_chart(
        data=df.set_index(x)[y],
        use_container_width=True
    )


# ==========================================================
# Area Chart
# ==========================================================

def area_chart(
    data,
    x,
    y,
    title="Area Chart"
):
    """
    Display an area chart.
    """

    st.subheader(title)

    if not data:
        st.info("No data available.")
        return

    df = pd.DataFrame(data)

    st.area_chart(
        data=df.set_index(x)[y],
        use_container_width=True
    )


# ==========================================================
# Pie Chart
# ==========================================================

def pie_chart(
    data,
    labels,
    values,
    title="Pie Chart"
):
    """
    Display a pie chart using Plotly.
    """

    st.subheader(title)

    if not data:
        st.info("No data available.")
        return

    try:
        import plotly.express as px

        df = pd.DataFrame(data)

        fig = px.pie(
            df,
            names=labels,
            values=values,
            hole=0.35
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except ImportError:
        st.warning("Plotly is not installed.")


# ==========================================================
# Histogram
# ==========================================================

def histogram(
    data,
    column,
    title="Histogram"
):
    """
    Display a histogram.
    """

    st.subheader(title)

    if not data:
        st.info("No data available.")
        return

    try:
        import plotly.express as px

        df = pd.DataFrame(data)

        fig = px.histogram(
            df,
            x=column,
            nbins=10
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except ImportError:
        st.warning("Plotly is not installed.")


# ==========================================================
# Dashboard Metrics
# ==========================================================

def dashboard_metrics(metrics):
    """
    Display dashboard metric cards.
    """

    if not metrics:
        return

    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):

        with col:

            st.metric(
                metric["title"],
                metric["value"],
                metric.get("delta")
            )


# ==========================================================
# Empty Chart
# ==========================================================

def empty_chart(message="No chart data available."):
    st.info(message)
