import streamlit as st
from google import genai
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="武術術理チャットボット", layout="wide")
st.title("🥋 手の探究 術理探求 Bot")

# --- 2. クライアント初期化 ---
@st.cache_resource
def get_client():
    # Secretsから直接読み込むことで、古い環境変数の干渉を完全に防ぎます
    try:
        # st.secrets.get ではなく、[] で直接指定して確実に取得します
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Secretsの読み込みに失敗しました。設定を確認してください。")
        st.stop()

client = get_client()

# --- 3. チャット管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 知識ベースの読み込み
    try:
        with open("budo_knowledge.md", "r", encoding="utf-8") as f:
            knowledge = f.read()
    except:
        knowledge = ""

    # システム指示（キャラクター設定）
    st.session_state.sys_prompt = f"""
    あなたは琉球古伝空手心勢会の術理を擬人化した存在です。
    ・「〜なのです」は禁止。「〜です」「〜ます」で話してください。
    ・以下の知識に基づいて簡潔に答えてください。
    【心勢会知識ベース】に名前や事実の記載がない場合、あなたの想像や一般知識で名前を創作したり、似た名前を当てはめたりすることは絶対に禁止します。
    【重要指示】
    回答の最後には必ず「まとめ」という見出しを付け、今回の回答の要点を3行以内の箇条書きで簡潔にまとめて締めくくってください。
    {knowledge}
    """
    st.session_state.messages.append({"role": "model", "content": "ようこそ。ご質問をどうぞ。"})

# --- 4. 履歴表示 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. 入力処理 ---
if prompt := st.chat_input("質問を入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 送信用にシステム指示を結合
    full_prompt = f"{st.session_state.sys_prompt}\n\nユーザーの質問: {prompt}"

    try:
        # モデル名を最新の Gemini 3 Flash Preview に変更
        response = client.models.generate_content(
            model="gemini-1.5-flash-preview", 
            contents=full_prompt
        )
        answer = response.text
        
        # --- ここから追加：画面に回答を表示し、履歴に保存する ---
        with st.chat_message("model"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "model", "content": answer})
        # --------------------------------------------------
        
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")