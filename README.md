# MP4 Audio to Text Converter

Convert MP4 video files to text using NVIDIA's Whisper Large V3 API and Streamlit.

## Features

- 🎬 Upload MP4 video files
- 🎵 Automatic audio extraction
- 🤖 AI-powered transcription using NVIDIA Whisper Large V3
- ⏱️ Timestamp-based segmentation
- 👥 **Speaker diarization** - Automatically identifies and differentiates between speakers
- 📊 CSV output with structured data
- 💾 Automatic saving to Output folder
- 📥 Download CSV files
- 🎨 Clean and intuitive Streamlit UI

## Prerequisites

- Python 3.8 or higher
- NVIDIA API Key (Get it from [NVIDIA Build](https://build.nvidia.com/))
- Git (for cloning NVIDIA Riva Python client)

## Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/esaiaswt/MP4AudioToText.git
   cd MP4AudioToText
   ```

2. **Clone NVIDIA Riva Python client**
   ```bash
   git clone https://github.com/nvidia-riva/python-clients.git
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r python-clients/requirements.txt
   ```

4. **Configure your API key**
   
   Create a `.env` file in the project directory:
   ```
   NVIDIA_API_KEY=your_api_key_here
   ```
   
   You can use `.env.example` as a template:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual API key.

## Usage

1. **Run the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   
   The app will automatically open at `http://localhost:8501`

3. **Upload and transcribe**
   - Click "Browse files" to upload an MP4 video
   - Click "Transcribe Audio" to start the conversion
   - Wait for the transcription to complete
   - View the results in a structured table format
   - Download the CSV file (automatically saved in `Output/` folder)
   - CSV includes: Seconds in video, Speaker Name/Number, Transcribed text

## Project Structure

```
MP4AudioToText/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env               # API key configuration (not in git)
├── .env.example       # Template for environment variables
├── .gitignore         # Git ignore rules
├── Output/            # Generated CSV files (not in git)
├── python-clients/    # NVIDIA Riva Python client (not in git)
└── README.md          # This file
```

## How It Works

1. **Upload**: User uploads an MP4 video file
2. **Extract**: The app extracts audio from the video as WAV (16-bit, mono, 16kHz) using MoviePy
3. **Transcribe**: Audio is sent to NVIDIA's Whisper API via the official Riva Python client with gRPC
4. **Process**: Results are parsed from JSON with accurate timestamps from the API response
5. **Save**: Transcription is saved as CSV in the `Output/` folder (named after the MP4 file)
6. **Display**: Results are shown in a table format with download option

## CSV Output Format

The generated CSV file contains three columns:
- **Seconds in video**: Timestamp (rounded to nearest second) of when the speech segment ends
- **Speaker Name/Number**: Automatically identified speaker using AI-powered speaker diarization (e.g., Speaker 1, Speaker 2, etc.). The system can distinguish up to 5 different speakers.
- **Transcribed text**: The actual transcribed text for that segment

**Note**: Speaker diarization uses NVIDIA Riva's built-in AI capability to analyze voice characteristics and automatically assign speaker labels. This is not based on order but on actual voice patterns.

## Dependencies

- `streamlit` - Web UI framework
- `python-dotenv` - Environment variable management
- `moviepy` - Video/audio processing
- `pandas` - CSV data handling and table display
- `psutil` - Process management for quit functionality
- `keyboard` - Keyboard control for quit functionality
- `nvidia-riva-client` - Official NVIDIA Riva gRPC client (installed via python-clients)

## Troubleshooting

### Python Client Not Found
If you get "Python client not found" error:
```bash
git clone https://github.com/nvidia-riva/python-clients.git
pip install -r python-clients/requirements.txt
```

### API Key Not Found
Make sure your `.env` file exists in the project root and contains:
```
NVIDIA_API_KEY=your_actual_key
```

### MoviePy Installation Issues
If you encounter issues with MoviePy on Windows, you may need to install FFmpeg:
```bash
# Using chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### Module Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

## Security Notes

- ⚠️ Never commit your `.env` file to version control
- The `.gitignore` file is configured to exclude `.env` automatically
- The `Output/` folder (containing transcription results) is also excluded from Git
- The `python-clients/` folder is also excluded from Git
- Keep your NVIDIA API key confidential

## Technical Details

- Uses NVIDIA Riva gRPC API via official Python client
- Audio extracted as 16-bit PCM WAV, mono channel, 16kHz sample rate
- Supports automatic punctuation and word-level timestamps
- **Speaker diarization** enabled with support for up to 5 speakers
- AI-powered speaker identification based on voice characteristics
- Segmented output with ~30 second intervals
- CSV format with rounded timestamps for easy reading

## API Reference

This app uses the [NVIDIA Whisper Large V3 API](https://build.nvidia.com/openai/whisper-large-v3/api) via the official [NVIDIA Riva Python Client](https://github.com/nvidia-riva/python-clients)

## License

This project is open source and available for personal and commercial use.

## Support

For issues related to:
- NVIDIA API: Visit [NVIDIA Build](https://build.nvidia.com/)
- NVIDIA Riva Client: Check [python-clients repository](https://github.com/nvidia-riva/python-clients)
- This application: Open an issue in the repository
