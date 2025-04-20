<template>
  <div class="home-container">
    <header class="home-header">
      <h1>图像处理系统</h1>
      <div class="user-menu">
        <button class="user-icon" @click="toggleMenu">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
        </button>
        <div v-if="showMenu" class="dropdown-menu">
          <router-link to="/account" class="menu-item">
            <span>个人中心</span>
          </router-link>
          <button @click="logout" class="menu-item">
            <span>退出登录</span>
          </button>
        </div>
      </div>
    </header>

    <main class="home-content">
      <div class="sidebar">
        <button 
          class="function-btn"
          :class="{ active: activeFunction === 'image' }"
          @click="setActiveFunction('image')"
        >
          图像处理
        </button>
        <button 
          class="function-btn"
          :class="{ active: activeFunction === 'cameraQuery' }"
          @click="setActiveFunction('cameraQuery')"
        >
          监控点位查询
        </button>
        <button 
          class="function-btn"
          :class="{ active: activeFunction === 'function3' }"
          @click="setActiveFunction('function3')"
        >
          实时监控
        </button>
        <button 
          class="function-btn"
          :class="{ active: activeFunction === 'historyQuery' }"
          @click="setActiveFunction('historyQuery')"
        >
          历史监控查询
        </button>
      </div>

      <div class="content-area">
        <div v-if="activeFunction === 'image'" class="image-processing">
          <div class="processing-options">
            <button 
              class="option-btn"
              :class="{ active: activeOption === 'photo' }"
              @click="setActiveOption('photo')"
            >
              照片处理
            </button>
            <button 
              class="option-btn"
              :class="{ active: activeOption === 'video' }"
              @click="setActiveOption('video')"
            >
              视频处理
            </button>
            <button 
              class="option-btn"
              :class="{ active: activeOption === 'realtime' }"
              @click="setActiveOption('realtime')"
            >
              实时处理
            </button>
          </div>

          <div class="processing-content">
            <ImageUploader v-if="activeOption === 'photo'" />
            <VideoUploader v-else-if="activeOption === 'video'" />
            <CameraView v-else />
          </div>
        </div>

        <div v-else-if="activeFunction === 'cameraQuery'" class="camera-query">
          <div class="query-header">
            <h3>监控点位列表</h3>
          </div>
          <div v-if="cameras.length > 0" class="camera-list">
            <button
              v-for="camera in cameras" 
              :key="camera.id" 
              class="camera-item"
              @click="handleCameraClick(camera.camera_id)"
            >
              摄像头 {{ camera.id }}
            </button>
            <button @click="fetchCameras" class="refresh-btn">刷新列表</button>
          </div>
          <div v-else class="no-cameras">
            <p>未检测到摄像头</p>
            <button @click="fetchCameras" class="refresh-btn">刷新列表</button>
          </div>
        </div>
        
        <div v-else-if="activeFunction === 'function3'" class="realtime-monitoring">
          <div class="monitoring-header">
            <h3>实时监控</h3>
            <div class="camera-selector">
            <select v-model="selectedCamera" @change="startMonitoring">
                <option :value="null">-- 请选择摄像头 --</option>
                <option v-for="camera in cameras" :value="camera.camera_id" :key="camera.id">
                  摄像头 {{ camera.id }} (ID: {{ camera.camera_id }})
                </option>
            </select>
            <button @click="refreshMonitoring" class="refresh-btn">刷新监控</button>
            </div>
          </div>
          <div class="monitoring-content">
            <video ref="videoPlayer" controls></video>
            <div class="recording-controls">
              <button 
                @click="startRecording" 
                class="record-btn"
                :disabled="isRecording"
              >
                {{ isRecording ? '录制中...' : '开始录制' }}
              </button>
              <button 
                @click="stopRecording" 
                class="stop-btn"
                :disabled="!isRecording"
              >
                停止录制
              </button>
              <div v-if="isRecording" class="recording-timer">
                录制时间: {{ formatTime(recordingTime) }}
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="activeFunction === 'historyQuery'" class="history-query-container">
          <HistoryQuery />
        </div>
        <div v-else class="empty-function">
          <p>功能开发中...</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import ImageUploader from '../components/ImageUploader.vue'
import VideoUploader from '../components/VideoUploader.vue'
import CameraView from '../components/CameraView.vue'
import HistoryQuery from './HistoryQuery.vue'

const authStore = useAuthStore()
const router = useRouter()
const showMenu = ref(false)
const activeFunction = ref('image')
const activeOption = ref('photo')
const cameras = ref([])

const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const setActiveFunction = (func) => {
  activeFunction.value = func
  if (func === 'cameraQuery' || func === 'function3') {
    fetchCameras()
  }
}

const setActiveOption = (option) => {
  activeOption.value = option
}

const selectedCamera = ref(null)
const isRecording = ref(false)
const mediaStream = ref(null)

const handleCameraClick = (cameraId) => {
  console.log('Selected camera ID:', cameraId)
  if (confirm('是否要跳转到实时监控？')) {
    selectedCamera.value = cameraId
    activeFunction.value = 'function3'
    nextTick(() => {
      startMonitoring()
    })
  }
}

const fetchCameras = async () => {
  try {
    // 首先请求摄像头权限
    const tempStream = await navigator.mediaDevices.getUserMedia({ video: true })
    tempStream.getTracks().forEach(track => track.stop())
    
    // 获取设备列表
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')
    
    console.log('Available cameras:', videoDevices)
    
    cameras.value = videoDevices.map((device, index) => ({
      id: index,  // 从0开始编号
      camera_id: device.deviceId,
      label: device.label || `摄像头 ${index}`,
      deviceId: device.deviceId  // 确保设备ID正确传递
    }))
    
    if (cameras.value.length > 0) {
      console.log('检测到摄像头:', cameras.value)
      // 不再自动选择第一个摄像头
    } else {
      console.warn('未检测到摄像头设备')
      alert('未检测到摄像头设备，请检查连接')
    }
  } catch (error) {
    console.error('获取摄像头列表失败:', error)
    alert(`无法访问摄像头: ${error.message}`)
  }
}

const refreshMonitoring = async () => {
  await fetchCameras()
  if (selectedCamera.value) {
    await startMonitoring()
  }
}

const startMonitoring = async () => {
  try {
    // 清理之前的媒体流
    if (mediaStream.value) {
      mediaStream.value.getTracks().forEach(track => track.stop())
      mediaStream.value = null
    }

    const videoPlayer = document.querySelector('video')
    // 重置视频源
    if (videoPlayer) {
      videoPlayer.srcObject = null
    }

    // 处理空白选择
    if (!selectedCamera.value) {
      return
    }

    const currentCamera = cameras.value.find(cam => cam.camera_id === selectedCamera.value)
    
    if (!currentCamera) {
      console.error('未找到选中的摄像头:', selectedCamera.value)
      alert('未找到选中的摄像头，请刷新列表后重试')
      return
    }

    console.log('正在尝试使用摄像头:', currentCamera)
    
    // 多级回退策略
    const constraintsOptions = [
      // 首选配置
      {
        video: {
          deviceId: { exact: currentCamera.camera_id },
          width: { min: 640, ideal: 1280 },
          height: { min: 480, ideal: 720 },
          frameRate: { ideal: 30 }
        }
      },
      // 中级回退 - 移除分辨率要求
      {
        video: {
          deviceId: { exact: currentCamera.camera_id },
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      },
      // 基本回退 - 仅设备ID
      {
        video: {
          deviceId: { exact: currentCamera.camera_id }
        }
      },
      // 最终回退 - 无任何约束
      {
        video: true
      }
    ]

    let lastError = null
    for (const constraints of constraintsOptions) {
      try {
        console.log('尝试约束条件:', constraints)
        mediaStream.value = await navigator.mediaDevices.getUserMedia(constraints)
        videoPlayer.srcObject = mediaStream.value
        console.log('成功使用约束条件:', constraints)
        break // 成功则退出循环
      } catch (error) {
        console.error('摄像头配置失败:', error)
        lastError = error
        // 关闭可能已创建的部分流
        if (mediaStream.value) {
          mediaStream.value.getTracks().forEach(track => track.stop())
          mediaStream.value = null
        }
      }
    }

    if (!mediaStream.value) {
      console.error('所有摄像头配置尝试均失败', lastError)
      alert('无法访问摄像头。请检查摄像头是否被其他程序占用，或尝试更换摄像头。')
      return
    }
    
    // 更新摄像头列表
    const updatedDevices = await navigator.mediaDevices.enumerateDevices()
    const updatedVideoDevices = updatedDevices.filter(device => device.kind === 'videoinput')
    if (updatedVideoDevices.length !== cameras.value.length) {
      cameras.value = updatedVideoDevices.map((device, index) => ({
        id: index + 1,
        camera_id: device.deviceId,
        label: device.label || `摄像头 ${index + 1}`
      }))
    }
  } catch (error) {
    console.error('启动监控失败:', error)
    alert(`无法访问摄像头: ${error.message}`)
  }
}

const mediaRecorder = ref(null)
const recordedChunks = ref([])
const recordingTime = ref(0)
let recordingInterval = null

const startRecording = async () => {
  if (!mediaStream.value) {
    alert('请先启动摄像头')
    return
  }

  try {
    recordedChunks.value = []
    mediaRecorder.value = new MediaRecorder(mediaStream.value, {
      mimeType: 'video/webm'
    })

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = async () => {
      try {
        const blob = new Blob(recordedChunks.value, { type: 'video/webm' })
        const formData = new FormData()
        const filename = `recording-${new Date().toISOString().replace(/[:.]/g, '-')}.webm`
        formData.append('video', blob, filename)
        formData.append('cameraId', selectedCamera.value)

        const response = await fetch('/api/save_video', {
          method: 'POST',
          body: formData
        })

        const result = await response.json()
        if (result.success) {
          alert(`视频已保存到: ${result.filePath}`)
        } else {
          alert(`保存失败: ${result.message}`)
        }
      } catch (error) {
        console.error('保存视频失败:', error)
        alert('保存视频失败，请检查后端服务')
      }
    }

    mediaRecorder.value.start(100) // 每100ms收集一次数据
    isRecording.value = true
    
    // 计时器
    recordingTime.value = 0
    recordingInterval = setInterval(() => {
      recordingTime.value++
    }, 1000)
    
    console.log('开始录制')
  } catch (error) {
    console.error('开始录制失败:', error)
    alert(`开始录制失败: ${error.message}`)
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(recordingInterval)
    console.log('停止录制')
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #1976d2;
  color: white;
}

.user-menu {
  position: relative;
}

.user-icon {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 150px;
  z-index: 100;
}

.menu-item {
  display: block;
  padding: 0.75rem 1rem;
  text-align: left;
  color: #333;
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
}

.menu-item:hover {
  background: #f5f5f5;
}

.home-content {
  flex: 1;
  display: flex;
}

.sidebar {
  width: 200px;
  background: #f5f5f5;
  padding: 1rem;
  border-right: 1px solid #ddd;
}

.function-btn {
  display: block;
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
}

.function-btn:hover {
  background: #e3f2fd;
}

.function-btn.active {
  background: #1976d2;
  color: white;
}

.content-area {
  flex: 1;
  padding: 1rem;
}

.image-processing {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.processing-options {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.option-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.option-btn:hover {
  background: #f5f5f5;
}

.option-btn.active {
  background: #1976d2;
  color: white;
}

.processing-content {
  flex: 1;
  border: 1px dashed #ddd;
  border-radius: 4px;
  padding: 1rem;
  display: flex;
}

.option-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.empty-function {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.camera-query {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.query-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #1565c0;
}

.camera-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.camera-item {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.no-cameras {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.realtime-monitoring {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.monitoring-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.camera-selector select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.monitoring-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.monitoring-content video {
  width: 100%;
  max-height: 500px;
  background: #000;
  border-radius: 4px;
}

.recording-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.record-btn, .stop-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.record-btn {
  background: #4caf50;
  color: white;
}

.record-btn:hover:not(:disabled) {
  background: #388e3c;
}

.record-btn:disabled {
  background: #81c784;
  cursor: not-allowed;
}

.stop-btn {
  background: #f44336;
  color: white;
}

.stop-btn:hover:not(:disabled) {
  background: #d32f2f;
}

.stop-btn:disabled {
  background: #e57373;
  cursor: not-allowed;
}

.recording-timer {
  color: #f44336;
  font-weight: bold;
}
</style>
