<template>
  <div class="login-container">
    <h2>管理员登录</h2>
    <form @submit.prevent="handleLogin">
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
        <label for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
        />
      </div>
      <button type="submit" class="login-btn">登录</button>
    </form>
    <p class="register-link">
      没有账号？<router-link to="/register">立即注册</router-link>
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
  password: ''
})

const handleLogin = async () => {
  try {
    await authStore.login(form.value)
    router.push('/home')
  } catch (error) {
    alert('登录失败，请检查用户名或密码')
    console.error('登录失败:', error)
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.form-group {
  margin-bottom: 1rem;
}
.login-btn {
  width: 100%;
  padding: 0.5rem;
}
.register-link {
  margin-top: 1rem;
  text-align: center;
}
</style>
