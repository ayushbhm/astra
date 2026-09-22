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
      <div v-if="!isAuthenticated" class="login-group">
        <button class="btn-google" @click="handleLogin('user')">
          <svg viewBox="0 0 24 24" width="14" height="14">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          Google Login
        </button>
        <button class="btn-subtle" @click="handleLogin('admin')" title="Login as Admin">
          (as Admin)
        </button>
      </div>

      <div v-else class="user-pill">
        <span>{{ user.name }} ({{ user.role }})</span>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, isAuthenticated, isAdmin, login, logout } = useAuth()

const handleLogin = async (role) => {
  await login(role)
  if (role === 'admin') router.push('/adminhome')
  else router.push('/userhome')
}

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

.btn-google {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #d6d3d1;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}

.btn-subtle {
  background: none;
  border: none;
  font-size: 11px;
  color: #78716c;
  cursor: pointer;
}

.btn-subtle:hover {
  color: #7e2222;
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
