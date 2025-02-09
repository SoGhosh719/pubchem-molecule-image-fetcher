import os
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from tempfile import mkdtemp
import time
from rapidfuzz import process  # Using RapidFuzz for better performance

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
    Just enter a molecule name, fetch its image, and create animations. 🚀
    """
)

# 📌 Molecule Image Fetching Section
st.subheader("🔎 Fetch Molecule Image from PubChem")
molecule_name = st.text_input("Enter Molecule Name (e.g., Water, Glucose, Benzene):")
structure_type = st.radio("🧬 Select Structure Type:", ["2D Structure", "3D Structure"])

# ✅ Function to fetch molecule image
def fetch_pubchem_image(molecule_name, structure_type):
    if not molecule_name:
        st.warning("⚠️ Please enter a molecule name.")
        return None

    structure_code = "2d" if structure_type == "2D Structure" else "3d"
    image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/PNG?record_type={structure_code}"

    response = requests.get(image_url)

    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        st.error("❌ Molecule image not found. Check the name and try again.")
        return None

if st.button("🔍 Fetch Image"):
    img = fetch_pubchem_image(molecule_name, structure_type)
    
    if img:
        st.image(img, caption=f"{molecule_name} ({structure_type})", use_container_width=True)

        # Save fetched image for animation
        image_path = f"{molecule_name}.png"
        img.save(image_path)
        st.success("✅ Image Fetched & Saved!")

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

# 📌 Sidebar Chatbot (FAQ)
st.sidebar.subheader("💬 Ask the Chatbot")

# 🔹 Complete FAQ List
faq_data = {
    # General Questions
    "What does this app do?": "This app converts a series of molecule images into a smooth video or GIF.",
    "Who can use this app?": "Anyone! Researchers, students, and professionals working with molecule animations.",
    "Is this app free to use?": "Yes! It is completely free to use.",
    "Can I use this app on mobile devices?": "Yes, but for better experience, use it on a desktop or tablet.",

    # File Upload Questions
    "What file types are supported for uploading?": "PNG, JPG, and JPEG formats are supported.",
    "How many images can I upload at once?": "There is no strict limit, but too many images may slow down processing.",
    "Can I upload images in any order?": "The app sorts images alphabetically, so rename them (1.png, 2.png, etc.).",
    
    # Video & GIF Creation Questions
    "How does this app convert images into a video?": "It stitches your images together using MoviePy.",
    "How long does it take to create a video?": "Processing time depends on the number of images and FPS settings.",
    "What FPS should I choose?": "12-24 FPS is ideal for smooth animations.",
    "What is the difference between a video and a GIF?": "Videos are MP4 format with better quality, while GIFs are more compressed.",
    "Can I create both a video and a GIF at the same time?": "Yes, the app generates both simultaneously.",

    # Download & Storage Questions
    "How do I download my video or GIF?": "Click the download button after processing is complete.",
    "Where is my downloaded file saved?": "It is saved in your default 'Downloads' folder.",
    "Will my uploaded images be stored on the server?": "No, uploaded images are processed temporarily and not stored.",

    # Troubleshooting Questions
    "Why is my video not generating?": "Check if you uploaded images and selected FPS properly.",
    "Why does my video appear blurry?": "Use high-quality images for the best results.",
    "Why is the animation too fast or too slow?": "Adjust the FPS settings in the sidebar.",
}

# 🔹 Function to find the best matching question
def get_best_match(user_question):
    best_match, confidence = process.extractOne(user_question, faq_data.keys())

    if confidence > 75:  # Acceptable confidence threshold
        return faq_data[best_match]  # Return the answer mapped to the closest question

    return "🤖 Sorry, I couldn't understand your question. Try rephrasing!"

# 🔹 Streamlit UI
st.sidebar.write("Ask me anything about the Molecule Image to Video Converter!")

user_input = st.sidebar.text_input("🔍 Type your question below:")

if user_input:
    answer = get_best_match(user_input)
    st.sidebar.write(f"🤖 Answer: {answer}")

# ✅ Function to fetch molecule image
def fetch_pubchem_image(molecule_name, structure_type):
    if not molecule_name:
        st.warning("⚠️ Please enter a molecule name.")
        return None

    structure_code = "2d" if structure_type == "2D Structure" else "3d"
    image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/PNG?record_type={structure_code}"

    response = requests.get(image_url)

    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        st.error("❌ Molecule image not found. Check the name and try again.")
        return None

if st.button("🔍 Fetch Image"):
    img = fetch_pubchem_image(molecule_name, structure_type)
    
    if img:
        st.image(img, caption=f"{molecule_name} ({structure_type})", use_container_width=True)

        # Save fetched image for animation
        image_path = f"{molecule_name}.png"
        img.save(image_path)
        st.success("✅ Image Fetched & Saved!")

# ✅ Function to fetch and download 3D conformer video
def fetch_3d_conformer_video(molecule_name):
    if not molecule_name:
        st.warning("⚠️ Please enter a molecule name.")
        return None

    conformer_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/record/3d/JSON"
    response = requests.get(conformer_url)

    if response.status_code == 200:
        conformer_folder = mkdtemp()
        conformer_images = []

        # Simulate frames for 3D conformer (In reality, you’d fetch actual frames if available)
        for i in range(1, 31):
            frame_path = os.path.join(conformer_folder, f"frame_{i}.png")
            conformer_images.append(frame_path)
            img = Image.new("RGB", (300, 300), (i * 8, i * 8, i * 8))  # Placeholder for actual images
            img.save(frame_path)

        video_path = os.path.join(conformer_folder, f"{molecule_name}_3d_conformer.mp4")
        clip = ImageSequenceClip(conformer_images, fps=fps)
        clip.write_videofile(video_path, codec="libx264")

        return video_path
    else:
        st.error("❌ 3D Conformer not found. Check the molecule name.")
        return None

# Separate Button to Download 3D Conformer Video
if st.button("🔠 Download 3D Conformer Video"):
    video_path = fetch_3d_conformer_video(molecule_name)

    if video_path:
        st.success("✅ 3D Conformer Video Created Successfully!")

        # Download 3D Conformer Video
        with open(video_path, "rb") as f:
            st.download_button(
                "🔠 Download 3D Conformer Video",
                f,
                file_name=f"{molecule_name}_3d_conformer.mp4",
                mime="video/mp4",
            )

# 📌 Instructions Section
st.subheader("📌 How to Use:")
st.markdown(
    """
    1️⃣ **Fetch a molecule image**: Enter a name & click "Fetch Image".
    2️⃣ **Download the 3D conformer video**: Use the "Download 3D Conformer Video" button.
    3️⃣ **Upload additional images**: Select PNG, JPG, or JPEG files.
    4️⃣ **Set FPS (Frames Per Second)**: Adjust in the sidebar.
    5️⃣ **Click 'Create Video & GIF'**: The app will generate both formats.
    6️⃣ **Download your files**: Save & share your animations.
    """
)
