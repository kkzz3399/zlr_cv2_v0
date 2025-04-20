<template>
  <div class="camera-view">
    <div class="stream-container">
      <div class="video-wrapper">
        <h3>原始视频流</h3>
        <div class="video-container">
          <img :src="rawStreamUrl" class="video-feed" alt="原始视频流" />
        </div>
      </div>
      
      <div class="video-wrapper">
        <h3>处理后视频流</h3>
        <div class="video-container">
          <img :src="processedStreamUrl" class="video-feed" alt="处理后视频流" />
        </div>
      </div>
    </div>

    <button class="camera-btn" @click="toggleCamera">
      {{ isCameraActive ? '停止视频流' : '开始视频流' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isCameraActive = ref(false)
const rawStreamUrl = ref('')
const processedStreamUrl = ref('')

const toggleCamera = () => {
  isCameraActive.value = !isCameraActive.value
  if (isCameraActive.value) {
    // 添加时间戳避免缓存
    const timestamp = new Date().getTime()
    rawStreamUrl.value = `http://localhost:5000/video/raw?t=${timestamp}`
    processedStreamUrl.value = `http://localhost:5000/video/processed?t=${timestamp}`
  } else {
    rawStreamUrl.value = ''
    processedStreamUrl.value = ''
  }
}
</script>

<style scoped>
.camera-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
}

.stream-container {
  display: flex;
  flex: 1;
  gap: 1rem;
}

.video-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.video-wrapper h3 {
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.video-container {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f5f5;
}

.video-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-btn {
  padding: 0.5rem 1rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  align-self: center;
}

.camera-btn:hover {
  background: #1565c0;
}
</style>
