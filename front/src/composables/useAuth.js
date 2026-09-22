import { ref, computed } from 'vue'
import { authService } from '../services/authService'

const user = ref(authService.getUser())

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (role = 'user') => {
    user.value = await authService.loginWithGoogle(role)
  }

  const logout = () => {
    authService.logout()
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout
  }
}
