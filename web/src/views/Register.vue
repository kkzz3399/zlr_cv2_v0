<template>
  <div class="register-container">
    <h2>管理员注册</h2>
        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    <form @submit.prevent="handleRegister">
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
        <label for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
        />
      </div>
      <div class="form-group">
        <label for="confirmPassword">确认密码</label>
        <input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          required
        />
      </div>
      <button 
        type="submit" 
        class="register-btn"
        :disabled="isLoading"
      >
        {{ isLoading ? '注册中...' : '注册' }}
      </button>
    </form>
    <p class="login-link">
      已有账号？<router-link to="/login">立即登录</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  try {
    await authStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      confirmPassword: form.value.confirmPassword
    })
    router.push('/home')
  } catch (error) {
    alert('注册失败，请检查用户名或邮箱是否已被注册')
    console.error('注册失败:', error)
  }
}
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}
.form-group {
  margin-bottom: 1rem;
}
.register-btn {
  width: 100%;
  padding: 0.5rem;
}
.login-link {
  margin-top: 1rem;
  text-align: center;
}
</style>
