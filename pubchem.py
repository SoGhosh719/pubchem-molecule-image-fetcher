import os
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from tempfile import mkdtemp
import subprocess
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

    # ✅ Correct API request for fetching images
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

# ✅ Function to fetch and download the SDF file
def fetch_3d_conformer_sdf(molecule_name):
    if not molecule_name:
        return None
    
    # Correct API request for downloading 3D conformer SDF file
    sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule_name}/record/SDF?record_type=3d"

    response = requests.get(sdf_url, stream=True)

    if response.status_code == 200:
        sdf_path = f"{molecule_name}_3d_conformer.sdf"
        
        with open(sdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        return sdf_path
    else:
        return None

# ✅ Function to create a PyMOL script for rendering the video
def create_pymol_script(sdf_path, output_video_path):
    script_content = f"""
load {sdf_path}
set ray_trace_frames, 1
set ray_trace_mode, 1
set ray_opaque_background, 0
mset 1 x360
util.mroll 1, 360, 1
mpng {output_video_path.replace('.mp4', '')}
"""
    script_path = f"{sdf_path.replace('.sdf', '')}.pml"
    with open(script_path, 'w') as script_file:
        script_file.write(script_content)
    
    return script_path

# ✅ Function to run PyMOL script and convert PNG frames to MP4
def run_pymol_script(script_path, output_video_path):
    subprocess.run(["pymol", "-cq", script_path])

    # Convert the PNG frames to MP4 using FFmpeg
    frame_pattern = output_video_path.replace('.mp4', '') + "_*.png"
    ffmpeg_command = f"ffmpeg -framerate 24 -i {frame_pattern} -c:v libx264 -pix_fmt yuv420p {output_video_path}"
    subprocess.run(ffmpeg_command.split())

# ✅ Separate Button for Downloading 3D Conformer Animation in MP4 Format
if st.button("🎥 Download 3D Conformer Video"):
    sdf_path = fetch_3d_conformer_sdf(molecule_name)

    if sdf_path:
        st.success("✅ 3D Conformer SDF File Downloaded Successfully!")
        output_video_path = f"{molecule_name}_3d_conformer.mp4"
        script_path = create_pymol_script(sdf_path, output_video_path)
        run_pymol_script(script_path, output_video_path)
        
        st.success("✅ 3D Conformer Video Created Successfully!")
        with open(output_video_path, "rb") as f:
            st.download_button("⬇️ Download 3D Conformer Video (MP4)", f, file_name=f"{molecule_name}_3D_Conformer.mp4", mime="video/mp4")
    else:
        st.error("❌ 3D Conformer Video Not Available for this Molecule.")

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
    match = process.extractOne(user_question, faq_data.keys())  # Ensure proper tuple handling

    if match:  # Ensure a valid match exists
        best_match = match[0]  # Extract the best-matched question
        confidence = match[1]  # Extract the confidence score

        if confidence > 75:  # Acceptable confidence threshold
            return faq_data[best_match]  # Return the answer mapped to the closest question

    return "🤖 Sorry, I couldn't understand your question. Try rephrasing!"

# 🔹 Streamlit UI
st.sidebar.write("Ask me anything about the Molecule Image to Video Converter!")
user_input = st.sidebar.text_input("🔍 Type your question below:")

if user_input:
    answer = get_best_match(user_input)
    st.sidebar.write(f"🤖 Answer: {answer}")
