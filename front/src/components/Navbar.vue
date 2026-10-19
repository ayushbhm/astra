<template>
  <header class="navbar">
    <div class="nav-brand">
      <router-link to="/">✦ THE JYOTISH REGISTER</router-link>
    </div>

    <nav class="nav-links">
      <router-link to="/">Home</router-link>
      <router-link to="/cases">Charts</router-link>
      <router-link v-if="isAuthenticated && !isAdmin" to="/userhome">My Charts</router-link>
      <router-link v-if="isAdmin" to="/adminhome">Admin</router-link>
    </nav>

    <div class="nav-auth">
      <!-- v-show keeps element in DOM always — Google SDK needs a stable element to render into -->
      <div v-show="!isAuthenticated" class="login-group" :class="{ 'pulse-attention': pulsing }">
        <div ref="googleButton" class="google-button-container"></div>
        <span v-if="loginStatus" class="login-status" role="status">{{ loginStatus }}</span>
        <span v-if="loginError" class="login-error">{{ loginError }}</span>
      </div>

      <div v-show="isAuthenticated" class="user-pill">
        <span>{{ user?.name }} ({{ user?.role }})</span>
        <button class="btn-logout" type="button" @click="handleLogout">Logout</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, isAuthenticated, isAdmin, login, logout, showSignInTrigger } = useAuth()

const googleButton = ref(null)
const loginError = ref('')
const loginStatus = ref('')
const pulsing = ref(false)

// Google initializes once per page. Re-rendering the button is safe and lets
// us recover its iframe after Google's popup flow has been cancelled.
let googleReady = false

const handleGoogleCredential = async (response) => {
  loginError.value = ''
  loginStatus.value = 'Google account selected; completing sign-in…'
  try {
    if (!response?.credential) {
      throw new Error('Google returned no credential. Check the browser console for the Google Identity Services error.')
    }
    await login(response.credential)
    router.push(isAdmin.value ? '/adminhome' : '/userhome')
  } catch (err) {
    console.error('Google login failed:', err)
    loginStatus.value = ''
    loginError.value = err.message || 'Google login failed'
  }
}

const renderGoogleButton = () => {
  if (!window.google || !googleButton.value || !googleReady) return
  // GIS creates an iframe inside this node. Clear any stale instance first.
  googleButton.value.replaceChildren()
  window.google.accounts.id.renderButton(googleButton.value, {
    theme: 'outline',
    size: 'medium',
    text: 'signin_with',
    shape: 'rectangular',
    logo_alignment: 'left'
  })

}

const initGoogle = () => {
  if (!window.google || !googleButton.value || googleReady) return

  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: handleGoogleCredential,
    auto_select: false
  })

  googleReady = true
  renderGoogleButton()
}

// Pulse navbar sign-in area when Home "Sign in" button is clicked
watch(showSignInTrigger, () => {
  if (!isAuthenticated.value) {
    pulsing.value = true
    setTimeout(() => { pulsing.value = false }, 1200)
  }
})

let checkInterval = null

onMounted(async () => {
  await nextTick()
  if (window.google) {
    initGoogle()
  } else {
    checkInterval = setInterval(() => {
      if (window.google) {
        clearInterval(checkInterval)
        checkInterval = null
        initGoogle()
      }
    }, 100)
  }
})

onBeforeUnmount(() => {
  if (checkInterval) clearInterval(checkInterval)
})

const handleLogout = () => {
  // Clear Google's remembered account. A full page reload recreates the GIS
  // client and button iframe for the next sign-in attempt.
  window.google?.accounts.id.disableAutoSelect()
  logout()
  window.location.assign('/')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e7e0d5;
}

.nav-brand a {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #241f1a;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  font-family: var(--font-serif);
  font-size: 13px;
  color: #57534e;
  text-decoration: none;
  font-weight: 600;
}

.nav-links a.router-link-active {
  color: #7e2222;
  border-bottom: 2px solid #7e2222;
}

.login-group {
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  padding: 2px;
}

.login-group.pulse-attention {
  animation: pulse-once 0.8s ease forwards;
}

@keyframes pulse-once {
  0%   { box-shadow: 0 0 0 0 rgba(200,155,60,0.7); }
  50%  { box-shadow: 0 0 0 8px rgba(200,155,60,0.1); }
  100% { box-shadow: 0 0 0 0 rgba(200,155,60,0); }
}

.google-button-container {
  display: flex;
  align-items: center;
  min-width: 120px;
  min-height: 40px;
}

.login-error {
  color: #b91c1c;
  font-size: 12px;
}

.login-status {
  color: #57534e;
  font-size: 12px;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #241f1a;
}

.btn-logout {
  background: none;
  border: none;
  color: #78716c;
  cursor: pointer;
  text-decoration: underline;
  font-size: 11px;
}
</style>
