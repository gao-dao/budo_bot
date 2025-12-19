import streamlit as st
from google import genai
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="武術術理チャットボット", layout="wide")
st.title("🥋 心勢会 術理探求 Bot")
st.caption("型稽古の力、術理について応答します。")

# --- 1.5 チャット履歴クリア関数の定義 ---
def clear_chat_history():
    if "messages" in st.session_state:
        del st.session_state["messages"]
    if "chat" in st.session_state:
        del st.session_state["chat"]
    st.rerun()

with st.sidebar:
    st.title("設定")
    if st.button("💬 チャット履歴をクリア"):
        clear_chat_history()

# --- 2. Gemini クライアントの初期化 ---
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") 
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("APIキーが設定されていません。")
            st.stop()
    
    # 安定版の v1 を使用
    client = genai.Client(api_key=api_key)
    return client

client = get_gemini_client()
MODEL_NAME = "gemini-1.5-flash"

# --- 3. チャットセッションの初期化 ---
if "messages" not in st.session_state:
    try:
        with open("budo_knowledge.txt", "r", encoding="utf-8") as f:
            knowledge_text = f.read()
    except FileNotFoundError:
        knowledge_text = ""

    # キャラクター設定を「最初の指示」として定義
    initial_prompt = f"""
    あなたは琉球古伝空手心勢会の代表です。
    以下のルールを厳守して応答してください。

    【語尾のルール】
    ・「〜なのです」「〜なのですよ」「〜ございます」は一切使わず、「〜です」「〜ます」に統一してください。
    ・格調高くも親しみやすい丁寧語で回答してください。

    【回答の指針】
    ・以下の知識ベースに基づき、誠実かつ簡潔に応答してください。
    ・知識にない場合は「現在の知識ベースに含まれておりません」と答えてください。
    ・最後に内容の簡単なまとめをつけてください。

    [武術知識ベース]
    {knowledge_text}
    """
    
    # エラーの元になる config 指定を避け、空の状態でチャットを開始
    st.session_state.chat = client.chats.create(model=MODEL_NAME)
    
    # 最初の指示をAIに送り、設定を覚えさせる（画面には表示しない）
    st.session_state.chat.send_message(initial_prompt)
    
    st.session_state.messages = [{"role": "model", "content": "ようこそ、心勢会へ。武術の術理について、何なりとお尋ねください。"}]

# --- 4. 履歴表示と入力処理 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form(key="chat_form", clear_on_submit=True):
    user_prompt = st.text_area("質問を入力してください", height=100)
    submitted = st.form_submit_button("質問を送信")

if submitted and user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    try:
        response = st.session_state.chat.send_message(user_prompt)
        with st.chat_message("model"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "model", "content": response.text})
    except Exception as e:
        st.error(f"エラーが発生しました。履歴をクリアしてやり直してください: {e}")