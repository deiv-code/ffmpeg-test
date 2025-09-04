#!/usr/bin/env python3

import ffmpeg
import os
import sys
import argparse
import math


class TextGlowProcessor:
    def __init__(self):
        # Neon color definitions: single bright core colors for true glow effect
        self.colors = {
            'white': '#FFFFFF',
            'red': '#FF0033',
            'blue': '#0066FF', 
            'yellow': '#FFFF00',
            'green': '#00FF00',  # Electric green like reference image
            'purple': '#FF00FF',
            'orange': '#FF6600',
            'cyan': '#00FFFF'  # Bright aqua/cyan for reference image effect
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
    
 
    def process_video(self, input_video, output_video, text, color='white', x=0.5, y=0.7,
                  font_size=None, blur_background=False):
        """Process video with neon text glow effect (blur only on text)"""

        neon_color = self.colors.get(color.lower(), self.colors['white'])
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, font_size)

        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        processed_text = text.replace('\\n', '\n')

        # Define glow layers (opacity, blur) - optimized for speed
        glow_layers = [
            (0.6, 15),   # outer glow
            (0.8, 6),    # inner glow  
            (1.0, None)  # sharp core text
        ]

        try:
            input_stream = ffmpeg.input(input_video)

            # Prepare base video
            if blur_background:
                bg = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='increase') \
                                    .filter('crop', 1080, 1920) \
                                    .filter('gblur', sigma=15)
                main = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
                base = ffmpeg.overlay(bg, main, x='(W-w)/2', y='(H-h)/2')
            else:
                base = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='increase') \
                                        .filter('crop', 1080, 1920)

            # --- Split base for each layer to avoid multiple outgoing edges ---
            streams = [base]
            for _ in range(len(glow_layers)):
                split_streams = streams[-1].split()
                streams[-1] = split_streams[0]
                streams.append(split_streams[1])
            # streams[0..n-1] for text layers, streams[-1] is clean base

            out = streams[-1]  # start with clean base

            # Draw glow layers sequentially
            for i, (opacity, blur) in enumerate(glow_layers):
                txt = ffmpeg.drawtext(
                    streams[i],
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor=neon_color + f"@{opacity}",
                    x=x_pos,
                    y=y_pos,
                    alpha=1
                )
                if blur:
                    txt = txt.filter('gblur', sigma=blur)
                out = ffmpeg.overlay(out, txt)

            final = out

            # Output with audio - optimized for speed
            output = ffmpeg.output(
                final,
                input_stream.audio,
                output_video,
                vcodec='libx264',
                preset='fast',      # faster encoding
                crf=23,            # slightly lower quality for speed
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
  python text_glow_processor.py input.mp4 output.mp4 "GOAL!" --color red --y 0.8
  python text_glow_processor.py video.mov result.mp4 "NEWS" --color blue
  python text_glow_processor.py clip.avi output.mp4 "EPIC WIN" --color yellow --x 0.3 --y 0.4
        """
    )
    
    parser.add_argument('input_video', help='Input video file')
    parser.add_argument('output_video', help='Output video file')
    parser.add_argument('text', help='Text to overlay')
    
    parser.add_argument('--color', default='white',
                       choices=['white', 'red', 'blue', 'yellow', 'green', 'purple', 'orange', 'cyan'],
                       help='Text color (default: white)')
    parser.add_argument('--x', type=float, default=0.5,
                       help='Horizontal position 0-1 (default: 0.5)')
    parser.add_argument('--y', type=float, default=0.7,
                       help='Vertical position 0-1 (default: 0.7)')
    parser.add_argument('--size', type=int, help='Font size in pixels (default: auto)')
    parser.add_argument('--no-blur-background', action='store_true',
                       help='Use simple crop to fit (default: blurred background with centered video)')
    
    args = parser.parse_args()
    
    # Validate position arguments
    if not (0 <= args.x <= 1):
        print("Error: --x must be between 0 and 1")
        sys.exit(1)
    if not (0 <= args.y <= 1):
        print("Error: --y must be between 0 and 1")
        sys.exit(1)
    
    processor = TextGlowProcessor()
    print(f"Processing: {args.text} ({args.color})")
    
    try:
        processor.process_video(
            args.input_video,
            args.output_video,
            args.text,
            color=args.color,
            x=args.x,
            y=args.y,
            font_size=args.size,
            blur_background=not args.no_blur_background
        )
        print(f"Output: {args.output_video}")
        
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()