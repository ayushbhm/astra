import { ref, computed } from 'vue'
import { authService } from '../services/authService'

// Singleton reactive state
const user = ref(authService.getUser())
const showSignInTrigger = ref(0) // bump to tell Navbar to focus/highlight sign-in

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (credential) => {
    user.value = await authService.loginWithGoogle(credential)
  }

  const logout = () => {
    authService.logout()
    user.value = null
  }

  // Any component can call this to signal the navbar sign-in button
  const promptSignIn = () => {
    showSignInTrigger.value++
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    promptSignIn,
    showSignInTrigger
  }
}
