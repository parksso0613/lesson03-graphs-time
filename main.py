import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
page_title="영화 데이터 그래프 도감 1 - 시간",
page_icon="🎬",
layout="wide",
)

@st.cache_data
def load_data():
"""GitHub에서 1년치 KOBIS 일별 박스오피스 CSV 데이터를 불러와 전처리합니다."""
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
df = pd.read_csv(url)
# 날짜(숫자 8자리)를 datetime 객체로 변환
df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
return df

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("1년치(365일) 일별 박스오피스 10위권 기록을 다양한 시각으로 분석합니다.")

df = load_data()

st.divider()

----------------------------------------------------

구역 1: 특정 영화의 날짜별 일관객 변화

----------------------------------------------------

st.header("1. 영화별 날짜별 일관객 변화")

movie_list = sorted(df["영화명"].unique().tolist())
selected_movie = st.selectbox("조회할 영화를 선택해 주세요:", movie_list)

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
movie_df,
x="날짜",
y="일관객",
title=f"'{selected_movie}' 날짜별 일관객 추이",
labels={"날짜": "날짜", "일관객": "일 관객수 (명)"},
markers=True,
)
fig1.update_traces(
hovertemplate="날짜: %{x|%Y-%m-%d}



관객수: %{y:,}명"
)

st.plotly_chart(fig1, width="stretch")

st.info(
f"💡 이 그래프로 알 수 있는 것: '{selected_movie}'의 개봉 후 관객수 변화 흐름과 주말/평일 관객 차이 및 흥행 유지 기간을 한눈에 파악할 수 있습니다."
)

st.divider()

----------------------------------------------------

구역 2: 일관객 합계 상위 5개 영화 비교

----------------------------------------------------

st.header("2. 관객수 상위 5개 영화 관객 추이 비교")

top5_movies = (
df.groupby("영화명")["일관객"]
.sum()
.nlargest(5)
.index.tolist()
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
top5_df,
x="날짜",
y="일관객",
color="영화명",
title="기간 내 일관객 합계 상위 5개 영화 추이 비교",
labels={"날짜": "날짜", "일관객": "일 관객수 (명)", "영화명": "영화 제목"},
markers=True,
)
fig2.update_traces(
hovertemplate="%{data.name}



날짜: %{x|%Y-%m-%d}



관객수: %{y:,}명"
)

st.plotly_chart(fig2, width="stretch")

st.info(
"💡 이 그래프로 알 수 있는 것: 해당 기간 최고 흥행작 5편의 관객 추이를 동시에 비교할 수 있으며, 우측 범례를 클릭하여 원하는 영화의 선만 켜거나 끌 수 있습니다."
)

st.divider()

----------------------------------------------------

구역 3: 극장가 일별 10위권 총 관객수 흐름

----------------------------------------------------

st.header("3. 극장가 일별 박스오피스 TOP 10 총 관객수 흐름")

daily_total = (
df.groupby("날짜")["일관객"]
.sum()
.reset_index()
.sort_values("날짜")
)

총 관객수 상위 3일 추출

top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

fig3 = px.area(
daily_total,
x="날짜",
y="일관객",
title="일별 박스오피스 10위권 관객 합계",
labels={"날짜": "날짜", "일관객": "10위권 관객 합계 (명)"},
)
fig3.update_traces(
hovertemplate="날짜: %{x|%Y-%m-%d}



합계 관객수: %{y:,}명"
)

상위 3일 주석 추가

for i, row in enumerate(top3_days.itertuples(), start=1):
date_str = row.날짜.strftime("%Y-%m-%d")
fig3.add_annotation(
x=row.날짜,
y=row.일관객,
text=f"🏆 {i}위: {date_str} ({row.일관객:,}명)",
showarrow=True,
arrowhead=2,
ax=0,
ay=-30 - (i * 10),
bgcolor="rgba(255, 255, 255, 0.8)",
bordercolor="red",
)

st.plotly_chart(fig3, width="stretch")

top3_info = ", ".join(
[f"{r.날짜.strftime('%Y-%m-%d')} ({r.일관객:,}명)" for r in top3_days.itertuples()]
)
st.info(
f"💡 이 그래프로 알 수 있는 것: 극장 전체의 성수기/비수기 시즌 흐름을 파악할 수 있으며, 이 기간 관객이 가장 몰렸던 TOP 3 날짜는 {top3_info} 입니다."
)

st.divider()

----------------------------------------------------

구역 4: 기간 내 관객수 TOP 10 영화 (가로 막대그래프)

----------------------------------------------------

st.header("4. 기간 내 총 관객수 TOP 10 영화")

movie_summary = (
df.groupby("영화명")
.agg(총관객=("일관객", "sum"), 십위권_진입일수=("날짜", "count"))
.reset_index()
)

가장 관객수가 많은 영화가 위에 오도록 ascending=True 정렬 후 Head 10 추출

top10_summary = (
movie_summary.sort_values("총관객", ascending=False)
.head(10)
.sort_values("총관객", ascending=True)
)

fig4 = px.bar(
top10_summary,
x="총관객",
y="영화명",
orientation="h",
title="기간 내 총 관객수 TOP 10 영화",
labels={
"총관객": "총 일관객 합계 (명)",
"영화명": "영화 제목",
"십위권_진입일수": "10위권 유지 날수",
},
custom_data=["십위권_진입일수"],
)

fig4.update_traces(
hovertemplate="%{y}



총 관객수: %{x:,}명



10위권 유지 날수: %{customdata[0]}일"
)

st.plotly_chart(fig4, width="stretch")

st.info(
"💡 이 그래프로 알 수 있는 것: 분석 기간 동안 가장 많은 총 관객을 모은 흥행 TOP 10 영화와, 각 영화가 박스오피스 10위권 내에 며칠 동안 유지되었는지(흥행 롱런 여부)를 한눈에 확인할 수 있습니다."
)
