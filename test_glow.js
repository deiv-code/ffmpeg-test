#!/usr/bin/env node

const TextGlowProcessor = require('./create_glow_text');
const { execSync } = require('child_process');
const fs = require('fs');

async function createTestVideo() {
    // Create a simple test video if none exists
    const testVideoPath = './test_input.mp4';
    
    if (!fs.existsSync(testVideoPath)) {
        console.log('📹 Creating test video...');
        try {
            let ffmpegPath = require('ffmpeg-static');
            if (!fs.existsSync(ffmpegPath) && fs.existsSync(ffmpegPath + '.exe')) {
                ffmpegPath = ffmpegPath + '.exe';
            }
            execSync(`"${ffmpegPath}" -f lavfi -i "testsrc2=duration=10:size=1920x1080:rate=30" -f lavfi -i "sine=frequency=1000:duration=10" -c:v libx264 -c:a aac -shortest -y ${testVideoPath}`, 
                { stdio: 'inherit' });
            console.log('✅ Test video created');
        } catch (error) {
            console.error('❌ Failed to create test video:', error.message);
            return;
        }
    }

    const processor = new TextGlowProcessor();
    
    // Test different configurations
    const tests = [
        {
            output: './test_white_glow.mp4',
            text: 'AMAZING GOAL!',
            color: 'white',
            y: 0.8
        },
        {
            output: './test_red_glow.mp4', 
            text: 'BREAKING NEWS',
            color: 'red',
            y: 0.7
        },
        {
            output: './test_blue_enhanced.mp4',
            text: 'EPIC MOMENT',
            color: 'blue',
            y: 0.3,
            enhanced: true
        }
    ];

    for (const test of tests) {
        console.log(`\n🎨 Testing: ${test.text} (${test.color})`);
        try {
            const options = {
                inputVideo: testVideoPath,
                outputVideo: test.output,
                text: test.text,
                color: test.color,
                y: test.y
            };

            options.enhanced = test.enhanced || false;
            await processor.processVideo(options);
            
            console.log(`✅ Created: ${test.output}`);
        } catch (error) {
            console.error(`❌ Failed to create ${test.output}:`, error.message);
        }
    }
}

if (require.main === module) {
    createTestVideo().catch(console.error);
}

module.exports = { createTestVideo };