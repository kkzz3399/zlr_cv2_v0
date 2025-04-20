import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Account = () => import('../views/Account.vue')
const Home = () => import('../views/Home.vue')
const RedirectToLogin = () => import('../views/RedirectToLogin.vue')

const routes = [
  {
    path: '/',
    redirect: '/home' // 根路径自动跳转到主界面
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true } // 需要登录
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { skipAuthCheck: true } // 跳过登录检查
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { skipAuthCheck: true }
  },
  {
    path: '/account',
    name: 'Account',
    component: Account,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/ProfileInfo.vue')
      },
      {
        path: 'edit',
        name: 'ProfileEdit',
        component: () => import('../views/ProfileEdit.vue')
      },
      {
        path: 'delete',
        name: 'DeleteAccount',
        component: () => import('../views/DeleteAccount.vue')
      },
      {
        path: '',
        redirect: { name: 'Profile' }
      }
    ]
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/home' // 或指向专门的404页面
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果目标路由需要认证且未登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } 
  // 如果已登录但访问的是登录/注册页
  else if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/home') // 跳转到主界面
  }
  else {
    next() // 正常放行
  }
})

export default router