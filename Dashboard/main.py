import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Bike Sharing Analysis Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1976D2;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1976D2;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
</style>
""", unsafe_allow_html=True)

# App title and author info
st.markdown("<h1 class='main-header'>🚲 Bike Sharing Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center;">
    <p><b>Nama:</b> Hafiyan Al Muqaffi Umary | <b>Email:</b> jhodywiraputra@student.ub.ac.id | <b>ID Dicoding:</b> MC006D5Y1369</p>
</div>
""", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("all_data_cleaned.csv")
        df['dteday'] = pd.to_datetime(df['dteday'])
        return df
    except FileNotFoundError:
        # If the cleaned file is not found, use sample data for demonstration
        st.warning("File 'all_data_cleaned.csv' not found. Using sample data for demonstration.")
        
        # Generate sample data
        n_samples = 10000
        date_range = pd.date_range(start='2011-01-01', periods=365*2)
        
        data = {
            'dteday': np.random.choice(date_range, n_samples),
            'hr': np.random.randint(0, 24, n_samples),
            'season': np.random.randint(1, 5, n_samples),
            'workingday': np.random.randint(0, 2, n_samples),
            'weathersit': np.random.randint(1, 5, n_samples),
            'temp': np.random.uniform(0, 1, n_samples),
            'atemp': np.random.uniform(0, 1, n_samples),
            'hum': np.random.uniform(0, 1, n_samples),
            'windspeed': np.random.uniform(0, 1, n_samples),
            'cnt': np.random.randint(1, 1000, n_samples)
        }
        df = pd.DataFrame(data)
        return df

# Load data
df = load_data()

# Sidebar
st.sidebar.markdown("## 📊 Dashboard Controls")
st.sidebar.markdown("---")

# Date range filter
min_date = df['dteday'].min().date()
max_date = df['dteday'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['dteday'].dt.date >= start_date) & (df['dteday'].dt.date <= end_date)]
else:
    filtered_df = df

# Season filter
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
seasons = st.sidebar.multiselect(
    "Select Seasons",
    options=list(season_mapping.keys()),
    default=list(season_mapping.keys()),
    format_func=lambda x: season_mapping[x]
)

if seasons:
    filtered_df = filtered_df[filtered_df['season'].isin(seasons)]

# Weather situation filter
weather_mapping = {
    1: "Clear/Few clouds",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Thunderstorm"
}
weather_situations = st.sidebar.multiselect(
    "Select Weather Conditions",
    options=list(weather_mapping.keys()),
    default=list(weather_mapping.keys()),
    format_func=lambda x: weather_mapping[x]
)

if weather_situations:
    filtered_df = filtered_df[filtered_df['weathersit'].isin(weather_situations)]

# Display dataset info
st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Information")
st.sidebar.info(f"""
- Total Records: {len(df)}
- Date Range: {min_date} to {max_date}
- Filtered Records: {len(filtered_df)}
""")

# Display analysis questions
st.sidebar.markdown("---")
st.sidebar.markdown("### Analysis Questions")
st.sidebar.markdown("""
1. How does the bike rental pattern vary throughout the day, and is there a difference between weekdays and weekends?

2. How does weather affect bike rentals?
""")

# Main dashboard content
tab1, tab2, tab3 = st.tabs(["📈 Overview", "⏱️ Time Analysis", "🌦️ Weather Impact"])

with tab1:
    st.markdown("<h2 class='sub-header'>Dashboard Overview</h2>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Rentals",
            f"{filtered_df['cnt'].sum():,}",
            delta=f"{filtered_df['cnt'].sum() / df['cnt'].sum() * 100:.1f}% of total"
        )
    
    with col2:
        avg_daily = filtered_df.groupby('dteday')['cnt'].sum().mean()
        st.metric(
            "Avg. Daily Rentals",
            f"{int(avg_daily):,}"
        )
    
    with col3:
        peak_hour = filtered_df.groupby('hr')['cnt'].mean().idxmax()
        peak_hour_value = filtered_df.groupby('hr')['cnt'].mean().max()
        st.metric(
            "Peak Hour",
            f"{peak_hour}:00",
            f"Avg: {int(peak_hour_value)} rentals"
        )
    
    with col4:
        weekend_avg = filtered_df[filtered_df['workingday'] == 0].groupby('dteday')['cnt'].sum().mean()
        weekday_avg = filtered_df[filtered_df['workingday'] == 1].groupby('dteday')['cnt'].sum().mean()
        st.metric(
            "Weekend vs Weekday",
            f"{int(weekend_avg):,} vs {int(weekday_avg):,}",
            f"{(weekend_avg/weekday_avg - 1) * 100:.1f}% difference"
        )
    
    # Monthly trends
    st.markdown("<h3 class='sub-header'>Monthly Rental Trends</h3>", unsafe_allow_html=True)
    
    # Extract month and year
    filtered_df['month'] = filtered_df['dteday'].dt.month
    filtered_df['year'] = filtered_df['dteday'].dt.year
    filtered_df['month_year'] = filtered_df['dteday'].dt.strftime('%b %Y')
    
    monthly_data = filtered_df.groupby(['year', 'month', 'month_year'])['cnt'].sum().reset_index()
    monthly_data = monthly_data.sort_values(['year', 'month'])
    
    fig_monthly = px.line(
        monthly_data,
        x='month_year',
        y='cnt',
        markers=True,
        labels={'cnt': 'Total Rentals', 'month_year': 'Month'},
        title='Monthly Bike Rental Trends'
    )
    fig_monthly.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Rentals',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of rentals
        st.markdown("<h3 class='sub-header'>Rental Distribution</h3>", unsafe_allow_html=True)
        fig_dist = px.histogram(
            filtered_df,
            x='cnt',
            nbins=30,
            labels={'cnt': 'Number of Rentals'},
            title='Distribution of Hourly Bike Rentals'
        )
        fig_dist.update_layout(
            bargap=0.1,
            height=350,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Correlation heatmap
        st.markdown("<h3 class='sub-header'>Factor Correlation</h3>", unsafe_allow_html=True)
        corr_cols = ['temp', 'atemp', 'hum', 'windspeed', 'cnt']
        corr_matrix = filtered_df[corr_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title='Correlation Between Factors and Rentals'
        )
        fig_corr.update_layout(
            height=350,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Insight box
    st.markdown(
    """
    <style>
        .key-insights {
            background: linear-gradient(135deg, #2563eb, #1e40af); /* Gradasi biru */
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        .conclusions {
            background: linear-gradient(135deg, #4b5563, #1f2937); /* Gradasi abu-abu gelap */
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        .business-recommendations {
            background: linear-gradient(135deg, #15803d, #065f46); /* Gradasi hijau */
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        h3 {
            font-size: 22px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        ul {
            padding-left: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with tab2:
    st.markdown("<h2 class='sub-header'>Hourly Rental Patterns</h2>", unsafe_allow_html=True)

    # Hourly patterns by working day
    hourly_data = filtered_df.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()

    fig_hourly = px.line(
        hourly_data,
        x='hr',
        y='cnt',
        color='workingday',
        color_discrete_map={0: '#4CAF50', 1: '#2196F3'},
        labels={'cnt': 'Average Rentals', 'hr': 'Hour of Day', 'workingday': 'Working Day'},
        title='Hourly Bike Rental Patterns: Weekdays vs. Weekends'
    )

    fig_hourly.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            title='Hour of Day'
        ),
        yaxis_title='Average Rentals',
        legend_title='Day Type',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig_hourly.update_traces(
        line=dict(width=3),
        mode='lines+markers'
    )

    # Update legend labels
    newnames = {'0': 'Weekend', '1': 'Weekday'}
    fig_hourly.for_each_trace(lambda t: t.update(name=newnames[t.name]))

    st.plotly_chart(fig_hourly, use_container_width=True)

    st.markdown(
    """
    <style>
        .insight-box {
            background: linear-gradient(135deg, #9333ea, #6b21a8); /* Gradasi ungu */
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }

        .insight-box h4 {
            font-size: 20px;
            margin-bottom: 10px;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .insight-box ul {
            padding-left: 20px;
        }

        .insight-box li {
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
    """
    <div class="insight-box">
        <h4>Key Observations</h4>
        <ul>
            <li><b>Weekdays:</b> Show two distinct peaks - morning (7-9 AM) and evening (5-7 PM), corresponding to commuting hours.</li>
            <li><b>Weekends:</b> Have a more even distribution throughout the day with a gradual increase from morning to afternoon (10 AM-4 PM), suggesting recreational use.</li>
            <li>The lowest usage for both weekdays and weekends occurs during early morning hours (2-5 AM).</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
    )

    
    # Hourly patterns by season
    st.markdown("<h3 class='sub-header'>Seasonal Hourly Patterns</h3>", unsafe_allow_html=True)
    
    season_data = filtered_df.groupby(['hr', 'season'])['cnt'].mean().reset_index()
    
    fig_season = px.line(
        season_data,
        x='hr',
        y='cnt',
        color='season',
        color_discrete_map={1: '#4CAF50', 2: '#FF9800', 3: '#F44336', 4: '#2196F3'},
        labels={'cnt': 'Average Rentals', 'hr': 'Hour of Day', 'season': 'Season'},
        title='Hourly Bike Rental Patterns Across Seasons'
    )
    
    fig_season.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            title='Hour of Day'
        ),
        yaxis_title='Average Rentals',
        legend_title='Season',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig_season.update_traces(
        line=dict(width=2),
        mode='lines+markers'
    )
    
    # Update legend labels
    season_names = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    fig_season.for_each_trace(lambda t: t.update(name=season_names[int(t.name)]))
    
    st.plotly_chart(fig_season, use_container_width=True)
    
    # Interactive heatmap
    st.markdown("<h3 class='sub-header'>Hourly Rentals Heatmap</h3>", unsafe_allow_html=True)
    
    # Prepare data for heatmap - create day of week column
    filtered_df['dow'] = filtered_df['dteday'].dt.dayofweek
    heatmap_data = filtered_df.groupby(['dow', 'hr'])['cnt'].mean().reset_index()
    
    # Create a pivot table
    heatmap_pivot = heatmap_data.pivot(index='dow', columns='hr', values='cnt')
    
    # Create custom colorscale
    colorscale = [
        [0, '#E3F2FD'],
        [0.2, '#90CAF9'],
        [0.4, '#42A5F5'],
        [0.6, '#1E88E5'],
        [0.8, '#1565C0'],
        [1, '#0D47A1']
    ]
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        color_continuous_scale=colorscale,
        labels=dict(x="Hour of Day", y="Day of Week", color="Avg. Rentals"),
        title="Weekly Rental Pattern Heatmap"
    )
    
    fig_heatmap.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            title='Hour of Day'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            title='Day of Week'
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=450
    )
    
    fig_heatmap.update_traces(hoverongaps=False)
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.markdown("<h2 class='sub-header'>Weather Impact Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Impact of weather situation
        weather_data = filtered_df.groupby('weathersit')['cnt'].mean().reset_index()
        weather_data['weathersit'] = weather_data['weathersit'].map(weather_mapping)
        
        fig_weather = px.bar(
            weather_data,
            x='weathersit',
            y='cnt',
            color='cnt',
            color_continuous_scale='Blues',
            labels={'cnt': 'Average Rentals', 'weathersit': 'Weather Condition'},
            title='Impact of Weather Conditions on Bike Rentals'
        )
        
        fig_weather.update_layout(
            xaxis_title='Weather Condition',
            yaxis_title='Average Rentals',
            coloraxis_showscale=False,
            margin=dict(l=40, r=40, t=60, b=40),
            height=400
        )
        
        st.plotly_chart(fig_weather, use_container_width=True)
    
    with col2:
        # Impact of temperature
        fig_temp = px.scatter(
            filtered_df.sample(1000) if len(filtered_df) > 1000 else filtered_df,
            x='temp',
            y='cnt',
            color='temp',
            color_continuous_scale='Viridis',
            trendline="ols",
            labels={'cnt': 'Number of Rentals', 'temp': 'Temperature (Normalized)'},
            title='Relationship Between Temperature and Bike Rentals'
        )
        
        fig_temp.update_layout(
            xaxis_title='Temperature (Normalized)',
            yaxis_title='Number of Rentals',
            margin=dict(l=40, r=40, t=60, b=40),
            height=400
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Environmental factors impact
    st.markdown("<h3 class='sub-header'>Environmental Factors Impact</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Impact of humidity
        fig_hum = px.scatter(
            filtered_df.sample(1000) if len(filtered_df) > 1000 else filtered_df,
            x='hum',
            y='cnt',
            color='hum',
            color_continuous_scale='Blues',
            trendline="ols",
            labels={'cnt': 'Number of Rentals', 'hum': 'Humidity (Normalized)'},
            title='Impact of Humidity on Bike Rentals'
        )
        
        fig_hum.update_layout(
            xaxis_title='Humidity (Normalized)',
            yaxis_title='Number of Rentals',
            margin=dict(l=40, r=40, t=60, b=40),
            height=350
        )
        
        st.plotly_chart(fig_hum, use_container_width=True)
    
    with col2:
        # Impact of wind speed
        fig_wind = px.scatter(
            filtered_df.sample(1000) if len(filtered_df) > 1000 else filtered_df,
            x='windspeed',
            y='cnt',
            color='windspeed',
            color_continuous_scale='Greens',
            trendline="ols",
            labels={'cnt': 'Number of Rentals', 'windspeed': 'Wind Speed (Normalized)'},
            title='Impact of Wind Speed on Bike Rentals'
        )
        
        fig_wind.update_layout(
            xaxis_title='Wind Speed (Normalized)',
            yaxis_title='Number of Rentals',
            margin=dict(l=40, r=40, t=60, b=40),
            height=350
        )
        
        st.plotly_chart(fig_wind, use_container_width=True)
    
    # Combined weather effect
    st.markdown("<h3 class='sub-header'>Combined Weather Effect</h3>", unsafe_allow_html=True)
    
    # Create 3D scatter plot
    fig_3d = px.scatter_3d(
        filtered_df.sample(2000) if len(filtered_df) > 2000 else filtered_df,
        x='temp',
        y='hum',
        z='cnt',
        color='cnt',
        size='cnt',
        size_max=10,
        opacity=0.7,
        color_continuous_scale='Viridis',
        labels={'temp': 'Temperature', 'hum': 'Humidity', 'cnt': 'Rentals'}
    )
    
    fig_3d.update_layout(
        title='3D View: Temperature, Humidity and Bike Rentals',
        scene=dict(
            xaxis_title='Temperature (Normalized)',
            yaxis_title='Humidity (Normalized)',
            zaxis_title='Number of Rentals'
        ),
        height=700,
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown(
    '<div class="key-insights"><h3>Key Insights:</h3>'
    '<ul>'
    '<li>Temperature has a significant positive correlation with bike rentals.</li>'
    '<li>Humidity shows a negative correlation with rentals.</li>'
    '<li>Peak rental hours differ between weekdays and weekends.</li>'
    '</ul></div>', 
    unsafe_allow_html=True
)

st.markdown(
    '<div class="conclusions"><h3>Conclusions</h3>'
    '<h4>Key Business Questions Answered:</h4>'
    '<ol>'
    '<li><b>How does the bike rental pattern vary throughout the day, and is there a difference between weekdays and weekends?</b>'
    '<ul>'
    '<li>Weekday rentals show distinct commuting patterns with peaks during morning (7-9 AM) and evening (5-7 PM) rush hours.</li>'
    '<li>Weekend rentals display a more even distribution with highest usage during midday (10 AM-4 PM), suggesting recreational use.</li>'
    '<li>Overall, weekday usage is more concentrated at specific hours, while weekend usage is more spread out across the day.</li>'
    '</ul></li>'
    '<li><b>How does weather affect bike rentals?</b>'
    '<ul>'
    '<li>Clear weather conditions result in significantly higher bike rentals.</li>'
    '<li>Temperature has the strongest positive correlation with rentals.</li>'
    '<li>High humidity and precipitation drastically reduce bike usage.</li>'
    '<li>Wind speed has a moderate negative effect on rental numbers.</li>'
    '</ul></li>'
    '</ol></div>', 
    unsafe_allow_html=True
)

st.markdown(
    '<div class="business-recommendations"><h3>Business Recommendations</h3>'
    '<ol>'
    '<li><b>Demand-Based Resource Allocation:</b> Adjust bike availability and maintenance schedules based on time patterns - focus on commuting hours during weekdays and midday during weekends.</li>'
    '<li><b>Weather-Based Pricing:</b> Implement dynamic pricing strategies based on weather forecasts to optimize revenue.</li>'
    '<li><b>Marketing Strategies:</b> Promote different benefits of bike sharing depending on day type - convenience for commuters on weekdays vs recreational activity on weekends.</li>'
    '<li><b>Weather Contingency Plans:</b> Develop strategies to mitigate revenue loss during unfavorable weather conditions, such as covered stations or weather protection accessories.</li>'
    '</ol></div>', 
    unsafe_allow_html=True
)

st.markdown(
    '<p style="text-align:center; font-size:14px; color:#9ca3af;">Developed by Hafiyan Al Muqaffi Umary • Dicoding ID: MC006D5Y1369</p>'
    '<p style="text-align:center; font-size:14px; color:#9ca3af;">Bike Sharing Dataset Analysis • Data Science Project • 2025</p>',
    unsafe_allow_html=True
)
