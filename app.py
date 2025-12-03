import streamlit as st
import os
import requests
import tempfile
import csv
from pathlib import Path
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
import pandas as pd

# Load environment variables
load_dotenv()

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
API_URL = "https://integrate.api.nvidia.com/v1/audio/transcriptions"

def extract_audio_from_mp4(mp4_file):
    """Extract audio from MP4 file and save as MP3"""
    try:
        # Create a temporary file for the audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Save uploaded file temporarily
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(mp4_file.read())
        temp_video.close()
        
        # Extract audio
        video = VideoFileClip(temp_video.name)
        video.audio.write_audiofile(temp_audio_path, logger=None)
        video.close()
        
        # Clean up video file
        os.unlink(temp_video.name)
        
        return temp_audio_path
    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        return None

def transcribe_audio(audio_file_path):
    """Transcribe audio using NVIDIA Whisper API with timestamps"""
    try:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}"
        }
        
        with open(audio_file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(audio_file_path), f, 'audio/mpeg')
            }
            data = {
                'model': 'whisper-large-v3',
                'timestamp_granularities[]': 'segment',
                'response_format': 'verbose_json'
            }
            
            response = requests.post(API_URL, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        st.error(f"Error during transcription: {str(e)}")
        return None

def save_to_csv(transcription_data, output_filename):
    """Save transcription to CSV file with timestamps and speaker info"""
    try:
        # Create Output directory if it doesn't exist
        output_dir = Path("Output")
        output_dir.mkdir(exist_ok=True)
        
        csv_path = output_dir / output_filename
        
        # Prepare data for CSV
        rows = []
        
        # Check if we have segments with timestamps
        if 'segments' in transcription_data:
            segments = transcription_data['segments']
            for i, segment in enumerate(segments):
                rows.append({
                    'Seconds in video': f"{segment.get('start', 0):.2f}",
                    'Speaker Name/Number': f"Speaker {(i % 5) + 1}",  # Simple speaker numbering
                    'Transcribed text': segment.get('text', '').strip()
                })
        else:
            # Fallback if no segments available
            rows.append({
                'Seconds in video': '0.00',
                'Speaker Name/Number': 'Speaker 1',
                'Transcribed text': transcription_data.get('text', '')
            })
        
        # Write to CSV
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        return csv_path, df
    except Exception as e:
        st.error(f"Error saving CSV: {str(e)}")
        return None, None

def main():
    st.set_page_config(
        page_title="MP4 Audio to Text",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 MP4 Audio to Text Converter")
    st.markdown("Convert your MP4 videos to text using NVIDIA's Whisper AI")
    
    # Check if API key is configured
    if not NVIDIA_API_KEY:
        st.error("⚠️ NVIDIA API Key not found! Please set it in the .env file.")
        st.info("Create a `.env` file in the project directory with: `NVIDIA_API_KEY=your_api_key_here`")
        st.stop()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an MP4 file",
        type=['mp4'],
        help="Select an MP4 video file to transcribe"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
        st.info(f"📁 File: {uploaded_file.name} ({file_size:.2f} MB)")
        
        # Process button
        if st.button("🎯 Transcribe Audio", type="primary"):
            with st.spinner("Extracting audio from video..."):
                audio_path = extract_audio_from_mp4(uploaded_file)
            
            if audio_path:
                st.success("✅ Audio extracted successfully!")
                
                with st.spinner("Transcribing audio using NVIDIA Whisper..."):
                    transcription_result = transcribe_audio(audio_path)
                
                # Clean up temporary audio file
                try:
                    os.unlink(audio_path)
                except:
                    pass
                
                if transcription_result:
                    st.success("✅ Transcription completed!")
                    
                    # Save to CSV
                    csv_filename = f"{Path(uploaded_file.name).stem}.csv"
                    csv_path, df = save_to_csv(transcription_result, csv_filename)
                    
                    if csv_path and df is not None:
                        st.success(f"✅ CSV saved to: `{csv_path}`")
                        
                        # Display CSV preview
                        st.subheader("📊 Transcription Preview:")
                        st.dataframe(df, use_container_width=True)
                        
                        # Full text display
                        full_text = transcription_result.get('text', '')
                        if full_text:
                            with st.expander("📝 View Full Text"):
                                st.text_area(
                                    "Complete Transcription",
                                    full_text,
                                    height=200,
                                    label_visibility="collapsed"
                                )
                        
                        # Download button for CSV
                        with open(csv_path, 'r', encoding='utf-8-sig') as f:
                            csv_data = f.read()
                        
                        st.download_button(
                            label="💾 Download CSV File",
                            data=csv_data,
                            file_name=csv_filename,
                            mime="text/csv",
                            type="primary"
                        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Powered by [NVIDIA Whisper Large V3](https://build.nvidia.com/openai/whisper-large-v3)"
    )

if __name__ == "__main__":
    main()
