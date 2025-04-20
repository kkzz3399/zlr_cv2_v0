<template>
  <div class="video-uploader">
    <div class="upload-section">
      <input 
        type="file" 
        accept="video/*" 
        @change="handleVideoUpload" 
        ref="fileInput"
        class="file-input"
      />
      <button @click="triggerFileInput" class="upload-btn">
        选择视频
      </button>
      <div v-if="videoSource" class="video-preview">
        <video 
          :src="videoSource" 
          controls
          class="preview-video"
        ></video>
      </div>
    </div>

    <div class="result-section">
      <div class="result-preview">
        <div v-if="isProcessing" class="processing-indicator">
          <p>视频处理中...</p>
          <progress v-if="progress > 0" :value="progress" max="100"></progress>
        </div>
        <div v-else-if="processedVideoUrl" class="result-video">
          <h3>处理结果</h3>
          <video 
            :src="processedVideoUrl" 
            controls
            class="processed-video"
            @error="handleResultError"
          ></video>
        </div>
        <div v-else class="placeholder">
          <p>处理结果将显示在这里</p>
        </div>
      </div>
      
      <button 
        @click="processVideo" 
        :disabled="!videoSource"
        class="process-btn"
      >
        处理视频
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const videoSource = ref(null)
const processedVideoUrl = ref(null)
const videoError = ref(null)
const resultError = ref(null)
const videoLoaded = ref(false)
const isProcessing = ref(false)
const progress = ref(0)

const handleVideoError = () => {
  videoError.value = '无法播放视频，请检查格式或网络连接'
}

const handleVideoLoaded = () => {
  videoLoaded.value = true
  videoError.value = null
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleVideoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      videoSource.value = e.target.result
      processedVideoUrl.value = null
    }
    reader.readAsDataURL(file)
  }
}

const processVideo = async () => {
  if (!videoSource.value) return
  
  const fileInput = document.querySelector('.file-input')
  const file = fileInput.files[0]
  
  const formData = new FormData()
  formData.append('file', file)
  
  isProcessing.value = true
  progress.value = 0
  resultError.value = null
  
  try {
    const response = await fetch('/api/detect/video', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '视频处理失败')
    }
    
    // 模拟进度更新
    const interval = setInterval(() => {
      progress.value = Math.min(progress.value + 10, 90)
    }, 500)
    
    const result = await response.json()
    clearInterval(interval)
    progress.value = 100
    
    // 确保URL是绝对路径
    processedVideoUrl.value = new URL(result.processed_url, window.location.origin).href;
    console.log('Processed video URL:', processedVideoUrl.value);
    await new Promise(resolve => setTimeout(resolve, 500)) // 等待进度条完成
  } catch (error) {
    console.error('视频处理错误:', error)
    resultError.value = error.message
  } finally {
    isProcessing.value = false
    progress.value = 0
  }
}

const handleResultError = (event) => {
  console.error('Video error:', event);
  const errorMsg = event.target.error ? event.target.error.message : '视频格式可能不受支持';
  resultError.value = `无法加载处理后的视频: ${errorMsg}`;
};

const checkVideoSupport = () => {
  const video = document.createElement('video');
  const supportedFormats = [
    'video/mp4',
    'video/webm',
    'video/ogg'
  ];
  return supportedFormats.some(format => video.canPlayType(format) !== '');
};

const checkVideoFormat = (url) => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.src = url;
    video.addEventListener('loadedmetadata', () => {
      resolve({
        format: video.videoWidth > 0 ? 'supported' : 'unsupported',
        codec: video.videoCodecs || 'unknown'
      });
    });
    video.addEventListener('error', () => {
      resolve({
        format: 'unsupported',
        codec: 'unknown'
      });
    });
  });
};

</script>

<style scoped>
.video-uploader {
  display: flex;
  height: 100%;
}

.upload-section, .result-section {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.file-input {
  display: none;
}

.upload-btn, .process-btn {
  padding: 0.5rem 1rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.upload-btn:hover, .process-btn:hover {
  background: #1565c0;
}

.process-btn:disabled {
  background: #b0bec5;
  cursor: not-allowed;
}

.video-preview, .result-preview {
  flex: 1;
  border: 1px dashed #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  overflow: hidden;
}

.preview-video {
  max-width: 100%;
  max-height: 100%;
}

.placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  border: 1px dashed #ddd;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.processing-indicator {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #1976d2;
}

.processing-indicator progress {
  width: 80%;
  margin-top: 1rem;
}

.result-video {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.processed-video {
  width: 100%;
  height: calc(100% - 2rem);
  margin-top: 1rem;
}

.error-message {
  color: #ff5252;
  margin-top: 0.5rem;
}
</style>
