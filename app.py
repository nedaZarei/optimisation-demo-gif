import streamlit as st

st.set_page_config(
    page_title="Artemis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #020617; }
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
footer, #MainMenu { display: none !important; }
.block-container {
    padding: 1.5rem 2.5rem 2rem !important;
    max-width: 1060px !important;
    margin: 0 auto !important;
}
[data-testid="stCustomComponentV1"] iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/llm_demo.py", title="LLM",  icon="🤖"),
    st.Page("pages/asr_demo.py", title="ASR",  icon="🎙️"),
])
pg.run()
