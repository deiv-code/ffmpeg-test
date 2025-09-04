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
                     font_size=None, enhanced=True, blur_background=False):
        """Process video with neon text glow effect"""
        
        # Get color value for true neon glow effect
        neon_color = self.colors.get(color.lower(), self.colors['white'])
        
        # Get font path and calculate size
        font_path = self.get_font_path()
        calculated_font_size = self.calculate_font_size(text, font_size)
        
        # Position calculations
        x_pos = f"w*{x}-text_w/2"
        y_pos = f"h*{y}-text_h/2"
        
        # Support manual line breaks
        processed_text = text.replace('\\n', '\n')
        
        try:
            # Input stream
            input_stream = ffmpeg.input(input_video)
            
            # Base video processing
            if blur_background:
                # Create blurred background
                bg = input_stream.video.filter('scale', 1080, 1920, 
                                             force_original_aspect_ratio='increase').filter(
                    'crop', 1080, 1920).filter('gblur', sigma=15 if enhanced else 10)
                
                # Create main video
                main = input_stream.video.filter('scale', 1080, 1920, 
                                                force_original_aspect_ratio='decrease')
                
                # Overlay main on blurred background
                base = ffmpeg.filter([bg, main], 'overlay', 
                                   x='(W-w)/2', y='(H-h)/2')
            else:
                # Simple crop to fit
                base = input_stream.video.filter('scale', 1080, 1920, 
                                                force_original_aspect_ratio='increase').filter(
                    'crop', 1080, 1920)
            
            # PROPER NEON GLOW: Multi-pass drawtext with shadow effects
            # Keep base video visible throughout - no overlays, no black backgrounds
            final = base  # Start with clean video and never lose it
            
            if enhanced:
                # Enhanced mode: Multiple shadow passes for realistic glow
                # Layer 1: Widest glow using shadow effect
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.3',  # 30% opacity shadow
                    shadowx=0, shadowy=0,  # Centered shadow for glow effect
                    x=x_pos,
                    y=y_pos
                )
                
                # Layer 2: Large glow
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text  
                    shadowcolor=neon_color + '@0.4',  # 40% opacity
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Layer 3: Medium glow
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.5',  # 50% opacity
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Layer 4: Inner glow  
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.7',  # 70% opacity
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Layer 5: Core glow
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.9',  # 90% opacity
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Final layer: Sharp, readable core text
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor=neon_color,  # Full opacity readable text
                    x=x_pos,
                    y=y_pos
                )
                
            else:
                # Standard mode: Simpler 2-shadow glow
                # Outer glow shadow
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.4',  # 40% opacity outer glow
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Inner glow shadow
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor='black@0.0',  # Invisible text
                    shadowcolor=neon_color + '@0.7',  # 70% opacity inner glow
                    shadowx=0, shadowy=0,
                    x=x_pos,
                    y=y_pos
                )
                
                # Core readable text
                final = final.drawtext(
                    text=processed_text,
                    fontfile=font_path,
                    fontsize=calculated_font_size,
                    fontcolor=neon_color,  # Full opacity readable text
                    x=x_pos,
                    y=y_pos
                )
            
            # Output with audio preservation
            output = ffmpeg.output(
                final,
                input_stream.audio,
                output_video,
                vcodec='libx264',
                preset='medium',
                crf=20 if enhanced else 23,
                acodec='aac',
                audio_bitrate='128k'
            )
            
            if enhanced:
                output = output.global_args('-movflags', '+faststart')
            
            # Overwrite output file
            output = output.overwrite_output()
            
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
    parser.add_argument('--enhanced', action='store_true',
                       help='Use enhanced glow effect')
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
            enhanced=args.enhanced,
            blur_background=not args.no_blur_background
        )
        print(f"Output: {args.output_video}")
        
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()