import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from streamlit_cropper import st_cropper
import io

# 🌟 1. पेज कॉन्फ़िगरेशन और प्रीमियम डार्क/मॉडर्न थीम
st.set_page_config(page_title="PixelCraft | Professional Image Studio", page_icon="🎨", layout="wide")

# कस्टम CSS फॉर ब्यूटीफुल UI
st.markdown("""
    <style>
    .main { background-color: #0f111a; color: #ffffff; }
    .stButton>button {
        background: linear-gradient(45deg, #ff4b4b, #ff7676);
        color: white; border-radius: 8px; border: none;
        font-weight: bold; width: 100%; padding: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(255,75,75,0.4); }
    .css-1r6slb0 { background-color: #161925; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    div[data-testid="stSidebarUserContent"] { background-color: #161925; padding-top: 20px; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; font-weight: 700; color: #ffffff; }
    .status-box { background-color: #1e2235; border-left: 5px solid #00fff0; padding: 15px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 🌟 2. हेडर सेक्शन
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🎨 PixelCraft Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888cbd; font-size: 18px;'>The Ultimate Interactive Web Image Editor</p>", unsafe_allow_html=True)
st.markdown("---")

# 🌟 3. साइडबार कंट्रोल्स (Clean Grouping)
st.sidebar.markdown("<h2 style='color: #ff4b4b; text-align: center;'>🛠️ Control Panel</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# इमेज अपलोडर
uploaded_file = st.sidebar.file_uploader("📂 Upload Studio Image", type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file is not None:
    # इमेज लोड करें
    original_image = Image.open(uploaded_file)
    
    # ⚙️ टैब आधारित एडिटिंग (Interactive Tabs)
    tab1, tab2, tab3 = st.sidebar.tabs(["✨ Filters & Tuning", "📐 Transform & Crop", "🎨 Color Modes"])
    
    with tab1:
        st.markdown("### 🎛️ Fine Tuning")
        brightness = st.slider("☀️ Brightness", 0.1, 3.0, 1.0, 0.1)
        contrast = st.slider("🌗 Contrast", 0.1, 3.0, 1.0, 0.1)
        sharpness = st.slider("🎯 Sharpness", 0.1, 5.0, 1.0, 0.1)
        
        st.markdown("### 🌪️ Artistic Effects")
        blur_amount = st.slider("💧 Gaussian Blur", 0, 15, 0, 1)
        emboss = st.checkbox("🎭 Emboss Effect")
        contour = st.checkbox("✏️ Sketch / Contour Line")

    with tab2:
        st.markdown("### ✂️ Smart Dynamic Crop")
        enable_crop = st.checkbox("🔓 Enable Cropping Tool", value=False)
        box_aspect = st.selectbox("Aspect Ratio", [None, "1:1", "16:9", "4:3"])
        aspect_dict = {"1:1": (1,1), "16:9": (16,9), "4:3": (4,3), None: None}
        
        st.markdown("### 🔄 Orientation")
        rotate_deg = st.slider("🔄 Rotate (Degrees)", 0, 360, 0, 90)
        flip_mode = st.radio("↔️ Flip Image", ["None", "Horizontal (Left-Right)", "Vertical (Up-Down)"])

    with tab3:
        st.markdown("### 🌈 Aesthetic Palettes")
        color_mode = st.selectbox("Select Theme/Mode", ["Vibrant Color", "Cinematic Grayscale", "Vintage Sepia", "Invert Colors"])

    # 🌟 4. इमेज प्रोसेसिंग इंजन (Sequential Execution)
    edited_image = original_image.copy()

    # रोटेशन और फ्लिप (पहला स्टेप)
    if rotate_deg > 0:
        edited_image = edited_image.rotate(rotate_deg, expand=True)
    if flip_mode == "Horizontal (Left-Right)":
        edited_image = ImageOps.mirror(edited_image)
    elif flip_mode == "Vertical (Up-Down)":
        edited_image = ImageOps.flip(edited_image)

    # ट्यूनिंग फिल्टर्स
    if brightness != 1.0:
        edited_image = ImageEnhance.Brightness(edited_image).enhance(brightness)
    if contrast != 1.0:
        edited_image = ImageEnhance.Contrast(edited_image).enhance(contrast)
    if sharpness != 1.0:
        edited_image = ImageEnhance.Sharpness(edited_image).enhance(sharpness)

    # इफ़ेक्ट फिल्टर्स
    if blur_amount > 0:
        edited_image = edited_image.filter(ImageFilter.GaussianBlur(blur_amount))
    if emboss:
        edited_image = edited_image.filter(ImageFilter.EMBOSS)
    if contour:
        edited_image = edited_image.filter(ImageFilter.CONTOUR)

    # कलर मोड्स
    if color_mode == "Cinematic Grayscale":
        edited_image = edited_image.convert("L")
    elif color_mode == "Invert Colors":
        if edited_image.mode == "RGBA":
            r,g,b,a = edited_image.split()
            rgb_img = Image.merge('RGB', (r,g,b))
            inv_img = ImageOps.invert(rgb_img)
            r,g,b = inv_img.split()
            edited_image = Image.merge('RGBA', (r,g,b,a))
        else:
            edited_image = ImageOps.invert(edited_image.convert("RGB"))
    elif color_mode == "Vintage Sepia":
        if edited_image.mode != "RGB":
            edited_image = edited_image.convert("RGB")
        w, h = edited_image.size
        pixels = edited_image.load()
        for py in range(h):
            for px in range(w):
                r, g, b = pixels[px, py]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))

    # 🌟 5. मेन वर्कस्पेस लेआउट (Main Workspace UI)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 📤 Canvas Viewport")
        if enable_crop:
            st.warning("📐 Drag the box on the image below to crop live!")
            edited_image = st_cropper(edited_image, realtime_update=True, box_color='#ff4b4b', aspect_ratio=aspect_dict[box_aspect])
        else:
            st.image(original_image, caption=f"Original File | Size: {original_image.width}x{original_image.height}", use_container_width=True)

    with col2:
        st.markdown("### 🚀 Live Render Output")
        st.image(edited_image, caption=f"Edited File | Size: {edited_image.width}x{edited_image.height}", use_container_width=True)
        
        # लाइव मेटाडेटा कार्ड
        st.markdown(f"""
        <div class="status-box">
            <h4>📊 Image Metadata Analysis</h4>
            <p><b>Resolution:</b> {edited_image.width} x {edited_image.height} Pixels</p>
            <p><b>Color Space Mode:</b> {edited_image.mode}</p>
        </div>
        """, unsafe_allow_html=True)

    # 🌟 6. डाउनलोड बार (Sticky Premium Action Area)
    st.markdown("---")
    img_byte_arr = io.BytesIO()
    save_format = "PNG" if original_image.format in ["PNG", "BMP"] else "JPEG"
    
    # सेव करने से पहले सेपिया या अन्य मोड्स को ठीक करना अगर वो L मोड में हैं
    final_to_save = edited_image.convert("RGB") if save_format == "JPEG" and edited_image.mode in ["L", "RGBA"] else edited_image
    final_to_save.save(img_byte_arr, format=save_format)
    img_byte_arr = img_byte_arr.getvalue()

    d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
    with d_col2:
        st.download_button(
            label="📥 EXPORT HIGH-RES IMAGE",
            data=img_byte_arr,
            file_name=f"pixelcraft_export.{save_format.lower()}",
            mime=f"image/{save_format.lower()}"
        )
else:
    # एम्प्टी स्टेट (Attractive Empty State UI)
    st.markdown("""
        <div style="text-align: center; padding: 80px; background-color: #161925; border-radius: 15px; border: 2px dashed #3f445b; margin-top: 30px;">
            <h2 style="color: #888cbd;">👋 Welcome to PixelCraft Studio!</h2>
            <p style="color: #5b5f7a; font-size: 16px;">To activate the neural graphics engines and begin editing, please drop an image in the left panel sidebar.</p>
        </div>
    """, unsafe_allow_html=True)
