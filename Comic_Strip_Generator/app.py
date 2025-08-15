import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Configure API key
client = genai.Client()


def generate_comic_strip(prompt: str, style: str):
    full_prompt = (
        f"Generate a 4-panel comic strip in a '{style}' style. "
        f"The comic should be about: {prompt}. "
        f"For each of the 4 panels, provide an image and a short, one-sentence caption for that image. "
        f"The response should be interleaved with an image, then its caption, then the next image, its caption, and so on."
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=full_prompt,
        config=types.GenerateContentConfig(response_modalities=['TEXT','IMAGE'])
    )

    comic_panels = []
    current_image = None
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image_data = part.inline_data.data
            image = Image.open(BytesIO(image_data))
            current_image = image
        elif part.text and current_image is not None:
            caption = part.text
            comic_panels.append((current_image, caption))
    return comic_panels


st.title("🎨 Comic Strip Generator")

# Session state to control box visibility
if "hide_box" not in st.session_state:
    st.session_state.hide_box = False

with st.sidebar:
    st.header("Config")
    user_prompt = st.text_area("Enter the comic prompt:")
    comic_style = st.selectbox("Choose a visual style", ["cartoon", "manga", "pixel art", "3d render"])
    generate_btn = st.button("Generate Comic Strip")

# Show info box only if not hidden
if not st.session_state.hide_box:
    st.markdown(
        """
        <div style="
            background: linear-gradient(180deg, rgba(34,34,34,0.85) 0%, rgba(34,34,34,0) 100%);
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
        ">
            <p style="color: #e0e0e0; font-size: 16px; line-height: 1.6; margin: 0;">
                Create your own <span style="color:#fbbf24;">AI-powered 4-panel comic strip</span> in seconds.  
                Pick a <b>style</b>, describe your idea, and watch your story come alive!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if generate_btn:
    st.session_state.hide_box = True  # Hide the box once generation starts
    with st.spinner("Generating..."):
        panels = generate_comic_strip(user_prompt, comic_style)
        
        if panels:
            st.success("Comic strip generated successfully!\nHere's your comic strip:")
            cols = st.columns(4)
            for i, (image, caption) in enumerate(panels):
                with cols[i]:
                    st.image(image)
                    st.caption(f"Panel {i+1}: {caption}")
