# MP4 Audio to Text Converter

Convert MP4 video files to text using NVIDIA's Whisper Large V3 API and Streamlit.

## Features

- 🎬 Upload MP4 video files
- 🎵 Automatic audio extraction
- 🤖 AI-powered transcription using NVIDIA Whisper Large V3
- ⏱️ Timestamp-based segmentation
- 👥 Speaker identification (numbered)
- 📊 CSV output with structured data
- 💾 Automatic saving to Output folder
- 📥 Download CSV files
- 🎨 Clean and intuitive Streamlit UI

## Prerequisites

- Python 3.8 or higher
- NVIDIA API Key (Get it from [NVIDIA Build](https://build.nvidia.com/))

## Setup

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**
   
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
└── README.md          # This file
```

## How It Works

1. **Upload**: User uploads an MP4 video file
2. **Extract**: The app extracts audio from the video using MoviePy
3. **Transcribe**: Audio is sent to NVIDIA's Whisper API with timestamp requests
4. **Process**: Results are parsed and organized with timestamps and speaker identification
5. **Save**: Transcription is saved as CSV in the `Output/` folder (named after the MP4 file)
6. **Display**: Results are shown in a table format with download option

## CSV Output Format

The generated CSV file contains three columns:
- **Seconds in video**: Timestamp of when the speech segment starts
- **Speaker Name/Number**: Identified speaker (e.g., Speaker 1, Speaker 2)
- **Transcribed text**: The actual transcribed text for that segment

## Dependencies

- `streamlit` - Web UI framework
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests to NVIDIA API
- `moviepy` - Video/audio processing
- `pandas` - CSV data handling and table display

## Troubleshooting

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
- Keep your NVIDIA API key confidential

## API Reference

This app uses the [NVIDIA Whisper Large V3 API](https://build.nvidia.com/openai/whisper-large-v3/api)

## License

This project is open source and available for personal and commercial use.

## Support

For issues related to:
- NVIDIA API: Visit [NVIDIA Build](https://build.nvidia.com/)
- This application: Open an issue in the repository
