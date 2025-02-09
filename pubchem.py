import os
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.editor import VideoFileClip
from tempfile import mkdtemp
import time
from rapidfuzz import process  # Using RapidFuzz for efficient fuzzy matching

# 🎨 Streamlit Page Config
st.set_page_config(page_title="Molecule Animation Creator", page_icon="🔬")

# 📌 Sidebar: User Settings
st.sidebar.header("⚙️ Settings")
fps = st.sidebar.slider("🎞️ Frames Per Second (FPS)", min_value=1, max_value=30, value=12)

# 📌 Main Title & Welcome Message
st.title("🔬 Molecule Image Fetcher & Animation Creator")
st.markdown(
    """
    Convert molecule images into **videos or GIFs** and fetch **molecular structures** from **PubChem**!
    Just enter a molecule name, fetch its image or 3D conformer, and create animations. 🚀
    """
)

# 📌 Molecule Image Fetching Section
st.subheader("🔎 Fetch Molecule Image from PubChem")
molecule_name = st.text_input("Enter Molecule Name (e.g., Water, Glucose, Benzene):")
structure_type = st.radio("🧬 Select Structure Type:", ["2D Structure", "3D Structure"])

# ✅ Function to check if the molecule exists in PubChem
def check_molecule_exists(molecule_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/cids/JSON"
    response = requests.get(url)
    return response.status_code == 200 and "IdentifierList" in response.json()

# ✅ Function to fetch molecule image or 3D conformer
def fetch_pubchem_image(molecule_name, structure_type):
    if not molecule_name:
        st.warning("⚠️ Please enter a molecule name.")
        return None, None

    if not check_molecule_exists(molecule_name):
        st.error("❌ Molecule not found on PubChem. Please check the spelling or try another name.")
        return None, None

    if structure_type == "2D Structure":
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/PNG"
        response = requests.get(image_url)
        
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)), "image"
        else:
            return None, None
    else:  # 3D Structure
        gif_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/record/3D/GIF"
        response = requests.get(gif_url)

        if response.status_code == 200:
            return response.content, "gif"
        else:
            return None, None

if st.button("🔍 Fetch Image"):
    image_data, file_type = fetch_pubchem_image(molecule_name, structure_type)

    if image_data:
        if file_type == "image":
            st.image(image_data, caption=f"{molecule_name} ({structure_type})", use_container_width=True)
            
            # Save fetched image for animation
            image_path = f"{molecule_name}.png"
            image_data.save(image_path)
            st.success("✅ Image Fetched & Saved!")
        
        elif file_type == "gif":  # Convert 3D conformer GIF to MP4
            gif_path = f"{molecule_name}_3D.gif"
            with open(gif_path, "wb") as f:
                f.write(image_data)

            st.image(gif_path, caption=f"3D Conformer of {molecule_name}", use_column_width=True)
            st.success("✅ 3D Conformer GIF Downloaded!")

            # Convert GIF to MP4
            mp4_path = gif_path.replace(".gif", ".mp4")
            clip = VideoFileClip(gif_path)
            clip.write_videofile(mp4_path, codec="libx264")

            st.video(mp4_path)
            with open(mp4_path, "rb") as f:
                st.download_button("⬇️ Download 3D Conformer Video (MP4)", f, file_name=f"{molecule_name}_3D.mp4", mime="video/mp4")

# 📌 Instructions Section
st.subheader("📌 How to Use:")
st.markdown(
    """
    1️⃣ **Fetch a molecule image**: Enter a name & click "Fetch Image".
    2️⃣ **Upload multiple images**: Select PNG, JPG, or JPEG files.
    3️⃣ **Ensure correct order**: Rename images (`1.png`, `2.png`, etc.).
    4️⃣ **Set FPS (Frames Per Second)**: Adjust in the sidebar.
    5️⃣ **Click 'Create Video & GIF'**: The app will generate both formats.
    6️⃣ **Download your files**: Save & share your animations.
    """
)

# 📂 File Upload for Animation
uploaded_files = st.file_uploader("📂 Upload Additional Images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

# ✅ Function to create video & GIF
def create_video_and_gif(folder_path, video_path="output_video.mp4", gif_path="output_animation.gif", fps=12):
    images = sorted(
        [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.endswith((".png", ".jpg", ".jpeg"))]
    )

    if not images:
        st.error("⚠️ No valid images found. Please upload PNG, JPG, or JPEG files.")
        return None, None

    clip = ImageSequenceClip(images, fps=fps)
    
    # Create progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Save as video
    st.info("🎬 Creating Video... This may take a few seconds.")
    clip.write_videofile(video_path, codec="libx264")

    # Save as GIF
    st.info("🖼️ Creating GIF... Please wait.")
    clip.write_gif(gif_path, fps=fps)

    progress_bar.progress(100)
    progress_text.text("✅ Video & GIF Creation Complete!")

    return video_path, gif_path

# 🎬 Video & GIF Creation
if st.button("🎬 Create Video & GIF"):
    if uploaded_files:
        st.info("⏳ Processing images... This may take a few seconds.")
        folder_path = save_uploaded_files(uploaded_files)
        video_path, gif_path = create_video_and_gif(folder_path, fps=fps)

        if video_path and gif_path:
            st.success("✅ Video & GIF Created Successfully! 🎉")
            
            # Download Video
            with open(video_path, "rb") as f:
                st.download_button("⬇️ Download Video", f, file_name="molecule_animation.mp4", mime="video/mp4")

            # Download GIF
            with open(gif_path, "rb") as f:
                st.download_button("🖼️ Download GIF", f, file_name="molecule_animation.gif", mime="image/gif")
    else:
        st.warning("⚠️ Please upload images first.")
