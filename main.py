import io

import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    # GitHub raw 서버가 User-Agent 없는 요청을 종종 막기 때문에,
    # pandas가 바로 URL을 읽게 하지 않고 requests로 먼저 내려받습니다.
    headers = {"User-Agent": "Mozilla/5.0 (Streamlit App)"}
    response = requests.get(DATA_URL, headers=headers, timeout=10)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
    df["장르"] = df["genre"].str.split("|").str[0]
    return df


df = load_data()

# ── 그래프 1. 장르별 영화 편수 도넛 ──
st.header("1. 장르별 영화 편수 (도넛)")
genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,  # 가운데 구멍을 뚫어 도넛 모양으로
)
# 조각에 마우스를 올리면 편수와 비율이 보이게 합니다
fig1.update_traces(hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>")
st.plotly_chart(fig1, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note1")

st.divider()

# ── 그래프 2. 장르 안에 영화가 들어 있는 트리맵 ──
st.header("2. 장르 안 영화별 총 관객 (트리맵)")
fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
)
# 칸에 마우스를 올리면 영화명과 총 관객이 보이게 합니다
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>"
)
st.plotly_chart(fig2, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note2")

st.divider()

# ── 그래프 3. 총 관객 히스토그램 ──
st.header("3. 총 관객 분포 (히스토그램)")
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig3.update_layout(
    xaxis_title="총 관객 (명)",
    yaxis_title="영화 편수",
)
st.plotly_chart(fig3, width="stretch")

# 대부분의 영화가 어느 구간에 몰려 있는지, 가장 관객이 많은 영화가 무엇인지 문구로 보여줍니다
under_1m = (df["total_audi"] < 1_000_000).sum()
total_count = len(df)
top_movie = df.loc[df["total_audi"].idxmax()]
st.markdown(
    f"- 전체 {total_count}편 중 **{under_1m}편**이 총 관객 **100만 명 미만** 구간에 몰려 있습니다.\n"
    f"- 총 관객이 가장 많은 영화는 **{top_movie['movieNm']}** "
    f"(총 관객 {top_movie['total_audi']:,}명)입니다."
)

st.text_input("이 그래프로 알 수 있는 것", key="note3")

st.divider()

# ── 그래프 4. 스크린수 vs 총 관객 산점도 ──
st.header("4. 개봉일 스크린수와 총 관객의 관계 (산점도)")
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
)
fig4.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 (명)",
)
st.plotly_chart(fig4, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note4")

st.divider()

# ── 그래프 5. 장르별 총 관객 박스플롯 (확장) ──
st.header("5. 장르별 총 관객 분포 (박스플롯)")
genre_counts_all = df["장르"].value_counts()
big_genres = genre_counts_all[genre_counts_all >= 10].index
df_box = df[df["장르"].isin(big_genres)]

fig5 = px.box(
    df_box,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
)
fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 (명)",
)
st.plotly_chart(fig5, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note5")

st.divider()

# ── 그래프 6. 버블 그래프 (확장) ──
st.header("6. 스크린수·총 관객·첫 주 관객 (버블)")
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="장르",
    hover_name="movieNm",
    size_max=40,
)
fig6.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 (명)",
)
st.plotly_chart(fig6, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note6")

st.divider()

# ── 그래프 7. 선버스트 (심화) ──
st.header("7. 국가 → 장르 (선버스트)")
nation_genre_count = (
    df.groupby(["nation", "장르"]).size().reset_index(name="편수")
)

fig7 = px.sunburst(
    nation_genre_count,
    path=["nation", "장르"],
    values="편수",
)
fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>%{value}편<extra></extra>"
)
st.plotly_chart(fig7, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note7")

st.divider()

# ── 그래프 8. 나만의 질문 — 10위권에 오래 머문 영화는 총 관객도 많은가 (산점도) ──
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")
fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
)
fig8.update_layout(
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객 (명)",
)
st.plotly_chart(fig8, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note8")
