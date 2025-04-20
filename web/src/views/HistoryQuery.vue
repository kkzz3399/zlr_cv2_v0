<template>
  <div class="history-query">
    <h2>历史监控查询</h2>
    <div class="query-controls">
      <div class="date-picker">
        <label for="date">选择日期：</label>
        <input 
          type="date" 
          id="date" 
          v-model="selectedDate"
          @change="fetchVideosByDate"
        >
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="videos.length > 0" class="video-list">
      <div 
        v-for="video in videos" 
        :key="video.id" 
        class="video-item"
        @click="playVideo(video)"
      >
        <div class="video-thumbnail">
          <img :src="getThumbnailUrl(video)" alt="视频缩略图">
        </div>
        <div class="video-info">
          <h3>{{ video.name }}</h3>
          <p>录制时间: {{ formatDateTime(video.date + video.time) }}</p>
        </div>
      </div>
    </div>

    <div v-else class="no-videos">
      <p>没有找到该日期的监控视频</p>
    </div>

    <div v-if="currentVideo" class="video-player-modal">
      <div class="modal-content">
        <span class="close" @click="closePlayer">&times;</span>
        <video controls autoplay>
          <source :src="currentVideo.url" type="video/webm">
          您的浏览器不支持视频播放
        </video>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedDate = ref('')
const videos = ref([])
const loading = ref(false)
const currentVideo = ref(null)

const fetchVideosByDate = async () => {
  if (!selectedDate.value) return
  
  try {
    loading.value = true
    const response = await fetch(`/api/history/videos?date=${selectedDate.value}`)
    if (!response.ok) throw new Error('获取视频列表失败')
    const data = await response.json()
    videos.value = data.data
  } catch (error) {
    console.error('获取视频列表失败:', error)
    alert('获取视频列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const getThumbnailUrl = (video) => {
  return `/api/history/videos/${video.id}?thumbnail=true`
}

const formatDateTime = (timestamp) => {
  // 格式: 20250420_170540 -> 2025-04-20 17:05:40
  const dateStr = timestamp.slice(0, 4) + '-' + 
                  timestamp.slice(4, 6) + '-' + 
                  timestamp.slice(6, 8)
  const timeStr = timestamp.slice(9, 11) + ':' + 
                  timestamp.slice(11, 13) + ':' + 
                  timestamp.slice(13, 15)
  return `${dateStr} ${timeStr}`
}

const playVideo = (video) => {
  currentVideo.value = {
    ...video,
    url: `/api/history/videos/${video.id}`
  }
}

const closePlayer = () => {
  currentVideo.value = null
}

// 默认加载当天的视频
onMounted(() => {
  const today = new Date()
  selectedDate.value = today.toISOString().split('T')[0]
  fetchVideosByDate()
})
</script>



<style scoped>
.history-query {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.query-controls {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.date-picker {
  display: flex;
  align-items: center;
}

.date-picker label {
  font-weight: bold;
}

.date-picker input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.video-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.video-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.video-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.video-thumbnail img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}

.video-info h3 {
  margin: 10px 0 5px;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.video-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.loading, .no-videos {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}

.video-player-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  width: 80%;
  max-width: 800px;
}

.modal-content video {
  width: 100%;
  max-height: 80vh;
}

.close {
  position: absolute;
  top: -40px;
  right: 0;
  color: white;
  font-size: 30px;
  cursor: pointer;
}
</style>
