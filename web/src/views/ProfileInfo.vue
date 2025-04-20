<template>
  <div class="profile-info">
    <h2>个人信息</h2>
    <div v-if="authStore.user" class="info-card">
      <div class="info-item">
        <span class="label">用户名：</span>
        <span class="value">{{ authStore.user.username }}</span>
      </div>
      <div class="info-item">
        <span class="label">邮箱：</span>
        <span class="value">{{ authStore.user.email }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.profile-info {
  max-width: 600px;
}

.info-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.info-item {
  margin-bottom: 1rem;
  display: flex;
}

.label {
  font-weight: 500;
  width: 100px;
  color: #555;
}

.value {
  flex: 1;
}
</style>
