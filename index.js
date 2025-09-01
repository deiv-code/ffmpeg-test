const TextGlowProcessor = require('./create_glow_text');

// Simple usage example
async function example() {
    const processor = new TextGlowProcessor();
    
    console.log('<¬ FFmpeg Text Glow Effect Generator');
    console.log('===================================');
    console.log('');
    console.log('Usage:');
    console.log('  node create_glow_text.js input.mp4 output.mp4 "YOUR TEXT" [options]');
    console.log('');
    console.log('Options:');
    console.log('  --color <color>    Text color: white, red, blue, yellow, green, purple, orange');
    console.log('  --x <0-1>         Horizontal position (0=left, 0.5=center, 1=right)');
    console.log('  --y <0-1>         Vertical position (0=top, 0.5=center, 1=bottom)'); 
    console.log('  --enhanced        Use enhanced glow effect');
    console.log('  --size <pixels>   Custom font size');
    console.log('');
    console.log('Examples:');
    console.log('  npm run example');
    console.log('  node create_glow_text.js video.mp4 output.mp4 "GOAL!" --color red --y 0.8');
    console.log('  node create_glow_text.js clip.mov result.mp4 "NEWS" --color blue --enhanced');
    console.log('');
    console.log('=¡ Run "npm test" to see sample outputs with different effects!');
}

if (require.main === module) {
    example();
}

module.exports = TextGlowProcessor;