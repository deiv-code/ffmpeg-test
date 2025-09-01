const express = require('express');
const fs = require('fs');
const path = require('path');
const TextGlowProcessor = require('./create_glow_text');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.static('public'));
app.use(express.json());
app.use('/videos', express.static('./', { 
    setHeaders: (res, path) => {
        if (path.endsWith('.mp4')) {
            res.set('Content-Type', 'video/mp4');
        }
    }
}));

// Get all video files with metadata
app.get('/api/videos', (req, res) => {
    try {
        const videoFiles = fs.readdirSync('.')
            .filter(file => file.endsWith('.mp4'))
            .map(file => {
                const stats = fs.statSync(file);
                const name = path.parse(file).name;
                
                // Parse metadata from filename patterns
                let color = 'unknown';
                let effect = 'standard';
                
                if (name.includes('neon_')) color = name.split('neon_')[1]?.split('_')[0] || 'unknown';
                if (name.includes('test_')) color = name.split('test_')[1]?.split('_')[0] || 'unknown';
                if (name.includes('enhanced') || name.includes('neon')) effect = 'enhanced';
                
                return {
                    filename: file,
                    name: name,
                    color: color,
                    effect: effect,
                    size: Math.round(stats.size / 1024 / 1024 * 100) / 100, // MB
                    created: stats.mtime,
                    duration: 'Unknown' // Could add ffprobe integration later
                };
            })
            .sort((a, b) => new Date(b.created) - new Date(a.created));
            
        res.json(videoFiles);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read video files' });
    }
});

// Create new video with neon text effect
app.post('/api/create', async (req, res) => {
    try {
        const { inputVideo, text, color, x, y, enhanced, autoPosition, blurBackground, fontSize } = req.body;
        
        if (!inputVideo || !text) {
            return res.status(400).json({ error: 'Missing required fields: inputVideo, text' });
        }
        
        // Generate output filename
        const timestamp = Date.now();
        const outputVideo = `neon_${color || 'white'}_${timestamp}.mp4`;
        
        const processor = new TextGlowProcessor();
        const options = {
            inputVideo,
            outputVideo,
            text,
            color: color || 'white',
            x: x || 0.5,
            y: y || 0.7,
            enhanced: enhanced || false,
            autoPosition: autoPosition || false,
            blurBackground: blurBackground || false,
            fontSize: fontSize || null
        };
        
        console.log(`🎬 Web request: Creating "${text}" in ${color} at (${x}, ${y})`);
        
        await processor.processVideo(options);
        
        res.json({ 
            success: true, 
            outputVideo,
            message: `Video created successfully: ${outputVideo}`
        });
        
    } catch (error) {
        console.error('Video creation error:', error);
        res.status(500).json({ 
            error: 'Video creation failed', 
            details: error.message 
        });
    }
});

// Get available input videos
app.get('/api/inputs', (req, res) => {
    try {
        const inputFiles = fs.readdirSync('.')
            .filter(file => file.match(/\.(mp4|mov|avi)$/i) && !file.startsWith('neon_') && !file.startsWith('test_'))
            .map(file => ({
                filename: file,
                name: path.parse(file).name
            }));
            
        res.json(inputFiles);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read input files' });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`🌐 Neon Text Web Interface running at http://localhost:${PORT}`);
    console.log(`📁 Serving videos from: ${__dirname}`);
    console.log(`🎨 Ready to create neon text effects!`);
});