# FFmpeg Neon Text Glow Processor

Create YouTube Shorts-style videos with professional neon text glow effects using Python and FFmpeg. Features authentic blur-based glow effects that simulate real neon lighting.

## Quick Start

```bash
# Install dependencies
pip install ffmpeg-python

# Basic usage with default settings
python text_glow_processor.py input.mp4 output.mp4 "YOUR TEXT" --color cyan

# With custom glow intensity
python text_glow_processor.py input.mp4 output.mp4 "YOUR TEXT" --color cyan --glow-alpha 0.5
```

## Step-by-Step Usage Guide

### 1. Prepare Your Video
- Any video format (MP4, MOV, AVI, WebM, etc.)
- Vertical videos work best but horizontal will be cropped to 9:16
- Audio is automatically preserved

### 2. Choose Your Text and Style
```bash
# Basic command structure
python text_glow_processor.py [input_video] [output_video] "[your_text]" --color [color] --glow-alpha [0.0-1.0]
```

### 3. Select Color and Glow Intensity
- **Colors available**: white, red, blue, yellow, green, purple, orange, cyan, pink, lime, magenta, aqua
- **Glow intensity**: 0.0 (no glow) to 1.0 (maximum glow), default is 0.4

### 4. Run and Check Output
```bash
# Example process
python text_glow_processor.py my_video.mp4 output.mp4 "AMAZING!" --color cyan --glow-alpha 0.6
```

The script will:
- Auto-detect video duration
- Scale text to fit screen width
- Apply blur-based glow effect
- Add shadow for depth
- Output 1080x1920 MP4 ready for social media

## Installation

### Prerequisites
- Python 3.6+
- FFmpeg (installed and available in PATH)

### Install Dependencies
```bash
pip install ffmpeg-python
```

### Font Setup
The script automatically looks for fonts in these locations:
1. `./static/Roboto-Bold.ttf` (recommended)
2. `./fonts/Roboto-Bold.ttf`
3. System fallback: `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`

## Usage

### Command Line Interface
```bash
python text_glow_processor.py <input_video> <output_video> <text> [options]
```

### Options

| Option | Description | Values | Default |
|--------|-------------|--------|---------|
| `--color` | Text and glow color | white, red, blue, yellow, green, purple, orange, cyan, pink, lime, magenta, aqua | yellow |
| `--glow-alpha` | Glow intensity/transparency | 0.0-1.0 (0.0=no glow, 1.0=maximum glow) | 0.4 |

## Examples

## Current Implementation Approach

The text glow processor uses a **multi-layer composition approach** for authentic neon glow effects:

1. **Base Video Processing**: Input video is scaled and cropped to 1080x1920 (9:16) with a blurred background
2. **Glow Layer Creation**: Semi-transparent text is rendered and blurred to create the glow effect
3. **Shadow Layer**: Black shadow text provides depth and contrast
4. **Sharp Text Overlay**: Final bright text is overlaid for crisp readability

### Key Features of Current Implementation
- **Fixed positioning**: Text appears at 70% down the screen (optimized for YouTube Shorts)
- **Auto-scaling**: Font size automatically adjusts based on text length
- **Color-matched glow**: Glow color perfectly matches text color
- **Blur-based glow**: Uses Gaussian blur (sigma=3.0) for realistic neon lighting
- **Multi-layer depth**: Shadow + glow + sharp text for maximum visual impact

### Basic Examples
```bash
# Default yellow neon glow
python text_glow_processor.py input.mp4 output.mp4 "NEON GLOW"

# Cyan glow with default intensity
python text_glow_processor.py video.mp4 result.mp4 "GOAL!" --color cyan

# Red text with subtle glow
python text_glow_processor.py clip.mp4 output.mp4 "WINNER" --color red --glow-alpha 0.3

# Bright lime with maximum glow
python text_glow_processor.py input.mov output.mp4 "EPIC" --color lime --glow-alpha 1.0
```

### Advanced Examples
```bash
# Long text (auto-scales to fit screen)
python text_glow_processor.py input.mp4 output.mp4 "THIS IS A VERY LONG TEXT EXAMPLE" --color lime

# Multi-line text using line breaks
python text_glow_processor.py video.mp4 result.mp4 "LINE 1\\nLINE 2" --color magenta

# No glow effect (sharp text only)
python text_glow_processor.py clip.avi output.mp4 "SHARP TEXT" --color white --glow-alpha 0.0

# Maximum glow for dramatic effect
python text_glow_processor.py video.webm output.mp4 "INTENSE" --color cyan --glow-alpha 1.0
```

## Features

### Authentic Neon Glow Effect
- **Single Layer Glow**: Precise, controlled glow that stays tight to text
- **Blur-Based Lighting**: Uses Gaussian blur to simulate real neon tube lighting  
- **Color Consistency**: Glow perfectly matches text color without tinting
- **No Background Contamination**: Glow effect is isolated to text area only

### Intelligent Text Scaling
- **Auto-sizing**: Automatically calculates optimal font size based on text length
- **Screen Fitting**: Ensures text fits within 90% of screen width with safety margins
- **Minimum Readability**: Won't scale below 30px to maintain legibility
- **Character Width Estimation**: Uses Roboto Bold metrics for accurate sizing

### Video Processing
- **Format Support**: MP4, MOV, AVI, and other FFmpeg-compatible formats
- **Output Format**: 1080x1920 (9:16 YouTube Shorts format)
- **Background Options**:
  - **Blur Background** (default): Blurred background with centered video
  - **Simple Crop**: Direct crop-to-fit scaling
- **Audio Preservation**: Maintains original audio with AAC encoding

## Color Palette

Enhanced neon color palette designed for maximum glow effect:

| Color | Hex Code | Description | Best For |
|-------|----------|-------------|----------|
| **white** | `#FFFFFF` | Pure white | High contrast, any background |
| **red** | `#FF0033` | Electric red | Sports, alerts, excitement |
| **blue** | `#0099FF` | Electric blue | Tech, professional, cool tones |
| **yellow** | `#FFFF00` | Bright yellow | Attention, warnings, energy |
| **green** | `#00FF33` | Electric green | Success, nature, positive |
| **purple** | `#FF00FF` | Magenta | Creative, luxury, artistic |
| **orange** | `#FF6600` | Bright orange | Energy, enthusiasm, warm |
| **cyan** | `#00FFFF` | Bright cyan | Modern, digital, fresh |
| **pink** | `#FF0099` | Hot pink | Fun, vibrant, bold |
| **lime** | `#66FF00` | Electric lime | High energy, modern |
| **magenta** | `#FF0066` | Electric magenta | Bold, dramatic |
| **aqua** | `#00FF99` | Electric aqua | Calm, digital, modern |

## Technical Implementation

### Glow Algorithm
1. **Base Video Processing**: Scale and crop input to 1080x1920 format
2. **Text Rendering**: Draw solid text directly on processed video
3. **Glow Generation**: Create semi-transparent text on transparent background
4. **Blur Application**: Apply Gaussian blur (sigma=6) for authentic glow spread
5. **Glow Overlay**: Overlay blurred glow over base video with text
6. **Final Output**: Encode to MP4 with H.264/AAC for optimal compatibility

### Filter Chain Structure
```
Input Video → Scale/Crop → Add Text → Create Glow Layer → Apply Blur → Overlay Glow → Output
```

### Glow Parameters
- **Opacity**: Configurable alpha (default 0.4) for optimal visibility
- **Blur Radius**: 3 pixels for tight, controlled glow spread  
- **Color Matching**: Identical color values for text and glow
- **Positioning**: Fixed at 70% screen height with centered horizontal alignment
- **Multi-layer**: Shadow (offset +3px) + glow (blurred) + sharp text overlay

## Input/Output Specifications

### Supported Input Formats
- **MP4**: H.264, H.265/HEVC
- **MOV**: H.264, ProRes
- **AVI**: XVID, MPEG-4
- **WebM**: VP8, VP9
- **MKV**: Various codecs

### Output Specifications
- **Container**: MP4
- **Video Codec**: H.264 (libx264)
- **Video Quality**: CRF 23 (high quality)
- **Video Resolution**: 1080x1920 (9:16 aspect ratio)
- **Audio Codec**: AAC
- **Audio Bitrate**: 128kbps
- **Optimization**: Fast start enabled for web playback

### Processing Features
- **Aspect Ratio Handling**: Automatically scales and crops to 9:16 format
- **Audio Preservation**: Maintains original audio track
- **Quality Control**: Optimized encoding settings for file size vs quality
- **Fast Processing**: Efficient filter chain for quick rendering

## Font Configuration

### Default Font Path Resolution
1. `./static/Roboto-Bold.ttf` (primary)
2. `./fonts/Roboto-Bold.ttf` (secondary)  
3. `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` (system fallback)

### Font Requirements
- **Style**: Bold weight recommended for maximum neon visibility
- **Format**: TrueType (.ttf) or OpenType (.otf)
- **Encoding**: Unicode support for special characters

## Performance and Quality

### Processing Speed
- **Typical Processing**: 0.5-2x real-time depending on video length and system specs
- **Optimization**: Single-pass processing with efficient filter chain
- **Memory Usage**: Optimized for standard system memory

### Quality Settings
- **Video Quality**: CRF 23 (visually lossless)
- **Encoding Preset**: Fast (good speed/quality balance)
- **Audio Quality**: 128kbps AAC (broadcast quality)

## Troubleshooting

### Common Issues

#### No Output Video Generated
```bash
# Check input file
ffmpeg -i input.mp4

# Verify Python dependencies
pip list | grep ffmpeg-python
```

#### Text Not Appearing
1. **Font Issues**: Ensure font files are accessible at specified paths
2. **Color Issues**: Try high contrast colors like white or cyan
3. **Positioning**: Check x/y values are between 0.0-1.0

#### Audio Missing from Output
- Input video should have audio track
- Check FFmpeg installation supports AAC encoding
- Original audio is preserved automatically

#### Glow Effect Too Subtle/Strong
- Use `--glow-alpha` parameter to adjust glow intensity (0.0 to 1.0)
- Default is 0.4 - increase for stronger glow, decrease for subtler effect
- For extreme customization, modify `sigma` in code (current: 3.0)

### Performance Tips
- Use shorter videos for testing
- Ensure sufficient disk space for output files
- Close other applications for faster processing

## Version History

- **v2.0**: Complete rewrite in Python with improved glow algorithm
- **v2.1**: Enhanced color palette with 12 neon colors
- **v2.2**: Optimized single-layer glow for better performance
- **v2.3**: Improved text scaling and positioning system
- **v2.4**: Fine-tuned glow parameters for authentic neon effect

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Contributions welcome! Please test thoroughly with various input formats and submit pull requests with clear descriptions of changes.