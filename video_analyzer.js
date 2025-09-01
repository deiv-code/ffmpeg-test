const fs = require('fs');
const { spawn } = require('child_process');
let ffmpegPath = require('ffmpeg-static');
if (!fs.existsSync(ffmpegPath) && fs.existsSync(ffmpegPath + '.exe')) {
    ffmpegPath = ffmpegPath + '.exe';
}

class VideoAnalyzer {
    constructor() {
        this.cv = null;
    }

    async initOpenCV() {
        if (!this.cv) {
            // Setup Node.js environment for OpenCV.js
            const { createCanvas, loadImage } = require('canvas');
            const { JSDOM } = require('jsdom');
            
            // Install DOM simulation for Node.js
            if (!global.document) {
                const dom = new JSDOM();
                global.document = dom.window.document;
                global.HTMLCanvasElement = createCanvas().constructor;
                global.HTMLImageElement = loadImage().constructor;
            }
            
            const cvReadyPromise = require('@techstark/opencv-js');
            this.cv = await cvReadyPromise;
            console.log('OpenCV.js initialized for video analysis');
        }
        return this.cv;
    }

    async extractMiddleFrame(inputVideo, outputImage = 'temp_frame.jpg') {
        return new Promise((resolve, reject) => {
            const args = [
                '-i', inputVideo,
                '-vf', 'select=eq(n\\,0)',
                '-vframes', '1',
                '-y', outputImage
            ];

            const ffmpeg = spawn(ffmpegPath, args);
            let stderr = '';

            ffmpeg.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            ffmpeg.on('close', (code) => {
                if (code === 0) {
                    resolve(outputImage);
                } else {
                    reject(new Error(`Frame extraction failed: ${stderr}`));
                }
            });
        });
    }

    async analyzeFrame(imagePath) {
        const cv = await this.initOpenCV();
        const { loadImage } = require('canvas');
        
        try {
            const img = await loadImage(imagePath);
            const canvas = require('canvas').createCanvas(img.width, img.height);
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            const imageData = ctx.getImageData(0, 0, img.width, img.height);
            const src = cv.matFromImageData(imageData);
            
            const gray = new cv.Mat();
            const edges = new cv.Mat();
            
            cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
            cv.Canny(gray, edges, 50, 150);
            
            const height = src.rows;
            const width = src.cols;
            
            const topRegion = edges.roi(new cv.Rect(0, 0, width, Math.floor(height * 0.3)));
            const bottomRegion = edges.roi(new cv.Rect(0, Math.floor(height * 0.7), width, Math.floor(height * 0.3)));
            
            // Count non-zero pixels (edges) in each region
            const topActivity = cv.countNonZero(topRegion);
            const bottomActivity = cv.countNonZero(bottomRegion);
            
            let suggestedY, zone;
            if (topActivity < bottomActivity) {
                suggestedY = 0.15;
                zone = 'top';
            } else {
                suggestedY = 0.8;
                zone = 'bottom';
            }
            
            src.delete();
            gray.delete();
            edges.delete();
            topRegion.delete();
            bottomRegion.delete();
            
            return {
                suggestedX: 0.5,
                suggestedY: suggestedY,
                zone: zone,
                confidence: Math.abs(topActivity - bottomActivity) / Math.max(topActivity, bottomActivity, 1)
            };
            
        } catch (error) {
            console.error('CV analysis error:', error);
            return {
                suggestedX: 0.5,
                suggestedY: 0.7,
                zone: 'bottom',
                confidence: 0
            };
        }
    }

    async suggestTextPosition(inputVideo) {
        try {
            console.log('🔍 Analyzing video for optimal text placement...');
            
            const tempFrame = `temp_frame_${Date.now()}.jpg`;
            await this.extractMiddleFrame(inputVideo, tempFrame);
            
            const analysis = await this.analyzeFrame(tempFrame);
            
            if (fs.existsSync(tempFrame)) {
                fs.unlinkSync(tempFrame);
            }
            
            console.log(`📍 Suggested position: (${analysis.suggestedX}, ${analysis.suggestedY}) in ${analysis.zone} zone (confidence: ${analysis.confidence.toFixed(2)})`);
            
            return analysis;
            
        } catch (error) {
            console.error('Video analysis failed:', error);
            return {
                suggestedX: 0.5,
                suggestedY: 0.7,
                zone: 'bottom',
                confidence: 0
            };
        }
    }
}

module.exports = VideoAnalyzer;