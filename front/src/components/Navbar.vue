<template>
  <header class="navbar">
    <div class="nav-brand">
      <router-link to="/">✦ THE JYOTISH REGISTER</router-link>
    </div>

    <nav class="nav-links">
      <router-link to="/">Home</router-link>

      <router-link to="/cases">Charts</router-link>

      <router-link
        v-if="isAuthenticated && !isAdmin"
        to="/userhome"
      >
        My Charts
      </router-link>

      <router-link
        v-if="isAdmin"
        to="/adminhome"
      >
        Admin
      </router-link>
    </nav>

    <div class="nav-auth">

      <!-- NOT LOGGED IN -->
      <div
        v-if="!isAuthenticated"
        class="login-group"
      >
        <div
          ref="googleButton"
          class="google-button-container"
        ></div>
      </div>

      <!-- LOGGED IN -->
      <div
        v-else
        class="user-pill"
      >
        <span>
          {{ user.name }} ({{ user.role }})
        </span>

        <button
          class="btn-logout"
          type="button"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>

    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import BASE_URL from '../services/api'
const router = useRouter()

const {
  user,
  isAuthenticated,
  isAdmin,
  logout
} = useAuth()

const googleButton = ref(null)

let googleCheckInterval = null


/*
 * This function runs after Google successfully
 * authenticates the user.
 */
const handleGoogleCredential = async (response) => {
  try {
    const res = await fetch(
      `${BASE_URL}/google`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          credential: response.credential
        })
      }
    )

    const data = await res.json()

    if (!res.ok) {
      console.error(data.message)
      return
    }

    localStorage.setItem(
      'user',
      JSON.stringify(data.user)
    )

    if (data.user.role === 'admin') {
      router.push('/adminhome')
    } else {
      router.push('/userhome')
    }

  } catch (error) {
    console.error('Google login failed:', error)
  }
}

/*
 * Render Google's official login button.
 */
const renderGoogleButton = async () => {
  await nextTick()

  if (!googleButton.value) {
    console.error('Google button container not found.')
    return
  }

  if (!window.google) {
    console.error(
      'Google Identity Services has not loaded.'
    )
    return
  }

  /*
   * Initialize Google Identity Services.
   */
  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: handleGoogleCredential
  })

  /*
   * Render Google's actual button.
   */
  window.google.accounts.id.renderButton(
    googleButton.value,
    {
      theme: 'outline',
      size: 'medium',
      text: 'signin_with',
      shape: 'rectangular',
      logo_alignment: 'left'
    }
  )
}


/*
 * Wait for Google's script to load.
 */
const waitForGoogle = () => {

  if (window.google) {
    renderGoogleButton()
    return
  }

  googleCheckInterval = setInterval(() => {

    if (window.google) {
      clearInterval(googleCheckInterval)
      googleCheckInterval = null

      renderGoogleButton()
    }

  }, 100)
}


/*
 * Component mounted.
 */
onMounted(() => {
  waitForGoogle()
})


/*
 * Component destroyed.
 */
onBeforeUnmount(() => {

  if (googleCheckInterval) {
    clearInterval(googleCheckInterval)
    googleCheckInterval = null
  }

})


/*
 * Logout.
 */
const handleLogout = () => {
  logout()
  router.push('/')
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
}

.google-button-container {
  display: flex;
  align-items: center;
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