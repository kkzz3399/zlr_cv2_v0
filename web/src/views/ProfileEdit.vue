<template>
  <div class="profile-edit">
    <h2>修改个人信息</h2>
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    <form @submit.prevent="handleSave" class="edit-form">
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          id="username" 
          v-model="form.username" 
          type="text" 
          required
        />
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">新密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          placeholder="留空则不修改"
        />
      </div>
      <div class="form-group">
        <label for="confirmPassword">确认新密码</label>
        <input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          placeholder="留空则不修改"
        />
      </div>
      <div class="form-actions">
        <button 
          type="submit" 
          class="save-btn"
          :disabled="isLoading"
        >
          {{ isLoading ? '保存中...' : '保存修改' }}
        </button>
        <router-link to="/account/profile" class="cancel-btn">
          取消
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isLoading = ref(false)
const errorMessage = ref('')

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

onMounted(() => {
  if (authStore.user) {
    form.value.username = authStore.user.username
    form.value.email = authStore.user.email
  }
})

const handleSave = async () => {
  if (form.value.password && form.value.password !== form.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  try {
    isLoading.value = true
    await authStore.updateProfile({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    errorMessage.value = ''
    router.push('/account/profile')
  } catch (error) {
    errorMessage.value = '更新失败: ' + error.message
    console.error('更新失败:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.profile-edit {
  max-width: 600px;
}

.edit-form {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.save-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background-color: #1976d2;
  color: white;
  border: none;
}

.cancel-btn {
  background: none;
  border: 1px solid #ddd;
  color: #333;
  text-decoration: none;
  text-align: center;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 1rem;
}
</style>
