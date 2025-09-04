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
 
    def process_video(self, input_video, output_video, text, color='white', x=0.5, y=0.7,
                  font_size=None, blur_background=False):
        """Process video with true neon glow using blur and blend"""

        neon_color = self.colors.get(color.lower(), self.colors['white'])
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, font_size)

        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        processed_text = text.replace('\\n', '\n').replace("'", r"\'")  # Escape quotes

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

            # Method 1: True glow using zero-offset shadow technique
            # Creates authentic glow that emanates from text itself
            final = ffmpeg.drawtext(
                base,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color,                # Use glow color for text
                shadowcolor=neon_color + '@0.6',     # Semi-transparent glow underneath
                shadowx=0,                           # Zero offset for true glow effect
                shadowy=0,                           # Zero offset for true glow effect  
                x=x_pos,
                y=y_pos
            )

            # Output with audio
            output = ffmpeg.output(
                final,
                input_stream.audio,
                output_video,
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
    
    def process_video_advanced_glow(self, input_video, output_video, text, color='white', x=0.5, y=0.7,
                                font_size=None, blur_background=False):
        """Process video with advanced neon glow using multiple blur layers"""

        neon_color = self.colors.get(color.lower(), self.colors['white'])
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, font_size)

        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        processed_text = text.replace('\\n', '\n').replace("'", r"\'")

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

            # Create multiple glow layers using transparent backgrounds (text-only blur)
            transparent = ffmpeg.input('color=black@0.0:size=1080x1920:duration=30', f='lavfi')

            # Create text-only glow layers with different blur levels
            glow_layers = []
            
            # Huge outer glow (most radiant) 
            glow_huge = ffmpeg.drawtext(
                transparent,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color + '@0.4',  # Semi-transparent for layering
                x=x_pos,
                y=y_pos
            ).filter('gblur', sigma=25)  # Very large blur
            glow_layers.append(glow_huge)

            # Large outer glow  
            glow_large = ffmpeg.drawtext(
                transparent,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color + '@0.5',
                x=x_pos,
                y=y_pos
            ).filter('gblur', sigma=15)  # Large blur
            glow_layers.append(glow_large)

            # Medium glow
            glow_medium = ffmpeg.drawtext(
                transparent,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color + '@0.6',
                x=x_pos,
                y=y_pos
            ).filter('gblur', sigma=8)  # Medium blur
            glow_layers.append(glow_medium)

            # Small inner glow
            glow_small = ffmpeg.drawtext(
                transparent,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color + '@0.7',
                x=x_pos,
                y=y_pos
            ).filter('gblur', sigma=3)  # Small blur
            glow_layers.append(glow_small)

            # Overlay all glow layers onto the base video
            current = base
            for glow in glow_layers:
                current = ffmpeg.overlay(current, glow)

            # Add final sharp text on top
            final = ffmpeg.drawtext(
                current,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color,
                x=x_pos,
                y=y_pos
            )

            # Output with audio
            output = ffmpeg.output(
                final,
                input_stream.audio,
                output_video,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='aac',
                audio_bitrate='128k'
            ).global_args('-movflags', '+faststart').overwrite_output()

            print('Running FFmpeg with advanced glow...')
            ffmpeg.run(output, quiet=False)
            print('Video processing completed successfully!')

        except ffmpeg.Error as e:
            print(f"FFmpeg failed: {e}")
            raise
        except Exception as e:
            print(f"Processing failed: {e}")
            raise

    def process_video_clean_glow(self, input_video, output_video, text, color='white', x=0.5, y=0.7,
                                font_size=None, blur_background=False):
        """Process video using clean split/blur/overlay approach for text-only glow"""
        
        neon_color = self.colors.get(color.lower(), self.colors['white'])
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, font_size)

        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        processed_text = text.replace('\\n', '\n').replace("'", r"\'")

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

            # Create transparent background for text-only glow
            transparent = ffmpeg.input('color=black@0.0:size=1080x1920:duration=30', f='lavfi')
            
            # Draw semi-transparent text on transparent background
            glow_alpha = 0.7
            text_glow = ffmpeg.drawtext(
                transparent,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color + f'@{glow_alpha}',
                x=x_pos,
                y=y_pos
            )
            
            # Apply blur only to the text layer to create glow
            glow_blurred = text_glow.filter('gblur', sigma=15)
            
            # Overlay the blurred text glow onto the video
            with_glow = ffmpeg.overlay(base, glow_blurred)
            
            # Add final sharp text on top
            final = ffmpeg.drawtext(
                with_glow,
                text=processed_text,
                fontfile=font_path,
                fontsize=calculated_font_size,
                fontcolor=neon_color,
                x=x_pos,
                y=y_pos
            )

            # Output with audio
            output = ffmpeg.output(
                final,
                input_stream.audio,
                output_video,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='aac',
                audio_bitrate='128k'
            ).global_args('-movflags', '+faststart').overwrite_output()

            print('Running FFmpeg with clean glow...')
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
  python text_glow_processor.py video.mov result.mp4 "NEWS" --color blue --advanced
  python text_glow_processor.py clip.avi output.mp4 "EPIC WIN" --color yellow --x 0.3 --y 0.4
        """
    )
    
    parser.add_argument('input_video', help='Input video file')
    parser.add_argument('output_video', help='Output video file')
    parser.add_argument('text', help='Text to overlay')
    
    parser.add_argument('--color', default='white',
                       choices=['white', 'red', 'blue', 'yellow', 'green', 'purple', 'orange', 'cyan', 'pink', 'lime', 'magenta', 'aqua'],
                       help='Text color (default: white)')
    parser.add_argument('--x', type=float, default=0.5,
                       help='Horizontal position 0-1 (default: 0.5)')
    parser.add_argument('--y', type=float, default=0.7,
                       help='Vertical position 0-1 (default: 0.7)')
    parser.add_argument('--size', type=int, help='Font size in pixels (default: auto)')
    parser.add_argument('--no-blur-background', action='store_true',
                       help='Use simple crop to fit (default: blurred background with centered video)')
    parser.add_argument('--advanced', action='store_true',
                       help='Use advanced multi-layer glow effect (slower but better quality)')
    parser.add_argument('--clean', action='store_true',
                       help='Use clean split/blur/overlay glow effect (recommended for best quality)')
    
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
        if args.clean:
            processor.process_video_clean_glow(
                args.input_video,
                args.output_video,
                args.text,
                color=args.color,
                x=args.x,
                y=args.y,
                font_size=args.size,
                blur_background=not args.no_blur_background
            )
        elif args.advanced:
            processor.process_video_advanced_glow(
                args.input_video,
                args.output_video,
                args.text,
                color=args.color,
                x=args.x,
                y=args.y,
                font_size=args.size,
                blur_background=not args.no_blur_background
            )
        else:
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