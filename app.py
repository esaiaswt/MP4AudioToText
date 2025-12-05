import streamlit as st
import os
import tempfile
import csv
import time
import psutil
import keyboard
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
import pandas as pd

# Load environment variables
load_dotenv()

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
RIVA_SERVER = "grpc.nvcf.nvidia.com:443"
FUNCTION_ID = "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"
PYTHON_CLIENT_PATH = Path("python-clients/scripts/asr/transcribe_file_offline.py")

def extract_audio_from_mp4(mp4_file):
    """Extract audio from MP4 file and save as WAV (16-bit, mono)"""
    try:
        # Create a temporary file for the audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Save uploaded file temporarily
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(mp4_file.read())
        temp_video.close()
        
        # Extract audio as WAV (mono, 16-bit)
        video = VideoFileClip(temp_video.name)
        video.audio.write_audiofile(
            temp_audio_path, 
            codec='pcm_s16le',  # 16-bit PCM
            fps=16000,          # 16kHz sample rate
            nbytes=2,           # 2 bytes = 16-bit
            ffmpeg_params=["-ac", "1"],  # Mono audio
            logger=None
        )
        video.close()
        
        # Clean up video file
        os.unlink(temp_video.name)
        
        return temp_audio_path
    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        return None

def transcribe_audio(audio_file_path):
    """Transcribe audio using NVIDIA Riva official Python client"""
    try:
        # Check if python client exists
        if not PYTHON_CLIENT_PATH.exists():
            st.error("Python client not found. Please run: git clone https://github.com/nvidia-riva/python-clients.git")
            return None
        
        # Build command (output goes to stdout)
        cmd = [
            "python",
            str(PYTHON_CLIENT_PATH),
            "--server", RIVA_SERVER,
            "--use-ssl",
            "--metadata", "function-id", FUNCTION_ID,
            "--metadata", "authorization", f"Bearer {NVIDIA_API_KEY}",
            "--language-code", "en",
            "--input-file", audio_file_path,
            "--word-time-offsets",  # Enable word timestamps
            "--output-seglst",  # Output segmented list with timestamps
            "--speaker-diarization",  # Enable speaker diarization
            "--diarization-max-speakers", "5"  # Max 5 speakers
        ]
        
        # Run the transcription
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            st.error(f"Transcription failed: {result.stderr}")
            return None
        
        # Get transcription from stdout
        output = result.stdout.strip()
        
        if not output:
            st.error("No transcription output received")
            return None
        
        # Try to parse JSON from output
        try:
            # Find JSON in output (it may have other text before/after)
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                data = json.loads(json_str)
                
                # Debug: Show JSON structure in expandable section
                with st.expander("🔍 Debug: View JSON Response Structure"):
                    st.json(data)
                
                # Extract results with timestamps
                result_data = {
                    'text': '',
                    'segments': []
                }
                
                if 'results' in data:
                    for result_item in data['results']:
                        if 'alternatives' in result_item and len(result_item['alternatives']) > 0:
                            alternative = result_item['alternatives'][0]
                            transcript = alternative.get('transcript', '').strip()
                            
                            if transcript:
                                # Get the audioProcessed time (end time of this segment)
                                audio_processed = result_item.get('audioProcessed', 0.0)
                                
                                # Extract speaker information from words
                                speaker_tag = None
                                if 'words' in alternative and len(alternative['words']) > 0:
                                    # Use the speaker tag from the first word in this segment
                                    first_word = alternative['words'][0]
                                    speaker_tag = first_word.get('speakerTag', None)
                                    
                                    # Debug: Log speaker detection
                                    if speaker_tag is not None:
                                        st.info(f"✓ Speaker detected: Speaker {int(speaker_tag) + 1} at {audio_processed:.1f}s")
                                
                                result_data['text'] += transcript + ' '
                                result_data['segments'].append({
                                    'start': audio_processed,
                                    'text': transcript,
                                    'speaker': speaker_tag
                                })
                
                result_data['text'] = result_data['text'].strip()
                
                # If no segments found, fall back to extracting just the final transcript
                if not result_data['segments'] and result_data['text']:
                    # Look for "Final transcript:" in output
                    final_transcript_marker = "Final transcript:"
                    if final_transcript_marker in output:
                        final_text = output.split(final_transcript_marker, 1)[1].strip()
                        result_data['text'] = final_text
                        result_data['segments'].append({
                            'start': 0.0,
                            'text': final_text
                        })
                
                return result_data if result_data['text'] else None
            else:
                st.error("Could not parse JSON from output")
                return None
                
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse JSON: {e}")
            return None
        
    except subprocess.TimeoutExpired:
        st.error("Transcription timed out. The file may be too large.")
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
                # Use actual speaker tag if available, otherwise fallback to simple numbering
                speaker_tag = segment.get('speaker', None)
                if speaker_tag is not None:
                    speaker_label = f"Speaker {int(speaker_tag) + 1}"  # Convert 0-based to 1-based
                else:
                    speaker_label = f"Speaker {(i % 5) + 1}"  # Fallback to simple numbering
                
                rows.append({
                    'Seconds in video': str(round(segment.get('start', 0))),
                    'Speaker Name/Number': speaker_label,
                    'Transcribed text': segment.get('text', '').strip()
                })
        else:
            # Fallback if no segments available
            rows.append({
                'Seconds in video': '0',
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
    
    # Header with logo and title
    col1, col2 = st.columns([2, 5])
    with col1:
        if os.path.exists("SOI Logo-Screen-Dark BG.png"):
            st.image("SOI Logo-Screen-Dark BG.png", width=540)
    with col2:
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
    
    # Configure max upload size to 2GB
    st.set_option('server.maxUploadSize', 2048)
    
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
    
    # Quit button at the bottom
    if st.button("🚪 Quit Application", type="secondary", use_container_width=True, help="Shutdown the Streamlit server"):
        # Give a bit of delay for user experience
        time.sleep(0.5)
        # Close streamlit browser tab
        keyboard.press_and_release('ctrl+w')
        # Terminate streamlit python process
        pid = os.getpid()
        p = psutil.Process(pid)
        p.terminate()
    
    st.markdown(
        "Powered by [NVIDIA Whisper Large V3](https://build.nvidia.com/openai/whisper-large-v3)"
    )

if __name__ == "__main__":
    main()
