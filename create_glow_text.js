#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const VideoAnalyzer = require('./video_analyzer');
let ffmpegPath = require('ffmpeg-static');
if (!fs.existsSync(ffmpegPath) && fs.existsSync(ffmpegPath + '.exe')) {
    ffmpegPath = ffmpegPath + '.exe';
}

class TextGlowProcessor {
    constructor() {
        this.colors = {
            white: ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#000000'],
            red: ['#FFAAAA', '#FF4444', '#FF0000', '#220000'],
            blue: ['#AACCFF', '#4477FF', '#0044FF', '#000022'],
            yellow: ['#FFFFCC', '#FFEE44', '#FFDD00', '#222200'],
            green: ['#AAFFAA', '#44FF44', '#00DD00', '#002200'],
            purple: ['#FFAAFF', '#FF44FF', '#DD00DD', '#220022'],
            orange: ['#FFDDAA', '#FF9944', '#FF7700', '#221100']
        };
    }

    getFontPath() {
        const paths = ['./static/Roboto-Bold.ttf', './fonts/Roboto-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'];
        return paths.find(fs.existsSync) || paths[0];
    }

    buildDrawText(text, fontPath, fontSize, color, opacity, x, y, borderWidth = 0, borderColor = null) {
        const border = borderWidth > 0 ? `:borderw=${borderWidth}:bordercolor=${borderColor}` : '';
        // Support manual line breaks with \n
        const processedText = text.replace(/\\n/g, '\n');
        return `drawtext=text='${processedText}':fontfile=${fontPath}:fontsize=${fontSize}:fontcolor=${color}@${opacity}:x=${x}:y=${y}${border}`;
    }


    async processVideo(options) {
        const { inputVideo, outputVideo, text, color = 'white', x = 0.5, y = 0.7, fontSize, enhanced = true, blurBackground = false, autoPosition = false } = options;
        
        let finalX = x;
        let finalY = y;
        
        // Auto-position text using computer vision
        if (autoPosition) {
            try {
                const analyzer = new VideoAnalyzer();
                const analysis = await analyzer.suggestTextPosition(inputVideo);
                if (analysis.confidence > 0.1) {
                    finalX = analysis.suggestedX;
                    finalY = analysis.suggestedY;
                    console.log(`🎯 Using CV-suggested position: (${finalX}, ${finalY})`);
                } else {
                    console.log('⚠️ CV analysis had low confidence, using manual position');
                }
            } catch (error) {
                console.log('⚠️ CV analysis failed, using manual position:', error.message);
            }
        }
        
        const [core, bright, glow, shadow] = this.colors[color.toLowerCase()] || this.colors.white;
        const fontPath = this.getFontPath();
        
        // Calculate font size based on text length to prevent cutoff
        let calculatedSize;
        if (fontSize) {
            calculatedSize = fontSize;
        } else {
            const baseSize = 80; // Reduced base size
            const maxWidth = 950; // Available width for 1080px output (with margins)
            
            // More accurate character width estimation for Roboto Bold
            const avgCharWidth = baseSize * 0.6; // Roboto Bold is roughly 60% of font size per character
            const estimatedWidth = text.length * avgCharWidth;
            
            if (estimatedWidth > maxWidth) {
                // Scale down proportionally with safety margin
                calculatedSize = Math.floor((maxWidth * 0.9) / (text.length * 0.6));
                calculatedSize = Math.max(calculatedSize, 30); // Minimum readable size
            } else {
                calculatedSize = baseSize;
            }
            
            console.log(`Auto-scaling: "${text}" (${text.length} chars) -> ${calculatedSize}px (estimated width: ${Math.floor(calculatedSize * text.length * 0.6)}px)`);
        }
        const fontSizeCalc = calculatedSize;
        
        const xPos = `w*${finalX}-text_w/2`;
        const yPos = `h*${finalY}-text_h/2`;

        // Build filter chain
        const filters = blurBackground ? [
            `[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,${enhanced ? 'gblur=sigma=15' : 'boxblur=20'}[bg]`,
            `[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[main]`,
            `[bg][main]overlay=(W-w)/2:(H-h)/2[base]`
        ] : [
            `[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base]`
        ];

        // Generate glow layers dynamically
        const glowLayers = enhanced ? 
            [
                { color: glow, opacity: 0.3, border: 20, borderOpacity: 0.2 },
                { color: glow, opacity: 0.5, border: 15, borderOpacity: 0.3 },
                { color: bright, opacity: 0.7, border: 10, borderOpacity: 0.5 },
                { color: bright, opacity: 0.85, border: 6, borderOpacity: 0.7 },
                { color: core, opacity: 0.95, border: 3, borderOpacity: 0.9 }
            ] : [
                { color: glow, opacity: 0.4, border: 15, borderOpacity: 0.25 },
                { color: glow, opacity: 0.6, border: 10, borderOpacity: 0.4 },
                { color: bright, opacity: 0.8, border: 6, borderOpacity: 0.6 },
                { color: bright, opacity: 0.9, border: 3, borderOpacity: 0.8 }
            ];

        let currentLayer = 'base';
        glowLayers.forEach((layer, i) => {
            const nextLayer = `glow${i + 1}`;
            filters.push(`[${currentLayer}]${this.buildDrawText(text, fontPath, fontSizeCalc, layer.color, layer.opacity, xPos, yPos, layer.border, `${layer.color}@${layer.borderOpacity}`)}[${nextLayer}]`);
            currentLayer = nextLayer;
        });

        // Final bright text (no shadows)
        const finalBorder = enhanced ? `${bright}@0.8` : `${bright}@0.5`;
        filters.push(`[${currentLayer}]${this.buildDrawText(text, fontPath, fontSizeCalc, core, 1.0, xPos, yPos, 1, finalBorder)}[final]`);

        const ffmpegArgs = [
            '-i', inputVideo,
            '-filter_complex', filters.join(';'),
            '-map', '[final]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'medium', 
            '-crf', enhanced ? '20' : '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            ...(enhanced ? ['-movflags', '+faststart'] : []),
            '-y', outputVideo
        ];

        return this.runFFmpeg(ffmpegArgs);
    }

    runFFmpeg(args) {
        return new Promise((resolve, reject) => {
            console.log('Running FFmpeg...');
            const ffmpeg = spawn(ffmpegPath, args);
            let stderr = '';
            
            ffmpeg.stderr.on('data', (data) => {
                stderr += data.toString();
                if (data.toString().includes('time=')) process.stdout.write('.');
            });
            
            ffmpeg.on('close', (code) => {
                console.log('\n');
                if (code === 0) {
                    console.log('✅ Video processing completed successfully!');
                    resolve();
                } else {
                    console.error('❌ FFmpeg failed:', stderr);
                    reject(new Error(`FFmpeg failed with code ${code}`));
                }
            });
            
            ffmpeg.on('error', reject);
        });
    }
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
        console.log(`
Usage: node create_glow_text.js <input_video> <output_video> <text> [options]

Options:
  --color <color>     red, blue, yellow, white, green, purple, orange (default: white)
  --x <0-1>          Horizontal position (default: 0.5)
  --y <0-1>          Vertical position (default: 0.7)
  --size <pixels>    Font size (default: auto)
  --auto-position    Use computer vision to find optimal text placement
  --blur-background  Use blurred background (default: crop to fit)

Examples:
  node create_glow_text.js input.mp4 output.mp4 "GOAL!" --color red --y 0.8
  node create_glow_text.js video.mov result.mp4 "NEWS" --color blue
        `);
        process.exit(1);
    }

    const [inputVideo, outputVideo, text] = args;
    const options = { inputVideo, outputVideo, text };
    
    for (let i = 3; i < args.length; i += 2) {
        const [flag, value] = [args[i], args[i + 1]];
        switch (flag) {
            case '--color': options.color = value; break;
            case '--x': options.x = parseFloat(value); break;
            case '--y': options.y = parseFloat(value); break;
            case '--size': options.fontSize = parseInt(value); break;
            case '--auto-position': options.autoPosition = true; i--; break;
            case '--blur-background': options.blurBackground = true; i--; break;
        }
    }

    const processor = new TextGlowProcessor();
    console.log(`🎬 Processing: ${text} (${options.color || 'white'})`);
    
    processor.processVideo(options)
        .then(() => console.log(`✨ Output: ${outputVideo}`))
        .catch(error => { console.error('❌ Failed:', error.message); process.exit(1); });
}

module.exports = TextGlowProcessor;