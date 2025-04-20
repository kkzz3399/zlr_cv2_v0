<template>
  <div class="delete-account">
    <h2>删除账号</h2>
    <div class="warning-card">
      <h3>警告</h3>
      <p>删除账号将永久移除您的所有数据，此操作不可撤销。</p>
      <p>请输入您的账号和密码确认删除操作：</p>
    </div>

    <form @submit.prevent="handleDelete" class="delete-form">
      <div class="form-group">
        <label for="username">账号</label>
        <input
          id="username"
          v-model="username"
          type="text"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
        />
      </div>
      <div class="form-actions">
        <button 
          type="submit" 
          class="delete-btn"
          :disabled="isLoading"
        >
          {{ isLoading ? '处理中...' : '确认删除账号' }}
        </button>
        <router-link to="/account/profile" class="cancel-btn">
          取消
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('') 
const password = ref('')
const isLoading = ref(false)

const handleDelete = async () => {
  if (!confirm('确定要永久删除您的账号吗？此操作不可撤销！')) {
    return
  }

  try {
    isLoading.value = true
    await authStore.deleteAccount({
      username: username.value,
      password: password.value
    })
    router.push('/login')
  } catch (error) {
    alert('删除失败: ' + error.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.delete-account {
  max-width: 600px;
}

.warning-card {
  background-color: #fff8e1;
  border-left: 4px solid #ffc107;
  padding: 1rem;
  margin-bottom: 2rem;
}

.warning-card h3 {
  color: #d32f2f;
  margin-top: 0;
}

.delete-form {
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

.delete-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn {
  background-color: #d32f2f;
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
</style>
