<template>
  <div class="image-uploader">
    <div class="upload-section">
      <input 
        type="file" 
        accept="image/*" 
        @change="handleImageUpload" 
        ref="fileInput"
        class="file-input"
      />
      <button @click="triggerFileInput" class="upload-btn">
        选择图片
      </button>
      <div v-if="originalImage" class="image-preview">
        <img :src="originalImage" alt="原始图片" class="preview-image"/>
      </div>
    </div>

    <div class="result-section">
      <div class="result-preview">
        <div v-if="processedImage">
          <h3>本次处理结果</h3>
          <img :src="processedImage" alt="本次处理结果" class="preview-image"/>
        </div>
        <div v-if="processedImageUrl">
          <h3>最新处理结果</h3>
          <img :src="processedImageUrl" alt="最新处理结果" class="preview-image"/>
        </div>
        <div v-if="!processedImage && !processedImageUrl" class="placeholder">
          <p>处理结果将显示在这里</p>
        </div>
      </div>
      
      <button 
        @click="processImage" 
        :disabled="!originalImage"
        class="process-btn"
      >
        处理图片
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const fileInput = ref(null)
const originalImage = ref(null)
const processedImage = ref(null)
const processedImageUrl = ref(null)
let refreshInterval = null

// 获取最新处理结果
const fetchLatestResult = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/detect/image/latest')
    if (response.ok) {
      const data = await response.json()
      if (data.result_url) {
        processedImageUrl.value = `http://localhost:5000${data.result_url}`
      }
    }
  } catch (error) {
    console.error('获取最新处理结果失败:', error)
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

// 初始化定时刷新
onMounted(() => {
  fetchLatestResult()
  refreshInterval = setInterval(fetchLatestResult, 3000)
})

// 清除定时器
onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      originalImage.value = e.target.result
      processedImage.value = null
    }
    reader.readAsDataURL(file)
  }
}

const processImage = async () => {
  if (!fileInput.value?.files[0]) return
  
  const formData = new FormData()
  formData.append('file', fileInput.value.files[0])
  
  try {
    const response = await fetch('http://localhost:5000/api/detect/image', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error('API请求失败')
    
    const result = await response.json()
    if (result.result_url) {
      processedImage.value = `http://localhost:5000${result.result_url}`
    }
  } catch (error) {
    console.error('处理图片时出错:', error)
    alert('图片处理失败，请重试')
  }
}
</script>

<style scoped>
.image-uploader {
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

.image-preview, .result-preview {
  flex: 1;
  border: 1px dashed #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  overflow: hidden;
}

.preview-image {
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
</style>
