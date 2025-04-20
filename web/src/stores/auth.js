import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import router from '../router';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const token = ref(localStorage.getItem('token') || null);
  const isAuthenticated = ref(false);

  // 设置全局 Axios 配置
  axios.defaults.withCredentials = true; // 跨域请求带上 cookie

  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
  }

  const setAuth = (userData, authToken) => {
    user.value = userData;
    token.value = authToken;
    isAuthenticated.value = true;
    localStorage.setItem('token', authToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
  };

  const clearAuth = () => {
    user.value = null;
    token.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/login', {
        username: credentials.username,
        password: credentials.password
      });

      // 适配 Flask 返回的数据结构
      setAuth(
        response.data.user,
        response.data.token
      );

      router.push('/home');
    } catch (error) {
      clearAuth();
      throw new Error(error.response?.data?.error || '登录失败');
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/register', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        confirmPassword: userData.confirmPassword
      });

      // 设置认证状态
      setAuth({
        username: userData.username,
        email: userData.email
      }, response.data.token);

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || '注册失败，请稍后重试');
    }
  };

  const logout = () => {
    clearAuth();
    router.push('/login');
  };

  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await axios.get('/api/auth/me');
        setAuth(
          response.data.user,
          token.value
        );
      } catch (error) {
        clearAuth();
      }
    }
  };

  const updateProfile = async (profileData) => {
    try {
      // 防御性检查：确保当前用户ID存在
      // 防止在未登录或会话过期时执行删除操作
      if (!user.value?.id) {
        throw new Error('无法获取当前用户信息，请重新登录后再试');
      }

      console.log('更新用户信息:', {
        userId: user.value.id,
        profileData
      });

      const response = await axios.put(`/api/users/${user.value.id}`, {
        username: profileData.username,
        email: profileData.email,
        password: profileData.password
      });

      console.log('更新响应:', response.data);

      // 更新本地用户信息
      user.value = {
        ...user.value,
        username: profileData.username,
        email: profileData.email
      };

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || '更新失败，请稍后重试');
    }
  };

  const deleteAccount = async (password) => {
    try {
      // 三重验证检查
      if (!user.value) {
        throw new Error('用户会话已过期，请重新登录');
      }
      if (!user.value.id) {
        throw new Error('无效的用户ID');
      }
      if (!user.value.username) {
        throw new Error('无法获取用户名');
      }

      console.log('删除账号请求:', { 
        user_id: user.value.id,
        username: user.value.username,
        password: password 
      });
      
      const response = await axios.delete(`/api/users/${user.value.id}`, {
        data: { 
          username: user.value.username,
          password: password 
        },
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('删除账号响应:', response.data);
      clearAuth();
      // 确保在下一个tick执行跳转，避免潜在的问题
      setTimeout(() => {
        router.push('/login');
      }, 0);
    } catch (error) {
      throw new Error(error.response?.data?.error || '删除账号失败，请检查密码是否正确');
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    deleteAccount
  };
});
