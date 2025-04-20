import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 设置路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 跳过需要跳过的路由检查
  if (to.meta.skipAuthCheck) {
    return next()
  }
  
  // 检查需要认证的路由
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    await authStore.checkAuth()
    if (!authStore.isAuthenticated) {
      return next('/login')
    }
  }
  
  next()
})

const mountedApp = app.mount('#app')

if (!mountedApp) {
  console.error('Vue应用挂载失败！请检查:')
  console.log('document.querySelector("#app")结果:', document.querySelector('#app'))
  console.log('Vue版本:', app.version)
} else {
  console.log('Vue应用已成功挂载')
}
