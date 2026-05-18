from streamlit_mic_recorder import speech_to_text
import streamlit as st


def get_voice_input():
    """
    Kirajzol egy mikrofon gombot a felületre.
    A böngésző beszédfelismerőjét használja a hang szöveggé alakításához.
    """
    # Egy kis vizuális trükk, hogy szépen jelenjen meg
    st.write("🎤 **Hangvezérlés:**")

    text = speech_to_text(
        language='hu-HU',
        start_prompt="🎙️ Kattints ide és kezdj beszélni",
        stop_prompt="🛑 Diktálás befejezése",
        just_once=True,  # Nagyon fontos: ne küldje el kétszer ugyanazt a szöveget
        key='voice_input_module'
    )

    return text