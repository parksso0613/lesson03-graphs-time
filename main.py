import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 1년치(365일) 일별 박스오피스 10위권 데이터 시각화")
st.markdown("---")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    # 날짜 열을 datetime 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df

df = load_data()

# ====================================================
# 구역 1: 선택한 영화의 날짜별 일관객 변화 (선 그래프)
# ====================================================
st.header("1. 선택한 영화의 날짜별 일관객 변화")

all_movies = sorted(df["영화명"].unique())
selected_movie = st.selectbox("분석할 영화를 선택하세요:", all_movies)

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
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객수:</b> %{y:,}명<extra></extra>"
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것**: '{selected_movie}' 영화의 관객수가 개봉 후 일자별로 어떻게 변화했는지 추이를 볼 수 있으며, "
    "주말 및 공휴일에 발생하는 관객 스파이크 현상을 한눈에 파악할 수 있습니다."
)

st.markdown("---")

# ====================================================
# 구역 2: 관객수 TOP 5 영화의 날짜별 일관객 비교 (다중 선 그래프)
# ====================================================
st.header("2. 관객수 TOP 5 영화의 날짜별 일관객 비교")

top5_movies = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="기간 내 흥행 TOP 5 영화의 일관객 추이 비교",
    labels={"날짜": "날짜", "일관객": "일 관객수 (명)", "영화명": "영화 제목"},
    markers=True,
)
fig2.update_traces(
    hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객수:</b> %{y:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

top5_str = ", ".join([f"'{m}'" for m in top5_movies])
st.info(
    f"💡 **이 그래프로 알 수 있는 것**: 전체 기간 일관객 합계 상위 5개 영화({top5_str})의 흥행 화력과 지속성을 직접 비교해볼 수 있습니다. "
    "우측 범례의 영화 이름을 클릭하면 특정 영화만 켜고 끌 수 있습니다."
)

st.markdown("---")

# ====================================================
# 구역 3: 날짜별 TOP 10 일관객 합계 (영역 그래프 + TOP 3 주석)
# ====================================================
st.header("3. 날짜별 TOP 10 일관객 합계 및 최다 관객일")

daily_sum = df.groupby("날짜")["일관객"].sum().reset_index()

fig3 = px.area(
    daily_sum,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 TOP 10 일관객 총합 추이",
    labels={"날짜": "날짜", "일관객": "일 관객수 합계 (명)"},
)
fig3.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>합계 관객수:</b> %{y:,}명<extra></extra>"
)

# 관객 합계 TOP 3 날짜 구하기 및 주석 추가
top3_days = daily_sum.nlargest(3, "일관객").reset_index(drop=True)
rank_emojis = ["🥇 1위", "🥈 2위", "🥉 3위"]

for idx, row in top3_days.iterrows():
    date_str = row["날짜"].strftime("%Y-%m-%d")
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=f"{rank_emojis[idx]} ({date_str})<br>{row['일관객']:,}명",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#FF4B4B",
        ax=0,
        ay=-40 - (idx * 15),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#FF4B4B",
        borderwidth=1,
    )

st.plotly_chart(fig3, use_container_width=True)

top3_desc = ", ".join([f"{r['날짜'].strftime('%Y-%m-%d')}({r['일관객']:,}명)" for _, r in top3_days.iterrows()])
st.info(
    f"💡 **이 그래프로 알 수 있는 것**: 영화 시장 전체의 일별 관객 볼륨 흐름을 파악할 수 있으며, "
    f"가장 극장 관객수가 많았던 TOP 3 날짜({top3_desc})를 직관적으로 확인할 수 있습니다."
)

st.markdown("---")

# ====================================================
# 구역 4: 기간 내 총 관객수 TOP 10 (가로 막대그래프)
# ====================================================
st.header("4. 기간 내 총 관객수 TOP 10 영화")

# 영화별 총 관객수 및 TOP 10 차트인 날수 집계
top10_stats = (
    df.groupby("영화명")
    .agg(총관객=("일관객", "sum"), 차트인일수=("날짜", "nunique"))
    .reset_index()
)

# TOP 10을 뽑은 뒤 가로 막대그래프 생성을 위해 오름차순 정렬 (큰 값이 위로 가도록)
top10_stats = top10_stats.nlargest(10, "총관객").sort_values("총관객", ascending=True)

fig4 = px.bar(
    top10_stats,
    x="총관객",
    y="영화명",
    orientation="h",
    title="기간 내 총 관객수 상위 10개 영화",
    labels={"총관객": "총 관객수 (명)", "영화명": "영화 제목"},
    custom_data=["차트인일수"],
)
fig4.update_traces(
    hovertemplate="<b>영화명:</b> %{y}<br><b>기간 총 관객수:</b> %{x:,}명<br><b>TOP 10 차트인 일수:</b> %{customdata[0]}일<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것**: 1년간 박스오피스 상위권에 머무른 가장 성공적인 10편의 영화를 비교할 수 있습니다. "
    "막대에 마우스를 올리면 총 관객수와 함께 10위권 내에 머문 날수(차트인 일수)도 확인할 수 있습니다."
)
