import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data():
    # 데이터 로드
    df = pd.read_csv(DATA_URL)
    
    # '날짜' 열을 YYYYMMDD 형태의 문자열로 변환 후 datetime 객체로 전환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d', errors='coerce')
    
    # 날짜 순 및 순위 순 정렬
    df = df.sort_values(by=['날짜', '순위']).reset_index(drop=True)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
KOBIS 일별 박스오피스 데이터를 바탕으로 **시간(날짜)**의 흐름에 따른 영화 관객 수 변화와 패턴을 시각화하는 도감입니다.
""")
st.divider()

st.header("📌 구역 1. 개별 영화의 일별 관객수 추이")
st.caption("드롭다운에서 영화를 선택하면, 상영 기간 동안 해당 영화의 일관객수 변화를 선 그래프로 보여줍니다.")

# 관객 수 합계 순으로 영화 목록 정렬하여 옵션 제공
movie_audience_sum = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False)
movie_options = movie_audience_sum.index.tolist()

selected_movie = st.selectbox(
    "📊 조회할 영화를 선택하세요:",
    options=movie_options,
    index=0
)

# 선택된 영화 데이터 필터링
movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

if not movie_df.empty:
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 변화 추이",
        labels={'날짜': '날짜', '일관객': '일일 관객수(명)'},
        markers=True
    )
    
    # 마우스 호버 및 스타일 설정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
        line=dict(width=3, color='#E50914'),
        marker=dict(size=6, color='#141414')
    )
    
    fig1.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#E5E5E5'),
        yaxis=dict(showgrid=True, gridcolor='#E5E5E5', tickformat=','),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 최고 관객수 기록 날짜 계산
    max_row = movie_df.loc[movie_df['일관객'].idxmax()]
    max_date_str = max_row['날짜'].strftime('%Y-%m-%d')
    max_audience = max_row['일관객']
    
    # 그래프 하단 '이 그래프로 알 수 있는 것' 문구 박스
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'은(는) **{max_date_str}**에 일일 최다 관객수(**{max_audience:,}명**)를 기록하였으며, 개봉 후 시간이 지남에 따라 관객 수가 점차 감소하거나 주말에 다시 상승하는 패턴을 확인할 수 있습니다."
    )
else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

st.divider()

st.header("📌 구역 2. 관객 수 Top 5 영화의 일별 관객수 비교")
st.caption("해당 기간 동안 누적 관객수(일관객 합계)가 가장 높은 상위 5개 영화의 일별 관객수 추이를 한 그래프에서 비교합니다.")

# 일관객 합계 기준 Top 5 영화 추출 및 데이터 필터링
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="<b>Top 5 영화 일별 관객수 추이 비교</b>",
    labels={'날짜': '날짜', '일관객': '일일 관객수(명)', '영화명': '영화명'},
    markers=True
)

fig2.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig2.update_layout(
    xaxis=dict(showgrid=True, gridcolor='#E5E5E5'),
    yaxis=dict(showgrid=True, gridcolor='#E5E5E5', tickformat=','),
    hovermode="x unified",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(
        title=dict(text="영화 목록 (클릭하여 범례 On/Off)"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig2, use_container_width=True)

# Top 5 영화 목록 문자열 생성
top5_str = ", ".join([f"**{m}**" for m in top5_movies])

# 그래프 하단 '이 그래프로 알 수 있는 것' 문구 박스
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 기간 전체 관객 수가 가장 많은 Top 5 영화({top5_str})의 흥행 주기와 전성기 관객 수를 한눈에 비교할 수 있으며, 범례 항목을 클릭해 특정 영화를 켜거나 끌 수 있습니다."
)

st.divider()

st.header("📌 구역 3. 날짜별 박스오피스 Top 10 일관객 합계 (영역 그래프)")
st.caption("매일 10위권 영화들의 일관객수 합계를 영역 그래프로 시각화하고, 관객 수가 가장 많았던 상위 3개 날짜를 그래프 위에 주석으로 강조합니다.")

# 날짜별 Top 10 일관객 합계 계산
daily_sum = df.groupby('날짜')['일관객'].sum().reset_index()

fig3 = px.area(
    daily_sum,
    x='날짜',
    y='일관객',
    title="<b>일별 박스오피스 Top 10 관객수 합계 추이</b>",
    labels={'날짜': '날짜', '일관객': '총 일관객수(명)'}
)

fig3.update_traces(
    line_color='#E50914',
    fillcolor='rgba(229, 9, 20, 0.25)',
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

# 일관객 합계가 가장 컸던 상위 3개 날짜 추출 및 그래프 상 표기
top3_days = daily_sum.nlargest(3, '일관객').reset_index(drop=True)

for i, row in top3_days.iterrows():
    rank = i + 1
    date_str = row['날짜'].strftime('%Y-%m-%d')
    aud_count = row['일관객']
    
    # 그래프 내 주석(Annotation) 배치
    fig3.add_annotation(
        x=row['날짜'],
        y=aud_count,
        text=f"<b>🏆 {rank}위: {date_str}</b><br>({aud_count:,}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor='#E50914',
        ax=0,
        ay=-45 - (i * 12),
        bgcolor="white",
        bordercolor='#E50914',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#141414')
    )

fig3.update_layout(
    xaxis=dict(showgrid=True, gridcolor='#E5E5E5'),
    yaxis=dict(showgrid=True, gridcolor='#E5E5E5', tickformat=','),
    hovermode="x unified",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig3, use_container_width=True)

# Top 3 날짜안내 문구 구성
top3_text_list = [
    f"**{row['날짜'].strftime('%Y-%m-%d')}** ({row['일관객']:,}명)"
    for _, row in top3_days.iterrows()
]
top3_str = ", ".join(top3_text_list)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 전체 극장가(Top 10 영화 기준)의 날짜별 관객수 총합 흐름을 영역 그래프로 한눈에 볼 수 있습니다. 이 기간 중 일일 총 관객 수가 가장 많았던 날 Top 3는 순서대로 {top3_str} 입니다."
)

st.divider()

st.header("📌 구역 4. 추가 시간 분석 그래프 (확장용 구역)")
st.caption("추후 요일별/월별 관객수 변화 등 새로운 시간 분석 그래프를 지속적으로 추가할 수 있는 영역입니다.")

with st.expander("🔍 원본 데이터 미리보기 (Data Viewer)"):
    st.dataframe(df, use_container_width=True)
