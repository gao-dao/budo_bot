import streamlit as st
from google import genai
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="武術術理チャットボット", layout="wide")
st.title("🥋 心勢会 術理探求 Bot")
st.caption("型稽古の力、術理について応答します。")

# --- 1.5 チャット履歴クリア関数の定義 ---
def clear_chat_history():
    """セッションの状態をリセットし、新しいチャットを開始する"""
    if "messages" in st.session_state:
        del st.session_state["messages"]
    if "chat" in st.session_state:
        del st.session_state["chat"]
    st.rerun()

# サイドバーにクリアボタンを配置（または st.title の下などお好きな場所に）
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
            st.error("エラー: APIキーが設定されていません。")
            st.stop()
    if not api_key:
        st.error("エラー: APIキーが空です。")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    return client

client = get_gemini_client()
# 最新のSDKに最適な名称に変更します
MODEL_NAME = "gemini-2.0-flash"
# --- 3. 知識ファイルの読み込みとチャットセッションの初期化 ---
if "messages" not in st.session_state:
    try:
        with open("budo_knowledge.txt", "r", encoding="utf-8") as f:
            knowledge_text = f.read()
    except FileNotFoundError:
        st.error("知識ファイルが見つかりません。")
        knowledge_text = ""

    system_instruction = f"""
    あなたは琉球古伝空手心勢会な代表です。
    以下の知識ベースに基づき、テキストの文体に沿った表現を忠実に守り文末の語尾などもテキストのトーンにそのままに回答してください。
    文末日は〜なのですよ〜ございますなどは使わず、ですます調で統一してください
　　 知識ベースにない質問には、「その情報については、現在の知識ベースに含まおりません」と応答してください。
    最後に返答の内容の簡単なまとめもつけてください。

    [武術知識ベース]
    {knowledge_text}
    """
    
    config = genai.types.GenerateContentConfig(
        system_instruction=system_instruction
    )
    
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME,
        config=config,
    )
    st.session_state.messages = [{"role": "model", "content": "ようこそ、術理探求の道へ。武術に関するご質問は何でしょうか？"}]


# --- 4. 既存のチャット履歴の表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. ユーザー入力とAI応答の処理 ---
with st.form(key="chat_form", clear_on_submit=True):
    user_prompt = st.text_area(
        "質問を入力してください", 
        key="user_input_area",
        height=100,
        placeholder="武術に関するご質問を入力し、「質問を送信」ボタンを押してください。"
    )
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
        st.error(f"応答中にエラーが発生しました: {e}")