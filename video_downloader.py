import time
import subprocess
import json
import os
import re
import threading
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class FixedModernHLSDownloader:
    def __init__(self):
        self.driver = None
        self.cookies = {}
        self.authenticated = False
        self.download_queue = []
        self.current_url = ""
        self.panel_injected = False
        self.monitor_thread = None
        self.running = True
        self.current_download_process = None
        self.current_download_filename = None
        self.download_stats = {
            'start_time': None,
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'eta': 0,
            'progress_percent': 0,
            'current_file': '',
            'status': 'idle'
        }

    def setup_browser(self):
        """Setup Chrome browser with network logging enabled"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.enable', {})

    def inject_welcome_info(self):
        """Show welcome information on first load"""
        welcome_js = """
        // Remove existing welcome if it exists
        const existingWelcome = document.getElementById('hls-welcome-info');
        if (existingWelcome) {
            existingWelcome.remove();
        }

        // Create welcome overlay
        const welcome = document.createElement('div');
        welcome.id = 'hls-welcome-info';
        welcome.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(8px);
                z-index: 999999;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                animation: fadeIn 0.3s ease-out;
            ">
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 500px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 25px 80px rgba(0,0,0,0.3);
                    transform: translateY(0);
                    animation: slideUp 0.4s ease-out;
                ">
                    <h2 style="margin: 0 0 25px 0; font-size: 26px; font-weight: 700;">HLS Video Downloader</h2>
                    <div style="font-size: 16px; line-height: 1.7; margin-bottom: 30px; text-align: left;">
                        <div style="margin-bottom: 18px;"><strong>How it works:</strong></div>
                        <div style="margin-bottom: 12px;">1. Navigate to your video lecture page</div>
                        <div style="margin-bottom: 12px;">2. Click "▶️ Start Recording" in the panel</div>
                        <div style="margin-bottom: 12px;">3. Play the video (let it load for 10+ seconds)</div>
                        <div style="margin-bottom: 12px;">4. Click "⏹️ Stop Recording"</div>
                        <div style="margin-bottom: 12px;">5. Select video, enter filename, add to queue</div>
                        <div style="margin-bottom: 18px;">6. Click "Start Downloads" to process queue</div>
                        <div style="margin-bottom: 18px;"><strong>Tips:</strong></div>
                        <div style="margin-bottom: 10px;">• The panel follows you across pages automatically</div>
                        <div style="margin-bottom: 10px;">• You can minimize the panel and restore it later</div>
                        <div style="margin-bottom: 10px;">• Add multiple videos to queue before downloading</div>
                        <div>• All controls are in the browser - no terminal needed!</div>
                    </div>
                    <button onclick="document.getElementById('hls-welcome-info').remove();" style="
                        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                        border: none;
                        color: white;
                        padding: 15px 30px;
                        border-radius: 12px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 600;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                    " onmouseover="this.style.transform='translateY(-2px) scale(1.02)'; this.style.boxShadow='0 6px 20px rgba(76, 175, 80, 0.4)'" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 4px 15px rgba(76, 175, 80, 0.3)'">
                        Got it! Let's start
                    </button>
                </div>
            </div>

            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { transform: translateY(30px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            </style>
        `;

        document.body.appendChild(welcome);
        """

        try:
            self.driver.execute_script(welcome_js)
        except:
            pass

    def inject_comprehensive_panel(self):
        """Inject a modern comprehensive control panel"""
        try:
            current_url = self.driver.current_url
            if not current_url or 'about:blank' in current_url:
                return False

            panel_js = """
            // Remove existing panel if it exists
            const existingPanel = document.getElementById('hls-comprehensive-panel');
            if (existingPanel) {
                existingPanel.remove();
            }

            // Modern styles and force light mode for inputs
            const modernStyle = document.createElement('style');
            modernStyle.textContent = `
                #hls-comprehensive-panel input {
                    color: #000 !important;
                    background: #fff !important;
                    border: 2px solid #e1e5e9 !important;
                    transition: all 0.3s ease !important;
                }
                #hls-comprehensive-panel input:focus {
                    border-color: #667eea !important;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
                    outline: none !important;
                }
                #hls-comprehensive-panel input::placeholder {
                    color: #666 !important;
                }
                @keyframes panelSlideIn {
                    from { 
                        transform: translateX(100%); 
                        opacity: 0; 
                    }
                    to { 
                        transform: translateX(0); 
                        opacity: 1; 
                    }
                }
                @keyframes progressPulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
                .downloading-pulse {
                    animation: progressPulse 16s ease-in-out infinite;
                }
            `;
            document.head.appendChild(modernStyle);

            // Create the modern comprehensive control panel
            const panel = document.createElement('div');
            panel.id = 'hls-comprehensive-panel';
            panel.innerHTML = `
                <div id="panel-container" style="
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    width: 300px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    border-radius: 16px;
                    padding: 0;
                    z-index: 99999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2), 0 0 0 1px rgba(255,255,255,0.1);
                    backdrop-filter: blur(20px);
                    color: white;
                    font-size: 13px;
                    max-height: 85vh;
                    overflow: hidden;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    animation: panelSlideIn 0.5s ease-out;
                ">
                    <!-- Minimized state header -->
                    <div id="minimized-header" style="display: none; text-align: center; cursor: pointer; padding: 20px;" onclick="restorePanel()">
                        <div style="font-weight: 600; font-size: 15px;">HLS Downloader</div>
                        <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Click to restore</div>
                    </div>

                    <!-- Full panel content -->
                    <div id="panel-content" style="padding: 20px; overflow-y: auto; max-height: 85vh;">
                        <!-- Header with glassmorphism effect -->
                        <div style="
                            text-align: center; 
                            margin-bottom: 20px; 
                            font-weight: 700; 
                            font-size: 16px;
                            padding: 15px;
                            background: rgba(255,255,255,0.1);
                            border-radius: 12px;
                            backdrop-filter: blur(10px);
                            border: 1px solid rgba(255,255,255,0.2);
                        ">
                            HLS Video Downloader
                        </div>

                        <!-- Status Section -->
                        <div id="status-section" style="
                            margin-bottom: 20px; 
                            padding: 15px; 
                            background: rgba(255,255,255,0.1); 
                            border-radius: 12px;
                            border: 1px solid rgba(255,255,255,0.2);
                            backdrop-filter: blur(10px);
                        ">
                            <div style="font-weight: 600; margin-bottom: 8px; font-size: 14px;">Status</div>
                            <div id="current-status" style="font-size: 12px; opacity: 0.9;">Ready to record</div>
                        </div>

                        <!-- Recording Controls -->
                        <div id="recording-controls" style="margin-bottom: 20px;">
                            <div style="font-weight: 600; margin-bottom: 12px; font-size: 14px;">Recording</div>
                            <div style="display: flex; gap: 10px; justify-content: center;">
                                <button id="start-recording" style="
                                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 18px;
                                    border-radius: 10px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                                    flex: 1;
                                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                                ">▶️ Start</button>
                                <button id="stop-recording" style="
                                    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 18px;
                                    border-radius: 10px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                                    opacity: 0.5;
                                    flex: 1;
                                    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
                                " disabled>⏹️ Stop</button>
                            </div>
                        </div>

                        <!-- Video Sources Section -->
                        <div id="sources-section" style="margin-bottom: 20px; display: none;">
                            <div style="font-weight: 600; margin-bottom: 12px; font-size: 14px;">Found Videos</div>
                            <div id="sources-list" style="
                                max-height: 120px; 
                                overflow-y: auto; 
                                margin-bottom: 12px;
                                background: rgba(255,255,255,0.05);
                                border-radius: 8px;
                                padding: 8px;
                            "></div>
                            <input id="filename-input" placeholder="Enter filename..." style="
                                width: 100%;
                                padding: 12px;
                                border: 2px solid #e1e5e9;
                                border-radius: 8px;
                                font-size: 12px;
                                margin-bottom: 12px;
                                box-sizing: border-box;
                                color: #000;
                                background: #fff;
                                transition: all 0.3s ease;
                            ">
                            <div style="display: flex; gap: 10px;">
                                <button id="add-to-queue" style="
                                    background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 16px;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
                                ">Add to Queue</button>
                                <button id="download-now" style="
                                    background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 16px;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
                                ">Download Now</button>
                            </div>
                        </div>

                        <!-- Queue Section -->
                        <div id="queue-section" style="margin-bottom: 20px;">
                            <div style="font-weight: 600; margin-bottom: 12px; font-size: 14px;">
                                Queue (<span id="queue-count">0</span>)
                            </div>
                            <div id="queue-list" style="
                                max-height: 120px; 
                                overflow-y: auto; 
                                margin-bottom: 12px; 
                                font-size: 11px;
                                background: rgba(255,255,255,0.05);
                                border-radius: 8px;
                                padding: 8px;
                            "></div>
                            <div style="display: flex; gap: 10px;">
                                <button id="process-queue" style="
                                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 16px;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                                " disabled>Start Downloads</button>
                                <button id="clear-queue" style="
                                    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                                    border: none;
                                    color: white;
                                    padding: 12px 16px;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    font-weight: 600;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
                                " disabled>Clear All</button>
                            </div>
                        </div>

                        <!-- Download Progress -->
                        <div id="progress-section" style="margin-bottom: 20px; display: none;">
                            <div style="
                                font-weight: 600; 
                                margin-bottom: 12px; 
                                font-size: 14px;
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                            ">
                                <span>📥 Downloading</span>
                                <button id="stop-download" style="
                                    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                                    border: none;
                                    color: white;
                                    padding: 6px 12px;
                                    border-radius: 6px;
                                    cursor: pointer;
                                    font-size: 10px;
                                    font-weight: 600;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
                                ">Stop</button>
                            </div>
                            <div id="progress-filename" style="
                                font-size: 11px; 
                                margin-bottom: 8px;
                                background: rgba(255,255,255,0.1);
                                padding: 8px;
                                border-radius: 6px;
                                font-weight: 500;
                            "></div>
                            <div id="progress-bar" style="
                                width: 100%;
                                height: 12px;
                                background: rgba(255,255,255,0.2);
                                border-radius: 6px;
                                margin-bottom: 8px;
                                overflow: hidden;
                                position: relative;
                            ">
                                <div id="progress-fill" style="
                                    height: 100%;
                                    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
                                    border-radius: 6px;
                                    width: 0%;
                                    transition: width 0.3s ease;
                                    position: relative;
                                "></div>
                            </div>
                            <div id="progress-stats" style="
                                font-size: 11px;
                                background: rgba(255,255,255,0.1);
                                padding: 6px 8px;
                                border-radius: 6px;
                                font-family: monospace;
                            "></div>
                        </div>

                        <!-- Controls -->
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                                <button id="minimize-panel" style="
                                    background: rgba(255,255,255,0.15);
                                    border: 1px solid rgba(255,255,255,0.2);
                                    color: white;
                                    padding: 8px 12px;
                                    border-radius: 6px;
                                    cursor: pointer;
                                    font-size: 11px;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    backdrop-filter: blur(10px);
                                ">Minimize</button>
                                <button id="close-panel" style="
                                    background: rgba(255,255,255,0.15);
                                    border: 1px solid rgba(255,255,255,0.2);
                                    color: white;
                                    padding: 8px 12px;
                                    border-radius: 6px;
                                    cursor: pointer;
                                    font-size: 11px;
                                    flex: 1;
                                    transition: all 0.3s ease;
                                    backdrop-filter: blur(10px);
                                ">Close</button>
                            </div>
                            <!-- Credit -->
                            <div style="
                                text-align: right; 
                                font-size: 9px; 
                                opacity: 0.6; 
                                margin-top: 8px;
                                font-style: italic;
                            ">
                                Made by Maarten
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Add modern button hover styles
            const hoverStyle = document.createElement('style');
            hoverStyle.textContent = `
                #hls-comprehensive-panel button:hover:not(:disabled) {
                    transform: translateY(-2px) scale(1.02);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                }
                #hls-comprehensive-panel button:active:not(:disabled) {
                    transform: translateY(0) scale(1);
                }
                #hls-comprehensive-panel button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none !important;
                }
                .queue-item-completed {
                    background: rgba(76, 175, 80, 0.2) !important;
                    border-left: 4px solid #4CAF50 !important;
                    border-radius: 6px;
                }
                .queue-item-remove {
                    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    cursor: pointer;
                    margin-left: 8px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
                }
                .queue-item-remove:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
                }
            `;
            document.head.appendChild(hoverStyle);

            document.body.appendChild(panel);

            // Initialize state
            if (!window.hlsDownloaderState) {
                window.hlsDownloaderState = {
                    recording: false,
                    capturedSources: [],
                    selectedSource: null,
                    queue: [],
                    downloading: false,
                    minimized: false,
                    completedDownloads: new Set(),
                    removeFromQueue: null,
                    stopDownload: false
                };
            }

            // Global functions
            window.restorePanel = function() {
                document.getElementById('minimized-header').style.display = 'none';
                document.getElementById('panel-content').style.display = 'block';
                document.getElementById('panel-container').style.height = 'auto';
                window.hlsDownloaderState.minimized = false;
            };

            window.removeQueueItem = function(index) {
                // Remove item directly from queue
                if (window.hlsDownloaderState.queue && index >= 0 && index < window.hlsDownloaderState.queue.length) {
                    window.hlsDownloaderState.queue.splice(index, 1);
                    updateQueueDisplay();
                    updatePanelStatus('Item removed from queue.');
                }
            };

            // Button event listeners
            document.getElementById('start-recording').addEventListener('click', () => {
                window.hlsDownloaderState.recording = true;
                window.hlsDownloaderState.capturedSources = [];
                updatePanelStatus('Recording... Play your video now!');
                updateRecordingButtons(true);
            });

            document.getElementById('stop-recording').addEventListener('click', () => {
                window.hlsDownloaderState.recording = false;
                updatePanelStatus('Processing captured data...');
                updateRecordingButtons(false);
                window.hlsDownloaderState.recordingStopped = true;
            });

            document.getElementById('add-to-queue').addEventListener('click', () => {
                const filename = document.getElementById('filename-input').value.trim();
                const source = window.hlsDownloaderState.selectedSource;
                if (source && filename) {
                    source.filename = filename;
                    source.id = Date.now();
                    window.hlsDownloaderState.queue.push(source);
                    updateQueueDisplay();
                    document.getElementById('filename-input').value = '';
                    document.getElementById('sources-section').style.display = 'none';
                    updatePanelStatus('Added to queue! Navigate to next video or start downloads.');
                } else {
                    updatePanelStatus('Please enter a filename!');
                }
            });

            document.getElementById('download-now').addEventListener('click', () => {
                const filename = document.getElementById('filename-input').value.trim();
                const source = window.hlsDownloaderState.selectedSource;
                if (source && filename) {
                    source.filename = filename;
                    source.id = Date.now();
                    window.hlsDownloaderState.downloadNow = source;
                    document.getElementById('filename-input').value = '';
                    document.getElementById('sources-section').style.display = 'none';
                    updatePanelStatus('Starting download...');
                } else {
                    updatePanelStatus('Please enter a filename!');
                }
            });

            document.getElementById('process-queue').addEventListener('click', () => {
                if (window.hlsDownloaderState.queue.length > 0) {
                    window.hlsDownloaderState.processQueue = true;
                    updatePanelStatus('Processing download queue...');
                }
            });

            document.getElementById('clear-queue').addEventListener('click', () => {
                window.hlsDownloaderState.queue = [];
                window.hlsDownloaderState.completedDownloads.clear();
                updateQueueDisplay();
                updatePanelStatus('Queue cleared.');
            });

            document.getElementById('stop-download').addEventListener('click', () => {
                window.hlsDownloaderState.stopDownload = true;
                updatePanelStatus('Stopping download...');
            });

            document.getElementById('minimize-panel').addEventListener('click', () => {
                document.getElementById('panel-content').style.display = 'none';
                document.getElementById('minimized-header').style.display = 'block';
                document.getElementById('panel-container').style.height = '80px';
                window.hlsDownloaderState.minimized = true;
            });

            document.getElementById('close-panel').addEventListener('click', () => {
                window.hlsDownloaderState.closedPanel = true;
                document.getElementById('hls-comprehensive-panel').style.animation = 'panelSlideIn 0.3s ease-out reverse';
                setTimeout(() => {
                    document.getElementById('hls-comprehensive-panel').remove();
                }, 300);
            });

            // Helper functions
            function updatePanelStatus(message) {
                document.getElementById('current-status').textContent = message;
            }

            function updateRecordingButtons(recording) {
                document.getElementById('start-recording').disabled = recording;
                document.getElementById('start-recording').style.opacity = recording ? '0.5' : '1';
                document.getElementById('stop-recording').disabled = !recording;
                document.getElementById('stop-recording').style.opacity = recording ? '1' : '0.5';
            }

            function updateQueueDisplay() {
                const queueList = document.getElementById('queue-list');
                const queueCount = document.getElementById('queue-count');
                const queue = window.hlsDownloaderState.queue;
                const completed = window.hlsDownloaderState.completedDownloads;

                queueCount.textContent = queue.length;

                if (queue.length === 0) {
                    queueList.innerHTML = '<div style="opacity: 0.7; padding: 12px; text-align: center;">Queue is empty</div>';
                    document.getElementById('process-queue').disabled = true;
                    document.getElementById('clear-queue').disabled = true;
                } else {
                    queueList.innerHTML = queue.map((item, i) => {
                        const isCompleted = completed.has(item.id);
                        const statusIcon = isCompleted ? '✅' : '⏳';
                        const itemClass = isCompleted ? 'queue-item-completed' : '';

                        return `<div class="${itemClass}" style="
                            padding: 10px 12px;
                            margin: 6px 0;
                            border-radius: 8px;
                            border-left: 4px solid ${isCompleted ? '#4CAF50' : 'rgba(255,255,255,0.3)'};
                            background: ${isCompleted ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255,255,255,0.1)'};
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            transition: all 0.3s ease;
                        ">
                            <span style="font-weight: 500;">${statusIcon} ${i+1}. ${item.filename} (${item.url_type})</span>
                            <button class="queue-item-remove" onclick="removeQueueItem(${i})">×</button>
                        </div>`;
                    }).join('');
                    document.getElementById('process-queue').disabled = false;
                    document.getElementById('clear-queue').disabled = false;
                }
            }

            function showSources(sources) {
                if (sources && sources.length > 0) {
                    const sourcesList = document.getElementById('sources-list');
                    sourcesList.innerHTML = sources.map((source, i) => 
                        `<div style="
                            padding: 12px;
                            margin: 6px 0;
                            background: rgba(255,255,255,0.1);
                            border-radius: 8px;
                            cursor: pointer;
                            border: 2px solid transparent;
                            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                            font-weight: 500;
                        " onclick="selectSource(${i})" onmouseover="this.style.background='rgba(255,255,255,0.2)'; this.style.transform='translateY(-1px)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'; this.style.transform='translateY(0)'">
                            ${i+1}. ${source.url_type}
                        </div>`
                    ).join('');

                    window.selectSource = function(index) {
                        // Remove previous selection
                        document.querySelectorAll('#sources-list > div').forEach(div => {
                            div.style.border = '2px solid transparent';
                        });
                        // Highlight selected
                        document.querySelectorAll('#sources-list > div')[index].style.border = '2px solid #4CAF50';
                        window.hlsDownloaderState.selectedSource = sources[index];
                    };

                    document.getElementById('sources-section').style.display = 'block';
                    // Auto-select first source
                    if (sources.length > 0) {
                        window.selectSource(0);
                    }
                }
            }

            // Expose functions to window
            window.hlsShowSources = showSources;
            window.hlsUpdateProgress = function(progress, filename, stats) {
                if (progress >= 0) {
                    const progressSection = document.getElementById('progress-section');
                    progressSection.style.display = 'block';
                    progressSection.classList.add('downloading-pulse');

                    document.getElementById('progress-filename').textContent = filename || 'Unknown file';
                    document.getElementById('progress-fill').style.width = progress + '%';
                    document.getElementById('progress-stats').textContent = stats || '';

                    if (progress >= 100) {
                        progressSection.classList.remove('downloading-pulse');
                        setTimeout(() => {
                            progressSection.style.display = 'none';
                        }, 3000);
                    }
                } else {
                    document.getElementById('progress-section').style.display = 'none';
                    document.getElementById('progress-section').classList.remove('downloading-pulse');
                }
            };

            window.hlsUpdateStatus = updatePanelStatus;
            window.hlsMarkCompleted = function(itemId) {
                window.hlsDownloaderState.completedDownloads.add(itemId);
                updateQueueDisplay();
            };

            // Initialize display
            updateQueueDisplay();
            updateRecordingButtons(false);
            updatePanelStatus('Ready! Navigate to a video page and click Start.');

            console.log('Modern HLS Downloader panel injected');
            return true;
            """

            result = self.driver.execute_script(panel_js)
            self.panel_injected = True
            self.current_url = current_url
            return True

        except Exception as e:
            print(f"Failed to inject panel: {e}")
            self.panel_injected = False
            return False

    def start_page_monitor(self):
        """Monitor page changes and re-inject panel as needed"""

        def monitor():
            while self.running:
                try:
                    if self.driver:
                        current_url = self.driver.current_url

                        # Check if URL changed or panel is missing
                        if (current_url != self.current_url or
                                not self.check_panel_exists()):

                            if current_url and 'about:blank' not in current_url:
                                time.sleep(1)  # Wait for page to load
                                if self.inject_comprehensive_panel():
                                    print(f"Panel re-injected on: {current_url[:50]}...")

                        time.sleep(2)  # Check every 2 seconds
                    else:
                        break

                except Exception as e:
                    time.sleep(2)

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def check_panel_exists(self):
        """Check if the panel still exists on the page"""
        try:
            exists = self.driver.execute_script(
                "return document.getElementById('hls-comprehensive-panel') !== null;"
            )
            return exists
        except:
            return False

    def authenticate_at_portal(self, portal_url):
        """Opens the university portal and sets up the system"""
        print("Opening university portal...")
        self.setup_browser()
        self.driver.get(portal_url)

        # Show welcome info first
        time.sleep(2)
        self.inject_welcome_info()

        print("\nPlease log in to your university portal...")
        print("The control panel will appear after you dismiss the welcome message.")
        print("All controls are in the browser - no more terminal commands!")

        # Wait for welcome to be dismissed, then inject panel
        def wait_and_inject():
            while True:
                try:
                    welcome_exists = self.driver.execute_script(
                        "return document.getElementById('hls-welcome-info') !== null;"
                    )
                    if not welcome_exists:
                        time.sleep(1)
                        self.inject_comprehensive_panel()
                        break
                    time.sleep(1)
                except:
                    time.sleep(1)

        inject_thread = threading.Thread(target=wait_and_inject, daemon=True)
        inject_thread.start()

        # Start monitoring for page changes
        self.start_page_monitor()

        cookies = self.driver.get_cookies()
        self.cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        self.authenticated = True

        print("System ready! Use the browser panel to control everything.")
        return self.driver.current_url

    def wait_for_user_action(self):
        """Wait for user actions through the panel"""
        print("\nAll controls are now in the browser panel!")
        print("The panel follows you across pages automatically.")
        print("Waiting for user actions...")

        while self.running:
            try:
                # Check for recording stopped
                recording_stopped = self.driver.execute_script(
                    "return window.hlsDownloaderState?.recordingStopped || false;"
                )
                if recording_stopped:
                    # Clear the flag
                    self.driver.execute_script("window.hlsDownloaderState.recordingStopped = false;")
                    return self.process_captured_sources()

                # Check for download now request
                download_now = self.driver.execute_script(
                    "return window.hlsDownloaderState?.downloadNow || null;"
                )
                if download_now:
                    # Clear the flag
                    self.driver.execute_script("window.hlsDownloaderState.downloadNow = null;")
                    return self.download_single_video(download_now)

                # Check for process queue request
                process_queue = self.driver.execute_script(
                    "return window.hlsDownloaderState?.processQueue || false;"
                )
                if process_queue:
                    # Clear the flag
                    self.driver.execute_script("window.hlsDownloaderState.processQueue = false;")
                    return self.process_download_queue()

                # Check for stop download request
                stop_download = self.driver.execute_script(
                    "return window.hlsDownloaderState?.stopDownload || false;"
                )
                if stop_download:
                    # Clear the flag
                    self.driver.execute_script("window.hlsDownloaderState.stopDownload = false;")
                    return self.stop_current_download()

                # Check if panel was closed
                panel_closed = self.driver.execute_script(
                    "return window.hlsDownloaderState?.closedPanel || false;"
                )
                if panel_closed:
                    print("Panel closed by user. Exiting...")
                    return False

                time.sleep(0.5)

            except Exception as e:
                time.sleep(1)

        return False

    def stop_current_download(self):
        """Stop the current download process and clean up partial files"""
        if self.current_download_process:
            try:
                self.current_download_process.terminate()
                print("Download stopped by user")

                # Clean up partial files
                if self.current_download_filename:
                    self.cleanup_partial_files(self.current_download_filename)

                self.driver.execute_script("window.hlsUpdateStatus('Download stopped and cleaned up.');")
                self.driver.execute_script("window.hlsUpdateProgress(-1, '', '');")
                self.current_download_process = None
                self.current_download_filename = None
            except Exception as e:
                print(f"Error stopping download: {e}")
        return True

    def cleanup_partial_files(self, filename):
        """Clean up partial download files (.part, .frag, etc.)"""
        try:
            # Create download directory path
            downloads_dir = "downloads"

            # Patterns for partial files
            partial_patterns = [
                f"{filename}.*.part",
                f"{filename}.*.frag*",
                f"{filename}.f*.ts",
                f"{filename}.*.tmp"
            ]

            for pattern in partial_patterns:
                full_pattern = os.path.join(downloads_dir, pattern)
                for partial_file in glob.glob(full_pattern):
                    try:
                        os.remove(partial_file)
                        print(f"Cleaned up: {partial_file}")
                    except Exception as e:
                        print(f"Could not remove {partial_file}: {e}")

            # Also check for any leftover fragment directories
            frag_dirs = glob.glob(os.path.join(downloads_dir, f"{filename}*"))
            for frag_dir in frag_dirs:
                if os.path.isdir(frag_dir):
                    try:
                        import shutil
                        shutil.rmtree(frag_dir)
                        print(f"Cleaned up directory: {frag_dir}")
                    except Exception as e:
                        print(f"Could not remove directory {frag_dir}: {e}")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def process_captured_sources(self):
        """Process sources captured during recording"""
        print("Processing captured network data...")

        # Update panel status
        self.driver.execute_script("window.hlsUpdateStatus('Processing captured data...');")

        # Get network logs
        try:
            logs = self.driver.get_log('performance')
        except Exception as e:
            print(f"Network capture failed: {e}")
            self.driver.execute_script("window.hlsUpdateStatus('Network capture failed. Try again.');")
            return True

        # Process HLS sources
        hls_sources = self.extract_hls_from_logs(logs)
        unique_sources = self.analyze_hls_sources(hls_sources)

        if unique_sources:
            print(f"Found {len(unique_sources)} HLS streams")

            # Show sources in panel
            sources_js = f"window.hlsShowSources({json.dumps(unique_sources)});"
            self.driver.execute_script(sources_js)

            self.driver.execute_script(
                f"window.hlsUpdateStatus('Found {len(unique_sources)} video(s). Select one and enter a filename.');"
            )
        else:
            print("No HLS streams found")
            self.driver.execute_script("window.hlsUpdateStatus('No videos found. Try recording again.');")

        return True

    def extract_hls_from_logs(self, logs):
        """Extract HLS sources from network logs"""
        hls_sources = []

        for log in logs:
            try:
                message = json.loads(log['message'])

                if message['message']['method'] in ['Network.responseReceived', 'Network.requestWillBeSent']:
                    if 'params' in message['message']:
                        if 'response' in message['message']['params']:
                            url = message['message']['params']['response']['url']
                        elif 'request' in message['message']['params']:
                            url = message['message']['params']['request']['url']
                        else:
                            continue

                        # Only capture HLS streams (.m3u8)
                        if '.m3u8' in url.lower() and 'kaltura' in url.lower():
                            headers = {}
                            if 'response' in message['message']['params']:
                                headers = message['message']['params']['response'].get('headers', {})
                            elif 'request' in message['message']['params']:
                                headers = message['message']['params']['request'].get('headers', {})

                            hls_sources.append({
                                'url': url,
                                'headers': headers
                            })

            except (json.JSONDecodeError, KeyError):
                continue

        return hls_sources

    def analyze_hls_sources(self, sources):
        """Analyze HLS sources and remove duplicates"""
        if not sources:
            return []

        # Remove duplicates
        unique_sources = []
        seen_urls = set()

        for source in sources:
            url = source['url']
            if url not in seen_urls:
                seen_urls.add(url)

                # Determine type
                if 'serveflavor' in url.lower():
                    url_type = "Direct"
                else:
                    url_type = "Manifest"

                unique_sources.append({
                    'url': url,
                    'headers': source['headers'],
                    'url_type': url_type,
                    'filename': ''
                })

        return unique_sources

    def download_single_video(self, source):
        """Download a single video immediately"""
        print(f"Starting download: {source['filename']}")

        self.driver.execute_script(
            f"window.hlsUpdateStatus('Downloading {source['filename']}...');"
        )

        success = self.download_video(source)

        if success:
            self.driver.execute_script("window.hlsUpdateStatus('Download completed! Ready for next video.');")
        else:
            self.driver.execute_script("window.hlsUpdateStatus('Download failed. Try again.');")

        return True

    def process_download_queue(self):
        """Process all items in the download queue"""
        # Get queue from browser
        queue = self.driver.execute_script("return window.hlsDownloaderState.queue || [];")

        if not queue:
            self.driver.execute_script("window.hlsUpdateStatus('Queue is empty.');")
            return True

        print(f"Processing {len(queue)} items in queue...")
        self.driver.execute_script(f"window.hlsUpdateStatus('Processing {len(queue)} downloads...');")

        for i, source in enumerate(queue, 1):
            print(f"Downloading {i}/{len(queue)}: {source['filename']}")

            self.driver.execute_script(
                f"window.hlsUpdateStatus('Downloading {i}/{len(queue)}: {source['filename']}');"
            )

            success = self.download_video(source)

            if success:
                # Mark as completed in the queue
                self.driver.execute_script(f"window.hlsMarkCompleted({source['id']});")
            else:
                print(f"Failed to download: {source['filename']}")
                self.driver.execute_script(
                    f"window.hlsUpdateStatus('Failed: {source['filename']}. Continuing...');"
                )

            # Check if user wants to stop
            stop_requested = self.driver.execute_script(
                "return window.hlsDownloaderState?.stopDownload || false;"
            )
            if stop_requested:
                self.driver.execute_script("window.hlsDownloaderState.stopDownload = false;")
                break

        # Don't clear queue automatically - let user see completed status
        self.driver.execute_script("window.hlsUpdateStatus('All downloads completed! Queue shows completion status.');")
        print("Queue processing completed!")

        return True

    def build_cookie_string(self):
        """Convert cookies dict to string format for yt-dlp"""
        return "; ".join([f"{name}={value}" for name, value in self.cookies.items()])

    def download_video(self, source, output_dir="downloads"):
        """Download video using yt-dlp with progress updates to panel"""
        if not self.authenticated:
            return False

        # Create downloads directory
        os.makedirs(output_dir, exist_ok=True)

        cookie_string = self.build_cookie_string()
        current_url = self.driver.current_url

        # Video goes directly to downloads folder
        video_output_pattern = os.path.join(output_dir, f"{source['filename']}.%(ext)s")

        # Store current download filename for cleanup
        self.current_download_filename = source['filename']

        cmd = [
            "yt-dlp",
            "--add-header", f"Cookie: {cookie_string}",
            "--referer", current_url,
            "--add-header", "Origin: https://kaltura-kaf.edu.kuleuven.cloud",
            "-o", video_output_pattern,
            "--no-write-info-json",  # Don't write JSON files
            "--no-write-thumbnail",  # Don't write thumbnail files
            "--newline",
            source['url']
        ]

        try:
            self.current_download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            while True:
                # Check if user wants to stop
                stop_requested = self.driver.execute_script(
                    "return window.hlsDownloaderState?.stopDownload || false;"
                )
                if stop_requested:
                    self.current_download_process.terminate()
                    self.driver.execute_script("window.hlsDownloaderState.stopDownload = false;")
                    self.driver.execute_script("window.hlsUpdateStatus('Download stopped by user.');")
                    self.driver.execute_script("window.hlsUpdateProgress(-1, '', '');")

                    # Clean up partial files
                    self.cleanup_partial_files(source['filename'])

                    self.current_download_process = None
                    self.current_download_filename = None
                    return False

                output = self.current_download_process.stdout.readline()
                if output == '' and self.current_download_process.poll() is not None:
                    break

                if output:
                    output = output.strip()
                    progress_info = self.parse_yt_dlp_progress(output)
                    if progress_info:
                        # Update panel progress
                        self.driver.execute_script(
                            f"window.hlsUpdateProgress({progress_info['percent']}, '{source['filename']}', '{progress_info['stats']}');"
                        )

            return_code = self.current_download_process.poll()
            self.current_download_process = None
            self.current_download_filename = None

            if return_code == 0:
                self.driver.execute_script(
                    f"window.hlsUpdateProgress(100, '{source['filename']}', 'Completed!');"
                )
                return True
            else:
                # Clean up partial files on failure
                self.cleanup_partial_files(source['filename'])
                return False

        except Exception as e:
            print(f"Error: {e}")
            # Clean up partial files on exception
            if self.current_download_filename:
                self.cleanup_partial_files(self.current_download_filename)
            self.current_download_process = None
            self.current_download_filename = None
            return False

    def parse_yt_dlp_progress(self, line):
        """Parse yt-dlp output for progress information"""
        if "[download]" in line and "%" in line:
            try:
                parts = line.strip().split()
                for i, part in enumerate(parts):
                    if "%" in part:
                        percent = float(part.replace('%', ''))

                        # Extract speed and ETA info
                        stats_parts = []

                        # Look for speed (after "at")
                        try:
                            at_index = parts.index("at")
                            if at_index + 1 < len(parts):
                                speed = parts[at_index + 1]
                                stats_parts.append(f"Speed: {speed}")
                        except (ValueError, IndexError):
                            pass

                        # Look for ETA
                        try:
                            eta_index = parts.index("ETA")
                            if eta_index + 1 < len(parts):
                                eta = parts[eta_index + 1]
                                stats_parts.append(f"ETA: {eta}")
                        except (ValueError, IndexError):
                            pass

                        # Look for file size (after "of")
                        try:
                            of_index = parts.index("of")
                            if of_index + 1 < len(parts):
                                size = parts[of_index + 1]
                                stats_parts.append(f"Size: {size}")
                        except (ValueError, IndexError):
                            pass

                        stats = " | ".join(stats_parts) if stats_parts else "Downloading..."

                        return {
                            'percent': percent,
                            'stats': stats
                        }
            except:
                pass
        return None

    def cleanup(self):
        """Close browser and cleanup"""
        self.running = False
        if self.current_download_process:
            try:
                self.current_download_process.terminate()
                # Clean up any partial files
                if self.current_download_filename:
                    self.cleanup_partial_files(self.current_download_filename)
            except:
                pass
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        if self.driver:
            self.driver.quit()


def main():
    downloader = FixedModernHLSDownloader()

    try:
        print("HLS Video Downloader")

        portal_url = "https://toledo.kuleuven.be"

        # Authenticate and setup
        downloader.authenticate_at_portal(portal_url)

        # Main loop - wait for user actions in panel
        while downloader.wait_for_user_action():
            pass

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        downloader.cleanup()


if __name__ == "__main__":
    main()