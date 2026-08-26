from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mapping India's Innovation Economy",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "startups_clean.csv"
)

HOTSPOT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "hotspot_scores.csv"
)

FOUNDER_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "founder_data.csv"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.7;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .insight-box {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(128,128,128,0.10);
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    if "year" in df.columns:
        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

    if "funding_crore" in df.columns:
        df["funding_crore"] = pd.to_numeric(
            df["funding_crore"],
            errors="coerce"
        ).fillna(0)

    return df


@st.cache_data
def load_hotspots():

    if not HOTSPOT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(HOTSPOT_FILE)


@st.cache_data
def load_founders():

    if not FOUNDER_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(FOUNDER_FILE)


df = load_data()
hotspots = load_hotspots()
founders = load_founders()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.error(
        """
        Dataset not found.

        Please run:

        1. `python src/02_clean_data.py`
        2. `python src/03_analysis.py`
        3. `python src/04_hotspot_score.py`

        Then restart Streamlit.
        """
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🇮🇳 Mapping India\'s Innovation Economy</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Where founders build. Where startups grow. Where capital flows.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🎛️ Explore the Ecosystem")

years = sorted(
    df["year"].dropna().astype(int).unique()
)

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

cities = sorted(
    df["city"].dropna().unique()
)

selected_cities = st.sidebar.multiselect(
    "City",
    cities,
    default=[]
)

industries = sorted(
    df["industry"].dropna().unique()
)

selected_industries = st.sidebar.multiselect(
    "Industry",
    industries,
    default=[]
)

rounds = sorted(
    df["funding_round"].dropna().unique()
)

selected_rounds = st.sidebar.multiselect(
    "Funding Round",
    rounds,
    default=[]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()

if selected_years:
    filtered = filtered[
        filtered["year"].isin(selected_years)
    ]

if selected_cities:
    filtered = filtered[
        filtered["city"].isin(selected_cities)
    ]

if selected_industries:
    filtered = filtered[
        filtered["industry"].isin(selected_industries)
    ]

if selected_rounds:
    filtered = filtered[
        filtered["funding_round"].isin(selected_rounds)
    ]


# ============================================================
# KPI CARDS
# ============================================================

total_startups = filtered["startup_name"].nunique()

total_funding = filtered["funding_crore"].sum()

total_cities = filtered["city"].nunique()

total_industries = filtered["industry"].nunique()

total_investors = filtered["investors"].nunique()


c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "🚀 Startups",
    f"{total_startups:,}"
)

c2.metric(
    "💰 Funding",
    f"₹{total_funding:,.0f} Cr"
)

c3.metric(
    "📍 Cities",
    f"{total_cities:,}"
)

c4.metric(
    "🏭 Industries",
    f"{total_industries:,}"
)

c5.metric(
    "🤝 Investors",
    f"{total_investors:,}"
)


# ============================================================
# TABS
# ============================================================

overview_tab, hotspot_tab, explorer_tab, founder_tab = st.tabs(
    [
        "🏠 Ecosystem Overview",
        "🏆 Innovation Hotspots",
        "🔍 Startup Explorer",
        "👤 Founder Journey"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    st.markdown(
        '<div class="section-title">📍 Where is innovation happening?</div>',
        unsafe_allow_html=True
    )

    city_data = (
        filtered.dropna(subset=["city"])
        .groupby("city")
        .agg(
            startups=("startup_name", "nunique"),
            funding=("funding_crore", "sum")
        )
        .reset_index()
    )

    city_data["funding"] = city_data["funding"].round(2)

    fig = px.bar(
        city_data.sort_values(
            "startups",
            ascending=False
        ).head(15),
        x="startups",
        y="city",
        orientation="h",
        title="Top Startup Cities"
    )

    fig.update_layout(
        height=550,
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ========================================================
    # FUNDING BY CITY + INDUSTRY
    # ========================================================

    st.markdown(
        '<div class="section-title">💰 Where is the money going?</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        funding_city = (
            filtered.dropna(subset=["city"])
            .groupby("city")["funding_crore"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(12)
            .reset_index()
        )

        fig_city = px.bar(
            funding_city,
            x="funding_crore",
            y="city",
            orientation="h",
            title="Funding by City",
            labels={
                "funding_crore": "Funding (₹ Crore)"
            }
        )

        fig_city.update_layout(
            height=500,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig_city,
            use_container_width=True
        )

    with col2:

        industry = (
            filtered.dropna(subset=["industry"])
            .groupby("industry")["funding_crore"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(12)
            .reset_index()
        )

        fig_industry = px.bar(
            industry,
            x="funding_crore",
            y="industry",
            orientation="h",
            title="Funding by Industry",
            labels={
                "funding_crore": "Funding (₹ Crore)"
            }
        )

        fig_industry.update_layout(
            height=500,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig_industry,
            use_container_width=True
        )


    # ========================================================
    # CITY × INDUSTRY
    # ========================================================

    st.markdown(
        '<div class="section-title">🔥 City × Industry</div>',
        unsafe_allow_html=True
    )

    heatmap_data = (
        filtered.dropna(
            subset=["city", "industry"]
        )
        .groupby(
            ["city", "industry"]
        )["funding_crore"]
        .sum()
        .reset_index()
    )

    top_cities = (
        filtered.groupby("city")["funding_crore"]
        .sum()
        .nlargest(10)
        .index
    )

    top_industries = (
        filtered.groupby("industry")["funding_crore"]
        .sum()
        .nlargest(10)
        .index
    )

    heatmap_data = heatmap_data[
        heatmap_data["city"].isin(top_cities)
        & heatmap_data["industry"].isin(top_industries)
    ]

    pivot = heatmap_data.pivot(
        index="city",
        columns="industry",
        values="funding_crore"
    ).fillna(0)

    fig_heat = px.imshow(
        pivot,
        aspect="auto",
        title="Funding Heatmap: City × Industry",
        labels={
            "color": "Funding (₹ Cr)"
        }
    )

    fig_heat.update_layout(
        height=550
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True
    )


    # ========================================================
    # YEARLY EVOLUTION
    # ========================================================

    st.markdown(
        '<div class="section-title">📈 How has the ecosystem evolved?</div>',
        unsafe_allow_html=True
    )

    yearly = (
        filtered.dropna(subset=["year"])
        .groupby("year")
        .agg(
            startups=("startup_name", "nunique"),
            funding=("funding_crore", "sum")
        )
        .reset_index()
    )

    fig_year = go.Figure()

    fig_year.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["startups"],
            mode="lines+markers",
            name="Startups"
        )
    )

    fig_year.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["funding"],
            mode="lines+markers",
            name="Funding (₹ Cr)",
            yaxis="y2"
        )
    )

    fig_year.update_layout(
        title="Startup Ecosystem Evolution",
        xaxis_title="Year",
        yaxis=dict(
            title="Number of Startups"
        ),
        yaxis2=dict(
            title="Funding (₹ Cr)",
            overlaying="y",
            side="right"
        ),
        height=500
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )


    # ========================================================
    # SCATTER
    # ========================================================

    st.markdown(
        '<div class="section-title">⚖️ Startup Activity vs Capital</div>',
        unsafe_allow_html=True
    )

    scatter = (
        filtered.dropna(subset=["city"])
        .groupby("city")
        .agg(
            startups=("startup_name", "nunique"),
            funding=("funding_crore", "sum")
        )
        .reset_index()
    )

    fig_scatter = px.scatter(
        scatter,
        x="startups",
        y="funding",
        text="city",
        size="funding",
        hover_name="city",
        title="Startup Count vs Total Funding",
        labels={
            "startups": "Number of Startups",
            "funding": "Funding (₹ Crore)"
        }
    )

    fig_scatter.update_traces(
        textposition="top center"
    )

    fig_scatter.update_layout(
        height=600
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


    # ========================================================
    # FUNDING ROUND
    # ========================================================

    st.markdown(
        '<div class="section-title">💵 Capital Journey</div>',
        unsafe_allow_html=True
    )

    round_data = (
        filtered.dropna(subset=["funding_round"])
        .groupby("funding_round")
        .agg(
            startups=("startup_name", "nunique"),
            funding=("funding_crore", "sum")
        )
        .reset_index()
        .sort_values(
            "funding",
            ascending=False
        )
    )

    fig_round = px.bar(
        round_data,
        x="funding_round",
        y="funding",
        title="Funding by Investment Round",
        labels={
            "funding": "Funding (₹ Crore)",
            "funding_round": "Funding Round"
        }
    )

    st.plotly_chart(
        fig_round,
        use_container_width=True
    )


# ============================================================
# HOTSPOT TAB
# ============================================================

with hotspot_tab:

    st.title("🏆 India's Innovation Hotspots")

    if hotspots.empty:

        st.warning(
            "Run 04_hotspot_score.py first."
        )

    else:

        st.markdown(
            """
            The **Innovation Hotspot Score** combines startup concentration,
            funding strength, industry diversity, investor diversity and
            ecosystem growth.
            """
        )

        top_hotspots = hotspots.head(15)

        fig_hotspot = px.bar(
            top_hotspots.sort_values(
                "hotspot_score"
            ),
            x="hotspot_score",
            y="city",
            orientation="h",
            text="hotspot_score",
            title="Top Innovation Hotspots"
        )

        fig_hotspot.update_layout(
            height=600,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig_hotspot,
            use_container_width=True
        )

        st.subheader("🏅 City Rankings")

        display_columns = [
            "rank",
            "city",
            "startup_count",
            "funding_crore",
            "industry_count",
            "investor_count",
            "hotspot_score"
        ]

        available = [
            c for c in display_columns
            if c in hotspots.columns
        ]

        st.dataframe(
            hotspots[available],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STARTUP EXPLORER
# ============================================================

with explorer_tab:

    st.title("🔍 Explore a Startup")

    startup_names = sorted(
        filtered["startup_name"]
        .dropna()
        .unique()
    )

    selected_startup = st.selectbox(
        "Choose a startup",
        startup_names
    )

    startup_data = filtered[
        filtered["startup_name"] == selected_startup
    ].copy()

    if not startup_data.empty:

        row = startup_data.iloc[0]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Industry",
            str(row.get("industry", "N/A"))
        )

        c2.metric(
            "City",
            str(row.get("city", "N/A"))
        )

        c3.metric(
            "Funding",
            f"₹{startup_data['funding_crore'].sum():,.2f} Cr"
        )

        st.subheader("📋 Startup Details")

        details = {
            "Startup": selected_startup,
            "Industry": row.get("industry", "N/A"),
            "City": row.get("city", "N/A"),
            "Funding Round": row.get("funding_round", "N/A"),
            "Investors": row.get("investors", "N/A")
        }

        st.table(
            pd.DataFrame(
                details.items(),
                columns=["Attribute", "Value"]
            )
        )

        if "year" in startup_data.columns:

            timeline = (
                startup_data.dropna(subset=["year"])
                .groupby("year")["funding_crore"]
                .sum()
                .reset_index()
            )

            if not timeline.empty:

                fig = px.line(
                    timeline,
                    x="year",
                    y="funding_crore",
                    markers=True,
                    title=f"{selected_startup} — Funding Timeline",
                    labels={
                        "year": "Year",
                        "funding_crore": "Funding (₹ Cr)"
                    }
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


# ============================================================
# FOUNDER JOURNEY
# ============================================================

with founder_tab:

    st.title("👤 Founder Journey")

    st.markdown(
        """
        ### From idea to investment

        This section adds the **human story** behind the startup ecosystem.

        Select a startup to explore its founder, origin, funding journey
        and growth story.
        """
    )

    if founders.empty:

        st.info(
            """
            Founder data has not been added yet.

            Create:

            `data/processed/founder_data.csv`

            using the template provided below.
            """
        )

    else:

        founder_startups = sorted(
            founders["startup_name"]
            .dropna()
            .unique()
        )

        selected_founder_startup = st.selectbox(
            "Select startup",
            founder_startups,
            key="founder_startup"
        )

        founder_rows = founders[
            founders["startup_name"]
            == selected_founder_startup
        ].copy()

        if not founder_rows.empty:

            founder_row = founder_rows.iloc[0]

            st.subheader(
                f"🚀 {selected_founder_startup}"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Founder",
                str(
                    founder_row.get(
                        "founder",
                        "N/A"
                    )
                )
            )

            col2.metric(
                "Founded",
                str(
                    founder_row.get(
                        "founded_year",
                        "N/A"
                    )
                )
            )

            col3.metric(
                "City",
                str(
                    founder_row.get(
                        "city",
                        "N/A"
                    )
                )
            )

            st.markdown("### 🛣️ Founder Journey")

            journey_columns = [
                "founder",
                "idea",
                "founded_year",
                "city",
                "industry",
                "first_funding_year",
                "first_funding_amount",
                "major_investors",
                "growth_story",
                "current_status"
            ]

            available_columns = [
                c for c in journey_columns
                if c in founder_rows.columns
            ]

            for column in available_columns:

                value = founder_row[column]

                if pd.notna(value):

                    label = column.replace(
                        "_",
                        " "
                    ).title()

                    st.markdown(
                        f"**{label}:** {value}"
                    )

            # Timeline visualization
            timeline_events = []

            if pd.notna(
                founder_row.get(
                    "founded_year",
                    np.nan
                )
            ):
                timeline_events.append(
                    (
                        int(founder_row["founded_year"]),
                        "Startup Founded"
                    )
                )

            if pd.notna(
                founder_row.get(
                    "first_funding_year",
                    np.nan
                )
            ):
                timeline_events.append(
                    (
                        int(
                            founder_row[
                                "first_funding_year"
                            ]
                        ),
                        "First Funding"
                    )
                )

            if timeline_events:

                timeline_df = pd.DataFrame(
                    timeline_events,
                    columns=[
                        "year",
                        "event"
                    ]
                )

                fig = px.scatter(
                    timeline_df,
                    x="year",
                    y="event",
                    text="event",
                    title="Founder / Startup Journey"
                )

                fig.update_traces(
                    marker_size=18
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )