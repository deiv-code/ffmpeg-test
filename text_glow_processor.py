#!/usr/bin/env python3

import ffmpeg
import os
import sys
import argparse
import math


class TextGlowProcessor:
    def __init__(self):
        # Enhanced neon color palette: intense, electric colors for maximum glow
        self.colors = {
            'white': '#FFFFFF',
            'red': '#FF0033',
            'blue': '#0099FF',      # Electric blue  
            'yellow': '#FFFF00',
            'green': '#00FF33',     # Brighter electric green
            'purple': '#FF00FF',
            'orange': '#FF6600',
            'cyan': '#00FFFF',      # Bright cyan
            'pink': '#FF0099',      # Hot pink
            'lime': '#66FF00',      # Electric lime
            'magenta': '#FF0066',   # Electric magenta
            'aqua': '#00FF99'       # Electric aqua
        }
    
    def get_font_path(self):
        """Find available font path with fallbacks"""
        paths = [
            './static/Roboto-Bold.ttf',
            './fonts/Roboto-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return paths[0]  # Return first path as default even if not exists
    
    def calculate_font_size(self, text, custom_size=None):
        """Calculate optimal font size based on text length"""
        if custom_size:
            return custom_size
        
        base_size = 80
        max_width = 950  # Available width for 1080px output (with margins)
        
        # Character width estimation for Roboto Bold
        avg_char_width = base_size * 0.6
        estimated_width = len(text) * avg_char_width
        
        if estimated_width > max_width:
            # Scale down proportionally with safety margin
            calculated_size = math.floor((max_width * 0.9) / (len(text) * 0.6))
            calculated_size = max(calculated_size, 30)  # Minimum readable size
        else:
            calculated_size = base_size

        print(f"Auto-scaling: \"{text}\" ({len(text)} chars) -> {calculated_size}px (estimated width: {math.floor(calculated_size * len(text) * 0.6)}px)")
        return calculated_size
 
    def process_video(self, input_video, output_video, text, color='yellow', glow_alpha=0.2):
        """Process video using blend-based approach for enhanced text glow effects"""
        
        neon_color = self.colors.get(color.lower(), self.colors['yellow'])
        # Fixed settings
        glow_neon_color = neon_color  # Glow same color as text
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, None)
        
        # Fixed position settings
        x = 0.5
        y = 0.7
        shadow_offset = 3
        
        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        # Shadow position (offset to the right)
        shadow_x_pos = f"w*{x}-text_w/2+{shadow_offset}"
        shadow_y_pos = f"h*{y}-text_h/2+{shadow_offset}"
        processed_text = text.replace('\\n', '\n').replace("'", r"\'")

        # Get input video duration for dynamic glow duration
        try:
            probe = ffmpeg.probe(input_video)
            duration = float(probe['streams'][0]['duration'])
            print(f"Detected video duration: {duration:.2f} seconds")
        except (KeyError, ValueError, Exception) as e:
            print(f"Could not detect duration ({e}), using fallback of 60 seconds")
            duration = 60  # Fallback duration

        try:
            input_stream = ffmpeg.input(input_video)

            # Fixed: Use blurred background
            bg = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='increase') \
                                .filter('crop', 1080, 1920) \
                                .filter('gblur', sigma=15)
            main = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
            base = ffmpeg.overlay(bg, main, x='(W-w)/2', y='(H-h)/2')

            # Use raw filter_complex approach to replicate Node.js glow effect exactly
            # This ensures proper filter graph construction for blur-based glow
            
            # Fixed filter complex chain with optimal settings
            filter_complex = []
            
            # Scale and crop base video with blurred background
            filter_complex.extend([
                '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=15[bg]',
                '[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[main]',
                '[bg][main]overlay=(W-w)/2:(H-h)/2[base]'
            ])
            
            # Create integrated glow effect - glow first, then sharp text over it
            filter_complex.append(f'nullsrc=size=1080x1920:duration={duration}[null]')
            
            # Create glow layer with alpha transparency for exact color matching
            drawtext_glow = f'drawtext=text=\'{processed_text}\':fontfile={font_path}:fontsize={calculated_font_size}:fontcolor={glow_neon_color}@{glow_alpha}:x={x_pos}:y={y_pos}'
            filter_complex.append(f'[null]{drawtext_glow}[glow_txt]')

            # Apply blur to create glow effect (increased blur for more diffuse glow)
            filter_complex.append('[glow_txt]gblur=sigma=2.0[glow]')
            
            # Apply glow to base video using direct overlay (preserves exact colors)
            filter_complex.append('[base][glow]overlay[with_glow_bg]')
            
            # Skip post-blur (fixed: disabled)
            
            # Add shadow layer (fixed: 0.6 opacity)
            drawtext_shadow = f'drawtext=text=\'{processed_text}\':fontfile={font_path}:fontsize={calculated_font_size}:fontcolor=black@0.6:x={shadow_x_pos}:y={shadow_y_pos}'
            filter_complex.append(f'[with_glow_bg]{drawtext_shadow}[with_shadow]')
            
            # Now add sharp, bright text over the shadow and glow for integrated effect
            drawtext_final = f'drawtext=text=\'{processed_text}\':fontfile={font_path}:fontsize={calculated_font_size}:fontcolor={neon_color}:x={x_pos}:y={y_pos}'
            filter_complex.append(f'[with_shadow]{drawtext_final}[final]')
            
            # Create output with raw filter_complex
            output = ffmpeg.output(
                input_stream,
                output_video,
                filter_complex=';'.join(filter_complex),
                **{
                    'map:v': '[final]',
                    'map:a': '0:a'
                },
                vcodec='libx264',
                preset='fast', 
                crf=23,
                acodec='aac',
                audio_bitrate='128k'
            ).global_args('-movflags', '+faststart').overwrite_output()

            print('Running FFmpeg...')
            ffmpeg.run(output, quiet=False)
            print('Video processing completed successfully!')

        except ffmpeg.Error as e:
            print(f"FFmpeg failed: {e}")
            raise
        except Exception as e:
            print(f"Processing failed: {e}")
            raise


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Create YouTube Shorts-style videos with neon text glow effects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_glow_processor.py input.mp4 output.mp4 "ARE YOU OK?"
  python text_glow_processor.py video.mov result.mp4 "NEWS" --color blue  
  python text_glow_processor.py clip.avi output.mp4 "EPIC WIN" --color red
        """
    )
    
    parser.add_argument('input_video', help='Input video file')
    parser.add_argument('output_video', help='Output video file')
    parser.add_argument('text', help='Text to overlay')
    
    parser.add_argument('--color', default='yellow',
                       choices=['white', 'red', 'blue', 'yellow', 'green', 'purple', 'orange', 'cyan', 'pink', 'lime', 'magenta', 'aqua'],
                       help='Text color (default: yellow)')

    parser.add_argument('--glow-alpha', type=float, default=0.25, metavar='0.0-1.0',
                       help='Glow transparency/intensity (0.0-1.0, default: 0.3)')
    
    args = parser.parse_args()
    
    processor = TextGlowProcessor()
    print(f"Processing: {args.text} ({args.color})")
    
    try:
        processor.process_video(
            args.input_video,
            args.output_video,
            args.text,
            color=args.color,
            glow_alpha=getattr(args, 'glow_alpha', 0.2)
        )
        print(f"Output: {args.output_video}")
        
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()