import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Heart Health & Lifestyle Analytics",
    page_icon="❤️",
    layout="wide"
)

# ----------------------------------------------------------
# PROFESSIONAL CSS
# ----------------------------------------------------------

st.markdown("""
<style>

.main{
    background:#F6F9FC;
}

h1{
    color:#12355B;
    font-weight:700;
}

h2,h3{
    color:#12355B;
}

section[data-testid="stSidebar"]{
    background:#12355B;
}

section[data-testid="stSidebar"] *{
    color:white;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,.08);
    border-left:5px solid #2E86AB;
}

</style>
""",unsafe_allow_html=True)

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------

from pathlib import Path
import pandas as pd

@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent / "Cleaned_data.csv"
    df = pd.read_csv(csv_path)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    bins = [18, 30, 40, 50, 60, 100]
    labels = ["18-30", "31-40", "41-50", "51-60", "60+"]

    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    return df

    labels=[
        "18-30",
        "31-40",
        "41-50",
        "51-60",
        "60+"
    ]

    df["Age_Group"]=pd.cut(
        df["Age"],
        bins=bins,
        labels=labels
    )

    return df

df=load_data()

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

st.sidebar.title("Dashboard Filters")

city=st.sidebar.multiselect(
    "City",
    sorted(df["City"].unique()),
    default=sorted(df["City"].unique())
)

gender=st.sidebar.multiselect(
    "Gender",
    sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

occupation=st.sidebar.multiselect(
    "Occupation",
    sorted(df["Occupation"].unique()),
    default=sorted(df["Occupation"].unique())
)

age_group=st.sidebar.multiselect(
    "Age Group",
    df["Age_Group"].dropna().unique(),
    default=df["Age_Group"].dropna().unique()
)

filtered=df[
    (df.City.isin(city))&
    (df.Gender.isin(gender))&
    (df.Occupation.isin(occupation))&
    (df.Age_Group.isin(age_group))
]

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------

st.title("🫀 Heart Health & Lifestyle Analytics")

st.caption(
"""
Executive Decision Support Dashboard

Identify heart attack risk factors using patient lifestyle and health data.
"""
)

st.divider()

# ----------------------------------------------------------
# KPI CALCULATIONS
# ----------------------------------------------------------

total=len(filtered)

heart_cases=(filtered["Heart_Attack"]=="Yes").sum()

risk=(heart_cases/total)*100

avg_bmi=filtered["BMI"].mean()

avg_sleep=filtered["Sleep_Hours"].median()

avg_chol=filtered["Cholesterol"].mean()

avg_stress=filtered["Stress_Level"].median()

# ----------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------

c1,c2,c3,c4,c5,c6=st.columns(6)

c1.metric(
    "👥 Patients",
    f"{total:,}"
)

c2.metric(
    "🫀 Heart Attack",
    heart_cases
)

c3.metric(
    "📈 Risk %",
    f"{risk:.1f}%"
)

c4.metric(
    "⚖ BMI",
    f"{avg_bmi:.1f}"
)

c5.metric(
    "😴 Sleep",
    f"{avg_sleep:.1f} hrs"
)

c6.metric(
    "🧠 Stress",
    f"{avg_stress:.1f}"
)

st.divider()

# ----------------------------------------------------------
# EXECUTIVE SUMMARY
# ----------------------------------------------------------

left,right=st.columns([2,1])

highest_age=filtered.groupby("Age_Group")["Heart_Attack"]\
.apply(lambda x:(x=="Yes").sum()).idxmax()

highest_city=filtered.groupby("City")["Heart_Attack"]\
.apply(lambda x:(x=="Yes").sum()).idxmax()

highest_job=filtered.groupby("Occupation")["Heart_Attack"]\
.apply(lambda x:(x=="Yes").sum()).idxmax()

with left:

    st.info(f"""

### Executive Insights

• Highest Risk Age Group : **{highest_age}**

• Highest Risk City : **{highest_city}**

• Highest Risk Occupation : **{highest_job}**

• Overall Heart Attack Risk : **{risk:.1f}%**

""")

with right:

    gauge=go.Figure(go.Indicator(

        mode="gauge+number",

        value=risk,

        number={"suffix":"%"},

        title={"text":"Risk Level"},

        gauge={

            "axis":{"range":[0,100]},

            "bar":{"color":"#E63946"},

            "steps":[

                {"range":[0,30],"color":"#52B788"},

                {"range":[30,60],"color":"#F4A261"},

                {"range":[60,100],"color":"#E63946"}

            ]

        }

    ))

    gauge.update_layout(height=300)

    st.plotly_chart(
        gauge,
       width="stretch"
    )

st.divider()

st.subheader("Risk Factor Analysis")


# ==========================================================
# AGE GROUP ANALYSIS
# ==========================================================

col1, col2 = st.columns(2)

age_df = (
    filtered[filtered["Heart_Attack"] == "Yes"]
    .groupby("Age_Group")
    .size()
    .reset_index(name="Cases")
)

fig_age = px.bar(
    age_df,
    x="Age_Group",
    y="Cases",
    text="Cases",
    color="Cases",
    color_continuous_scale="Blues"
)

fig_age.update_layout(
    title="Heart Attack Cases by Age Group",
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False,
    xaxis_title="Age Group",
    yaxis_title="Heart Attack Cases"
)

col1.plotly_chart(fig_age, width="stretch")

# ==========================================================
# STRESS ANALYSIS
# ==========================================================

stress_df = (
    filtered.groupby("Stress_Level")["Heart_Attack"]
    .apply(lambda x: (x == "Yes").sum())
    .reset_index(name="Cases")
)

fig_stress = px.line(
    stress_df,
    x="Stress_Level",
    y="Cases",
    markers=True
)

fig_stress.update_traces(
    line_color="#E63946",
    marker_size=10
)

fig_stress.update_layout(
    title="Stress Level vs Heart Attack",
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="Stress Level",
    yaxis_title="Heart Attack Cases"
)

col2.plotly_chart(fig_stress, width="stretch")

# ==========================================================
# SLEEP & EXERCISE
# ==========================================================

col3, col4 = st.columns(2)

fig_sleep = px.box(
    filtered,
    x="Heart_Attack",
    y="Sleep_Hours",
    color="Heart_Attack",
    color_discrete_map={
        "Yes": "#E63946",
        "No": "#52B788"
    }
)

fig_sleep.update_layout(
    title="Sleep Hours vs Heart Attack",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col3.plotly_chart(fig_sleep, width="stretch")

fig_exercise = px.box(
    filtered,
    x="Heart_Attack",
    y="Exercise_Hours_Per_Week",
    color="Heart_Attack",
    color_discrete_map={
        "Yes": "#E63946",
        "No": "#52B788"
    }
)

fig_exercise.update_layout(
    title="Exercise Hours vs Heart Attack",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col4.plotly_chart(fig_exercise,width="stretch")

# ==========================================================
# BMI & CHOLESTEROL
# ==========================================================

col5, col6 = st.columns(2)

fig_bmi = px.scatter(
    filtered,
    x="BMI",
    y="Cholesterol",
    color="Heart_Attack",
    size="Age",
    hover_data=[
        "Gender",
        "City",
        "Occupation"
    ],
    color_discrete_map={
        "Yes": "#E63946",
        "No": "#52B788"
    }
)

fig_bmi.update_layout(
    title="BMI vs Cholesterol",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col5.plotly_chart(fig_bmi, width="stretch")

fig_hist = px.histogram(
    filtered,
    x="BMI",
    color="Heart_Attack",
    nbins=25,
    color_discrete_map={
        "Yes": "#E63946",
        "No": "#52B788"
    }
)

fig_hist.update_layout(
    title="BMI Distribution",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col6.plotly_chart(fig_hist, width="stretch")

# ==========================================================
# BMI ANALYTICS
# ==========================================================

st.subheader("BMI Analytics")

bmi_df = filtered.copy()

bmi_df["BMI Category"] = pd.cut(
    bmi_df["BMI"],
    bins=[0,18.5,25,30,100],
    labels=[
        "Underweight",
        "Normal",
        "Overweight",
        "Obese"
    ]
)

# ------------------------------
# Row 1
# ------------------------------

col5, col6 = st.columns(2)

# BMI Category Distribution

bmi_category = (
    bmi_df.groupby("BMI Category")
    .size()
    .reset_index(name="Patients")
)

fig_bmi_category = px.bar(
    bmi_category,
    x="BMI Category",
    y="Patients",
    text="Patients",
    color="BMI Category",
    color_discrete_sequence=[
        "#43AA8B",
        "#4D908E",
        "#F9C74F",
        "#F94144"
    ]
)

fig_bmi_category.update_layout(
    title="Patient Distribution by BMI Category",
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

col5.plotly_chart(
    fig_bmi_category,
    width="stretch",
    key="bmi_category_chart"
)


# BMI Distribution

fig_distribution = px.histogram(
    bmi_df,
    x="BMI",
    color="Heart_Attack",
    nbins=30,
    marginal="box",
    color_discrete_map={
        "Yes":"#E63946",
        "No":"#52B788"
    }
)

fig_distribution.update_layout(
    title="BMI Distribution by Heart Attack Status",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col6.plotly_chart(
    fig_distribution,
    width="stretch",
    key="bmi_distribution_chart"
)



# ------------------------------
# Row 2
# ------------------------------

col7, col8 = st.columns(2)

# BMI vs Cholesterol

fig_scatter = px.scatter(
    bmi_df,
    x="BMI",
    y="Cholesterol",
    color="Heart_Attack",
    size="Age",
    hover_data=[
        "Gender",
        "City",
        "Occupation"
    ],
    color_discrete_map={
        "Yes":"#E63946",
        "No":"#52B788"
    }
)

fig_scatter.update_layout(
    title="BMI vs Cholesterol",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

col7.plotly_chart(
    fig_scatter,
    width="stretch",
    key="bmi_scatter_chart"
)


# Average BMI
avg_bmi_comparison = (
    bmi_df.groupby("Heart_Attack")["BMI"]
    .mean()
    .reset_index()
)

fig_avg = px.bar(
    avg_bmi_comparison,
    x="Heart_Attack",
    y="BMI",
    text_auto=".1f",
    color="Heart_Attack",
    color_discrete_map={
        "Yes":"#E63946",
        "No":"#52B788"
    }
)

fig_avg.update_layout(
    title="Average BMI by Heart Attack Status",
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

col8.plotly_chart(
    fig_avg,
    width="stretch",
    key="bmi_average_chart"
)

# ==========================================================
# SMOKING & ALCOHOL
# ==========================================================

col7, col8 = st.columns(2)

smoke_df = (
    filtered.groupby("Smoking")["Heart_Attack"]
    .apply(lambda x: (x == "Yes").sum())
    .reset_index(name="Cases")
)

fig_smoke = px.bar(
    smoke_df,
    x="Smoking",
    y="Cases",
    text="Cases",
    color="Cases",
    color_continuous_scale="Reds"
)

fig_smoke.update_layout(
    title="Smoking Impact on Heart Attack",
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False
)

col7.plotly_chart(fig_smoke, width="stretch")

alcohol_df = (
    filtered.groupby("Alcohol_Consumption")["Heart_Attack"]
    .apply(lambda x: (x == "Yes").sum())
    .reset_index(name="Cases")
)

fig_alcohol = px.bar(
    alcohol_df,
    x="Alcohol_Consumption",
    y="Cases",
    text="Cases",
    color="Cases",
    color_continuous_scale="Oranges"
)

fig_alcohol.update_layout(
    title="Alcohol Consumption",
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False
)

col8.plotly_chart(fig_alcohol, width="stretch")

# ==========================================================
# FAST FOOD ANALYSIS
# ==========================================================

fig_fast = px.box(
    filtered,
    x="Heart_Attack",
    y="Fast_Food_Meals_Per_Week",
    color="Heart_Attack",
    color_discrete_map={
        "Yes": "#E63946",
        "No": "#52B788"
    }
)

fig_fast.update_layout(
    title="Fast Food Meals per Week vs Heart Attack",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig_fast, width="stretch")
st.divider()



# ==========================================================
# GEOGRAPHIC ANALYSIS
# ==========================================================

st.subheader("🌍 Geographic & Occupation Analysis")

col1, col2 = st.columns(2)

# City Analysis
city_df = (
    filtered[filtered["Heart_Attack"] == "Yes"]
    .groupby("City")
    .size()
    .reset_index(name="Cases")
    .sort_values("Cases", ascending=False)
)

fig_city = px.bar(
    city_df,
    x="Cases",
    y="City",
    orientation="h",
    color="Cases",
    text="Cases",
    color_continuous_scale="Blues"
)

fig_city.update_layout(
    title="High-Risk Cities",
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False,
    yaxis_title="",
    xaxis_title="Heart Attack Cases"
)

col1.plotly_chart(fig_city, width="stretch")

# Occupation Analysis
occupation_df = (
    filtered[filtered["Heart_Attack"] == "Yes"]
    .groupby("Occupation")
    .size()
    .reset_index(name="Cases")
    .sort_values("Cases", ascending=False)
)

fig_job = px.bar(
    occupation_df,
    x="Cases",
    y="Occupation",
    orientation="h",
    color="Cases",
    text="Cases",
    color_continuous_scale="Teal"
)

fig_job.update_layout(
    title="High-Risk Occupations",
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False,
    yaxis_title="",
    xaxis_title="Heart Attack Cases"
)

col2.plotly_chart(fig_job, width="stretch")

st.divider()

# ==========================================================
# CORRELATION ANALYSIS
# ==========================================================

st.subheader("📈 Correlation Analysis")

numeric_columns = [
    "Age",
    "BMI",
    "Cholesterol",
    "Exercise_Hours_Per_Week",
    "Sleep_Hours",
    "Stress_Level",
    "Fast_Food_Meals_Per_Week"
]

corr = filtered[numeric_columns].corr()

fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    aspect="auto"
)

fig_corr.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig_corr, width="stretch")

st.divider()

# ==========================================================
# EXECUTIVE INSIGHTS
# ==========================================================

st.subheader("💡 Executive Insights")

highest_city = city_df.iloc[0]["City"] if not city_df.empty else "N/A"
highest_job = occupation_df.iloc[0]["Occupation"] if not occupation_df.empty else "N/A"

highest_age = (
    filtered.groupby("Age_Group")["Heart_Attack"]
    .apply(lambda x: (x == "Yes").sum())
    .idxmax()
)

avg_sleep_yes = filtered[filtered["Heart_Attack"] == "Yes"]["Sleep_Hours"].mean()
avg_sleep_no = filtered[filtered["Heart_Attack"] == "No"]["Sleep_Hours"].mean()

avg_bmi_yes = filtered[filtered["Heart_Attack"] == "Yes"]["BMI"].mean()
avg_bmi_no = filtered[filtered["Heart_Attack"] == "No"]["BMI"].mean()

c1, c2 = st.columns(2)

with c1:

    st.success(f"""
### Key Findings

✅ Highest Risk Age Group: **{highest_age}**

✅ Highest Risk City: **{highest_city}**

✅ Highest Risk Occupation: **{highest_job}**

✅ Overall Heart Attack Risk: **{risk:.1f}%**
""")

with c2:

    st.warning(f"""
### Lifestyle Comparison

😴 Average Sleep (Heart Attack): **{avg_sleep_yes:.1f} hrs**

😴 Average Sleep (Healthy): **{avg_sleep_no:.1f} hrs**

⚖ Average BMI (Heart Attack): **{avg_bmi_yes:.1f}**

⚖ Average BMI (Healthy): **{avg_bmi_no:.1f}**
""")

st.divider()

# ==========================================================
# STRATEGIC RECOMMENDATIONS
# ==========================================================

st.subheader("🎯 Strategic Recommendations")

st.markdown("""
### High Priority Actions

- 🚭 Promote smoking cessation programs.
- 🧠 Conduct stress-management workshops.
- 🫀 Organize cholesterol and BMI screening camps.
- 🏃 Encourage regular physical activity.

### Medium Priority Actions

- 😴 Encourage 7–8 hours of quality sleep.
- 🍎 Promote healthier eating and reduce fast-food consumption.
- 🍷 Raise awareness about responsible alcohol consumption.

### Resource Allocation

- 📍 Prioritize preventive healthcare campaigns in high-risk cities.
- 💼 Conduct health awareness programs for high-risk occupations.
- 👨‍⚕️ Schedule periodic medical check-ups for vulnerable age groups.
""")

st.divider()


# ==========================================================
# TOP 5 HIGH-RISK LOCATIONS & OCCUPATIONS
# ==========================================================

st.subheader("🏆 Top 5 High-Risk Categories")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 5 High-Risk Cities")
    top_cities = city_df.head(5).reset_index(drop=True)
    top_cities.index = top_cities.index + 1
    st.dataframe(top_cities, width="stretch")

with col2:
    st.markdown("#### Top 5 High-Risk Occupations")
    top_jobs = occupation_df.head(5).reset_index(drop=True)
    top_jobs.index = top_jobs.index + 1
    st.dataframe(top_jobs, width="stretch")

st.divider()

# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

st.subheader("📋 Dashboard Summary")

summary = pd.DataFrame({
    "Metric": [
        "Total Patients",
        "Heart Attack Cases",
        "Risk Percentage",
        "Highest Risk Age Group",
        "Highest Risk City",
        "Highest Risk Occupation",
        "Average BMI",
        "Average Sleep Hours",
        "Average Stress Level"
    ],
    "Value": [
        str(total),
        str(heart_cases),
        f"{risk:.1f}%",
        str(highest_age),
        str(highest_city),
        str(highest_job),
        f"{avg_bmi:.1f}",
        f"{avg_sleep:.1f}",
        f"{avg_stress:.1f}"
    ]
})

st.dataframe(summary, width="stretch")

st.divider()

# ==========================================================
# DOWNLOAD FILTERED DATA
# ==========================================================

st.subheader("📥 Export Data")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Dataset (CSV)",
    data=csv,
    file_name="Heart_Health_Filtered_Data.csv",
    mime="text/csv"
)

st.divider()

# ==========================================================
# STAKEHOLDER CONCLUSION
# ==========================================================

st.subheader("📝 Conclusion")

st.success("""
### Business Conclusion

The dashboard highlights that heart attack risk is strongly associated with
higher age, increased stress, unhealthy lifestyle habits, elevated BMI,
and cholesterol levels.

Using these insights, healthcare organizations can:

• Identify high-risk populations.

• Focus preventive campaigns in vulnerable cities.

• Encourage healthy lifestyle modifications.

• Improve early screening for patients at greater risk.

These data-driven insights enable better healthcare planning,
resource allocation, and preventive decision-making.
""")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """
    <hr style='margin-top:40px;margin-bottom:10px;'>

    <center>

    <h4 style='color:#12355B;'>
    🫀 Heart Health & Lifestyle Analytics
    </h4>

    <p style='color:gray;'>
    Executive Decision Support Dashboard
    </p>

    <p style='color:gray;font-size:13px;'>
    Prepared by <b>Bhuvaneshwaran C </b>
    </p>

    </center>
    """,
    unsafe_allow_html=True
)


