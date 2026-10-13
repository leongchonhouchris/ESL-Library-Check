import pandas as pd
import streamlit as st

st.set_page_config(page_title="128本英文教材檢索庫", layout="wide")
st.title("📚 英文教材與拆書篩選庫 (支援語意 Close Match)")


@st.cache_data
def load_data():
  return pd.read_csv("ESL_Textbooks_Categorized.csv")


df = load_data()

# 常用 DSE / IELTS 主題同義詞與語意關聯庫
THEME_EXPANSIONS = {
    "environment": [
        "environment",
        "nature",
        "natural world",
        "biodiversity",
        "climate",
        "planet",
        "ecology",
        "green",
        "pollution",
        "conservation",
        "wildlife",
        "carbon",
        "sustainable",
        "sustainability",
        "ecosystem",
        "global warming",
        "energy",
    ],
    "technology": [
        "tech",
        "technology",
        "ai",
        "artificial intelligence",
        "algorithm",
        "digital",
        "cyber",
        "automation",
        "internet",
        "robot",
        "virtual",
        "science",
        "computer",
        "media",
    ],
    "education": [
        "education",
        "school",
        "study",
        "student",
        "college",
        "university",
        "learning",
        "academic",
        "pedagogy",
        "campus",
    ],
    "health": [
        "health",
        "medicine",
        "medical",
        "mental",
        "disease",
        "fitness",
        "diet",
        "well-being",
        "ageing",
        "aging",
        "hospital",
        "psychology",
        "stress",
    ],
    "society": [
        "society",
        "social",
        "community",
        "equality",
        "culture",
        "cultural",
        "tradition",
        "population",
        "immigration",
        "family",
        "crime",
        "law",
        "charity",
    ],
    "work": [
        "work",
        "job",
        "career",
        "workplace",
        "employment",
        "business",
        "economy",
        "economic",
        "industry",
        "labour",
        "corporate",
    ],
    "youth": [
        "youth",
        "teenager",
        "adolescent",
        "young",
        "children",
        "generation",
    ],
    "grammar_complex": [
        "inversion",
        "conditional",
        "participle",
        "subjunctive",
        "relative clause",
        "noun clause",
        "passive",
    ],
}

# 側邊欄篩選器
st.sidebar.header("🔍 多維篩選條件")

# 1. 書籍細分類別
all_categories = sorted(df["書籍細分類別"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "書籍類別 (可多選):", options=all_categories, default=[]
)

# 2. 關鍵字搜尋 + Close Match 開關
keyword = st.sidebar.text_input("輸入關鍵字 (如 environment, AI, inversion):", "")
enable_synonyms = st.sidebar.checkbox(
    "💡 開啟語意 Close Match (自動包含同義與關聯概念)", value=True
)

# 3. 水平篩選
level_filter = st.sidebar.multiselect(
    "目標水平 (CEFR / Band):", ["B1", "B1+", "B2", "B2+", "C1", "C2"]
)

# 執行過濾
filtered = df.copy()

if selected_categories:
  filtered = filtered[filtered["書籍細分類別"].isin(selected_categories)]

if keyword:
  clean_kw = keyword.strip().lower()
  search_terms = [clean_kw]

  # 如果開啟關聯搜尋，檢查有沒有預設的關聯詞
  if enable_synonyms:
    matched_expansions = []
    for key, syn_list in THEME_EXPANSIONS.items():
      # 如果輸入的字在關聯群組內，將整組詞納入搜尋
      if clean_kw in syn_list or any(clean_kw in s for s in syn_list):
        matched_expansions.extend(syn_list)
    if matched_expansions:
      search_terms = list(set(search_terms + matched_expansions))
      st.sidebar.caption(
          f"🔗 自動關聯搜尋詞: `{', '.join(search_terms[:8])}...`"
      )

  # 構建正規表達式匹配
  pattern = "|".join(search_terms)
  mask = (
      filtered["包含的核心 Topic/Theme"].str.contains(
          pattern, case=False, na=False
      )
      | filtered["包括的 grammar points"].str.contains(
          pattern, case=False, na=False
      )
      | filtered["推薦用途"].str.contains(pattern, case=False, na=False)
      | filtered["書名與類型"].str.contains(pattern, case=False, na=False)
  )
  filtered = filtered[mask]

if level_filter:
  pattern = "|".join(level_filter)
  filtered = filtered[
      filtered["CEFR Level"].str.contains(pattern, case=False, na=False)
  ]

st.markdown(f"共找到 **{len(filtered)}** 本符合條件的參考書：")

# 顯示卡片列表
for _, row in filtered.iterrows():
  header_label = (
      f"【{row['書籍細分類別']}】{row['書本編號']}: {row['書名與類型']}"
  )
  with st.expander(header_label):
    col1, col2 = st.columns([1, 2])
    with col1:
      st.markdown(f"**CEFR Level:** `{row['CEFR Level']}`")
      st.markdown(f"**分類標籤:** `{row['書籍細分類別']}`")
    with col2:
      st.markdown(f"**核心主題 (Theme):** {row['包含的核心 Topic/Theme']}")
      st.markdown(f"**Grammar 涵蓋:** {row['包括的 grammar points']}")

    st.info(f"💡 **推薦用途與拆解建議：**\n\n{row['推薦用途']}")