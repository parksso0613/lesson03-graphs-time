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

st.header("📌 구역 2. 박스오피스 전체 일별 총 관객수 추이")
st.caption("1년 동안의 일별 박스오피스 Top 10 영화 관객수 합계를 통해 극장가 전체의 성수기와 비수기 흐름을 확인합니다.")

daily_total_df = df.groupby('날짜')['일관객'].sum().reset_index()

fig2 = px.line(
    daily_total_df,
    x='날짜',
    y='일관객',
    title="<b>일별 박스오피스 Top 10 총 관객수 흐름</b>",
    labels={'날짜': '날짜', '일관객': 'Top 10 일관객 합계(명)'}
)

fig2.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객수:</b> %{y:,}명<extra></extra>",
    line=dict(width=2, color='#2B6CB0')
)

fig2.update_layout(
    xaxis=dict(showgrid=True, gridcolor='#E5E5E5'),
    yaxis=dict(showgrid=True, gridcolor='#E5E5E5', tickformat=','),
    hovermode="x unified",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 하단 '이 그래프로 알 수 있는 것' 문구 박스
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 연휴, 명절, 여름 휴가철 등 특정 개봉 시즌에 극장 전체 관객수가 급격히 증가하는 '시즌성 변동 패턴'을 알 수 있습니다."
)

st.divider()

st.header("📌 구역 3. 추가 시간 분석 그래프 (확장용 구역)")
st.caption("추후 요일별/월별 관객수 변화 등 새로운 시간 분석 그래프를 지속적으로 추가할 수 있는 영역입니다.")

with st.expander("🔍 원본 데이터 미리보기 (Data Viewer)"):
    st.dataframe(df, use_container_width=True)
