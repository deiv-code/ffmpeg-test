# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Node.js project for creating YouTube Shorts-style videos with professional text glow effects using FFmpeg. Recreates After Effects Deep Glow and drop shadow effects purely with FFmpeg filters.

## Development Commands

- `npm install` - Install dependencies
- `npm test` - Run test suite creating sample glow videos
- `npm run glow` - Run the main glow text script
- `npm run example` - Run example with sample text

## Usage

### Basic Usage
```bash
node create_glow_text.js input.mp4 output.mp4 "YOUR TEXT" --color white --y 0.7
```

### Advanced Options
- `--color <color>`: red, blue, yellow, white, green, purple, orange
- `--x <0-1>`: Horizontal position (0=left, 0.5=center, 1=right)
- `--y <0-1>`: Vertical position (0=top, 0.5=center, 1=bottom)
- `--enhanced`: Use enhanced glow with better quality
- `--size <pixels>`: Custom font size (auto-calculated if omitted)

### Examples
```bash
# Red text at bottom
node create_glow_text.js input.mp4 output.mp4 "AMAZING GOAL!" --color red --y 0.8

# Blue text with enhanced glow at top
node create_glow_text.js input.mov output.mp4 "BREAKING NEWS" --color blue --y 0.2 --enhanced

# Yellow text positioned custom
node create_glow_text.js input.avi output.mp4 "EPIC MOMENT" --color yellow --x 0.3 --y 0.6
```

## Architecture

- **create_glow_text.js**: Main text glow processor with TextGlowProcessor class
- **test_glow.js**: Test runner for validating different configurations
- **Key Features**:
  - Converts any aspect ratio input to 9:16 (YouTube Shorts format)
  - Multi-layer glow effect simulation (outer, medium, inner glow layers)
  - Drop shadow with multiple depth layers
  - Auto-scaling text for mobile viewing
  - Cross-platform FFmpeg.exe handling

## FFmpeg Filter Chain

The glow effect uses multiple drawtext layers:
1. **Background**: Blurred and scaled input video
2. **Outer Glow**: Large border with low opacity
3. **Medium Glow**: Medium border with higher opacity  
4. **Inner Glow**: Small border with high opacity
5. **Drop Shadow**: Offset black text for depth
6. **Main Text**: Bright, crisp final text layer

## Input/Output Support

- **Input**: Any video format/codec (MP4, MOV, AVI, etc.)
- **Input Ratios**: 16:9, 9:16, 4:3, 3:4, or any custom ratio
- **Output**: 9:16 MP4 optimized for mobile viewing
- **Text Colors**: 7 preset colors with proper glow/shadow combinations
- **Fonts**: Roboto Bold (included in static/ directory)

## Key Dependencies

- `express@^5.1.0` - Web application framework
- `ffmpeg-static@^5.2.0` - Static FFmpeg binaries for Node.js