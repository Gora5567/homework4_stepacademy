
import os
import requests as rq
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
from dotenv import load_dotenv
import urllib.parse
from io import BytesIO

load_dotenv()

HF_API_URL = "https://router.huggingface.co/hf-interface/models/black-forest-labs/FLUX.1-schnell"
HF_TOKEN = os.getenv("HF_TOKEN")


def generate_image_hf(prompt):
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"

        response = rq.get(url, timeout=45)

        if response.status_code == 200:
            return response.content, None
        else:
            return None, f"сервис временно недоступен ({response.status_code})"

    except rq.exceptions.Timeout:
        return None, "время ожидания истекло"

    except Exception as e:
        return None, f"ошибка подключения: {e}"


st.title("ai creative studio")
st.write("опиши какое изображение хочешь получить")

prompt = st.text_area("описание изображения")

if st.button("сгенерировать изображение"):

    if prompt.strip():

        with st.spinner("ии генерирует изображение"):

            image_bytes, error = generate_image_hf(prompt)

        if error:
            st.error(error)

        elif image_bytes:
            st.session_state.original_image = image_bytes
            st.session_state.selected_filter = "без фильтра"

    else:
        st.warning("сначала введи описание изображения")


if "original_image" in st.session_state:

    st.header("твоё изображение")

    original_image = Image.open(
        BytesIO(st.session_state.original_image)
    ).convert("RGB")

    st.subheader("выбери фильтр")

    filter_option = st.selectbox(
        "доступные фильтры",
        [
            "без фильтра",
            "чёрно-белый",
            "размытие",
            "резкость",
            "яркость",
            "контраст",
            "насыщенность"
        ]
    )

    filtered_image = original_image.copy()

    if filter_option == "чёрно-белый":
        filtered_image = filtered_image.convert("L")

    elif filter_option == "размытие":
        intensity = st.slider("сила размытия", 1, 10, 3)
        filtered_image = filtered_image.filter(
            ImageFilter.GaussianBlur(intensity)
        )

    elif filter_option == "резкость":
        intensity = st.slider("сила резкости", 1.0, 5.0, 2.0)
        enhancer = ImageEnhance.Sharpness(filtered_image)
        filtered_image = enhancer.enhance(intensity)

    elif filter_option == "яркость":
        intensity = st.slider("уровень яркости", 0.1, 3.0, 1.0)
        enhancer = ImageEnhance.Brightness(filtered_image)
        filtered_image = enhancer.enhance(intensity)

    elif filter_option == "контраст":
        intensity = st.slider("уровень контрастности", 0.1, 3.0, 1.0)
        enhancer = ImageEnhance.Contrast(filtered_image)
        filtered_image = enhancer.enhance(intensity)

    elif filter_option == "насыщенность":
        intensity = st.slider("уровень насыщенности", 0.0, 3.0, 1.0)
        enhancer = ImageEnhance.Color(filtered_image)
        filtered_image = enhancer.enhance(intensity)

    st.subheader("результат обработки")

    st.image(filtered_image, width="stretch")

    if st.button("вернуть оригинал"):
        st.session_state.selected_filter = "без фильтра"
        st.rerun()
