# FFmpeg Neon Text Glow Effect

Create YouTube Shorts-style videos with professional neon text glow effects using FFmpeg. Recreates After Effects Deep Glow and drop shadow effects.

## Quick Start

```bash
npm install
npm start             # Launch web interface at http://localhost:3000
```

Or use command line:
```bash
node create_glow_text.js input.mp4 output.mp4 "YOUR TEXT" --color red --y 0.8
```

## Commands

### Web Interface
```bash
npm start             # Launch web gallery at http://localhost:3000
npm run dev           # Same as npm start
```

### Command Line Usage
```bash
node create_glow_text.js <input_video> <output_video> <text> [options]
```

### NPM Scripts
```bash
npm start             # Launch web interface
npm test              # Run test suite with sample videos
npm run example       # Run example with default settings
npm run glow          # Launch the glow text script (command line)
```

### Command Options

| Option | Description | Values | Default |
|--------|-------------|--------|---------|
| `--color` | Text color | red, blue, yellow, white, green, purple, orange | white |
| `--x` | Horizontal position | 0-1 (0=left, 1=right) | 0.5 |
| `--y` | Vertical position | 0-1 (0=top, 1=bottom) | 0.7 |
| `--size` | Font size in pixels | Any number | Auto-calculated |
| `--blur-background` | Use blurred background | Flag (no value) | false (crops to fit) |

## Examples

### Basic Examples
```bash
# Red text at bottom
node create_glow_text.js input.mp4 output.mp4 "AMAZING GOAL!" --color red --y 0.8

# Blue text with neon glow (enhanced by default)
node create_glow_text.js video.mov result.mp4 "BREAKING NEWS" --color blue

# Custom positioning
node create_glow_text.js clip.avi output.mp4 "EPIC WIN" --color yellow --x 0.3 --y 0.4

# Long text (auto-scales to fit)
node create_glow_text.js input.mp4 output.mp4 "THIS IS A VERY LONG TEXT EXAMPLE" --color green

# Manual line breaks
node create_glow_text.js input.mp4 output.mp4 "AMAZING\\nGOAL!" --color red
```

### Advanced Examples
```bash
# Purple neon with blur background
node create_glow_text.js input.mp4 output.mp4 "NEON SIGN" --color purple --blur-background

# Large yellow text at top
node create_glow_text.js video.mp4 result.mp4 "HEADLINE" --color yellow --y 0.2 --size 120

# Green text centered
node create_glow_text.js input.mov output.mp4 "CENTER TEXT" --color green --x 0.5 --y 0.5
```

## Input/Output Support

### Tested Video Formats & Codecs ✅
- **MP4**: H.264, H.265/HEVC ✅
- **MOV**: H.264 ✅  
- **AVI**: XVID/MPEG-4 ✅
- **WebM**: VP9 (supported) ✅

### Input Specifications
- **Aspect Ratios**: 16:9, 9:16, 4:3, 3:4, any custom ratio ✅
- **Resolutions**: 480p → 4K (tested up to 3840x2160) ✅
- **Frame Rates**: 24fps, 25fps, 30fps, 60fps ✅
- **Audio Codecs**: AAC, MP3, PCM ✅

### Output
- **Format**: MP4 (H.264 + AAC)
- **Resolution**: 1080x1920 (9:16 YouTube Shorts format)
- **Processing**: Crops/scales to fit 9:16 without letterboxing
- **Audio**: Preserves original audio with 128kbps AAC encoding
- **Quality**: Enhanced neon glow by default

## Color Presets

| Color | Main Text | Glow Effect | Best For |
|-------|-----------|-------------|----------|
| **white** | Pure white | Bright white glow | High contrast, any background |
| **red** | Bright red | Intense red neon | Sports, alerts, excitement |
| **blue** | Electric blue | Cool blue glow | Tech, calm, professional |
| **yellow** | Bright yellow | Golden glow | Attention, warnings, energy |
| **green** | Neon green | Electric green | Success, money, nature |
| **purple** | Magenta | Purple neon | Creative, luxury, mystery |
| **orange** | Bright orange | Warm orange glow | Energy, enthusiasm, fall |

## Technical Details

### Neon Effect Layers
1. **Outer Glow**: Large, soft glow simulating neon tube atmosphere
2. **Medium Glow**: Mid-range illumination for depth
3. **Inner Glow**: Bright, intense inner light
4. **Core Text**: Blazing bright center text for maximum impact

### Text Fitting
- **Auto-scaling**: Long text automatically reduces font size to fit screen width
- **Manual breaks**: Use `\\n` for explicit line breaks (e.g., "LINE 1\\nLINE 2")
- **Margins**: Text stays within 85% of screen width for optimal mobile viewing
- **Minimum size**: Font won't scale below 40% of base size for readability

### Font
- **Default**: Roboto Bold (included in `static/` directory)
- **Fallback**: System fonts if Roboto unavailable
- **Style**: Bold weight for maximum neon visibility

### Output Quality
- **Standard Mode**: Good quality, faster processing
- **Enhanced Mode**: Higher quality with more glow layers and better compression
- **Resolution**: 1080x1920 (9:16 aspect ratio)
- **Codec**: H.264 with AAC audio

## Troubleshooting

### No Audio in Output
Audio should be automatically preserved. If missing:
1. Check input video has audio: `ffmpeg -i input.mp4` 
2. Ensure FFmpeg version supports AAC encoding

### Font Issues
If text doesn't appear:
1. Verify Roboto fonts are in `./static/` directory
2. Script automatically falls back to system fonts

### Performance
- Use `--enhanced` for better quality (slower)
- Standard mode for faster processing
- Processing time depends on video length and complexity

## Version History

- **v1.0**: Initial release with basic glow effect
- **v1.1**: Added neon illumination with multiple glow layers
- **v1.2**: Roboto font integration and code optimization
- **v1.3**: Removed default blur background, added crop-to-fit scaling