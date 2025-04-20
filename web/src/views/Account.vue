<template>
  <div class="account-container">
    <div class="account-sidebar">
      <router-link 
        to="/account/profile" 
        class="sidebar-item"
        :class="{ active: $route.path === '/account/profile' }"
      >
        个人信息
      </router-link>
      <router-link 
        to="/account/edit" 
        class="sidebar-item"
        :class="{ active: $route.path === '/account/edit' }"
      >
        修改信息
      </router-link>
      <router-link 
        to="/account/delete" 
        class="sidebar-item"
        :class="{ active: $route.path === '/account/delete' }"
      >
        删除账号
      </router-link>
    </div>
    <div class="account-content">
      <router-view></router-view>
      <button @click="goToHome" class="home-btn">
        返回首页
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const goToHome = () => {
  router.push('/home')
}
</script>

<style scoped>
.home-btn {
  margin-top: 2rem;
  padding: 0.75rem 1.5rem;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.home-btn:hover {
  background-color: #1565c0;
}
.account-container {
  display: flex;
  min-height: 80vh;
}

.account-sidebar {
  width: 200px;
  padding: 1rem;
  border-right: 1px solid #eee;
}

.sidebar-item {
  display: block;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  color: #333;
  text-decoration: none;
}

.sidebar-item:hover {
  background-color: #f5f5f5;
}

.sidebar-item.active {
  background-color: #e3f2fd;
  color: #1976d2;
  font-weight: 500;
}

.account-content {
  flex: 1;
  padding: 2rem;
}
</style>
