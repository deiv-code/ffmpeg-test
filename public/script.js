class NeonVideoGallery {
    constructor() {
        this.videos = [];
        this.filteredVideos = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadInputVideos();
        await this.loadVideos();
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('colorFilter').addEventListener('change', () => this.filterVideos());
        document.getElementById('effectFilter').addEventListener('change', () => this.filterVideos());
        document.getElementById('refreshBtn').addEventListener('click', () => this.loadVideos());

        // Form controls
        document.getElementById('showCreateForm').addEventListener('click', () => this.showCreateForm());
        document.getElementById('cancelBtn').addEventListener('click', () => this.hideCreateForm());
        document.getElementById('videoForm').addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Range sliders
        document.getElementById('x').addEventListener('input', (e) => {
            document.getElementById('xValue').textContent = e.target.value;
        });
        document.getElementById('y').addEventListener('input', (e) => {
            document.getElementById('yValue').textContent = e.target.value;
        });
    }

    async loadInputVideos() {
        try {
            const response = await fetch('/api/inputs');
            const inputs = await response.json();
            
            const select = document.getElementById('inputVideo');
            select.innerHTML = '<option value="">Select input video...</option>';
            
            inputs.forEach(input => {
                const option = document.createElement('option');
                option.value = input.filename;
                option.textContent = input.name;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load input videos:', error);
        }
    }

    async loadVideos() {
        try {
            const response = await fetch('/api/videos');
            this.videos = await response.json();
            this.filteredVideos = [...this.videos];
            this.renderVideos();
        } catch (error) {
            console.error('Failed to load videos:', error);
            document.getElementById('videoGrid').innerHTML = 
                '<div class="loading">Failed to load videos</div>';
        }
    }

    filterVideos() {
        const colorFilter = document.getElementById('colorFilter').value;
        const effectFilter = document.getElementById('effectFilter').value;

        this.filteredVideos = this.videos.filter(video => {
            const colorMatch = !colorFilter || video.color === colorFilter;
            const effectMatch = !effectFilter || video.effect === effectFilter;
            return colorMatch && effectMatch;
        });

        this.renderVideos();
    }

    renderVideos() {
        const grid = document.getElementById('videoGrid');
        const count = document.getElementById('videoCount');
        
        count.textContent = `${this.filteredVideos.length} video${this.filteredVideos.length !== 1 ? 's' : ''}`;

        if (this.filteredVideos.length === 0) {
            grid.innerHTML = '<div class="loading">No videos found</div>';
            return;
        }

        grid.innerHTML = this.filteredVideos.map(video => `
            <div class="video-card" onclick="this.querySelector('video').play()">
                <video class="video-preview" controls preload="metadata">
                    <source src="/videos/${video.filename}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="video-info">
                    <div class="video-title">${video.name}</div>
                    <div class="video-meta">
                        <span class="color-tag color-${video.color}">${video.color}</span>
                        <span class="effect-tag ${video.effect === 'enhanced' ? 'effect-enhanced' : ''}">${video.effect}</span>
                    </div>
                    <div class="video-details">
                        ${video.size} MB • ${new Date(video.created).toLocaleDateString()}
                    </div>
                </div>
            </div>
        `).join('');
    }

    showCreateForm() {
        document.getElementById('createForm').classList.remove('hidden');
        document.getElementById('showCreateForm').style.display = 'none';
    }

    hideCreateForm() {
        document.getElementById('createForm').classList.add('hidden');
        document.getElementById('showCreateForm').style.display = 'block';
        document.getElementById('videoForm').reset();
        document.getElementById('xValue').textContent = '0.5';
        document.getElementById('yValue').textContent = '0.7';
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = {
            inputVideo: document.getElementById('inputVideo').value,
            text: document.getElementById('text').value,
            color: document.getElementById('color').value,
            x: parseFloat(document.getElementById('x').value),
            y: parseFloat(document.getElementById('y').value),
            enhanced: true,
            autoPosition: document.getElementById('autoPosition').checked,
            blurBackground: document.getElementById('blurBackground').checked
        };

        if (!formData.inputVideo || !formData.text) {
            alert('Please fill in all required fields');
            return;
        }

        this.showProgress();

        try {
            const response = await fetch('/api/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.hideProgress();
                this.hideCreateForm();
                await this.loadVideos(); // Refresh gallery
                alert(`✨ Video created successfully: ${result.outputVideo}`);
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            this.hideProgress();
            alert(`❌ Failed to create video: ${error.message}`);
        }
    }

    showProgress() {
        document.getElementById('progress').classList.remove('hidden');
        document.getElementById('createBtn').disabled = true;
    }

    hideProgress() {
        document.getElementById('progress').classList.add('hidden');
        document.getElementById('createBtn').disabled = false;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new NeonVideoGallery();
});