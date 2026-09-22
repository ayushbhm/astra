import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Cases from '../views/cases.vue'
import UserHome from '../views/userhome.vue'
import AdminHome from '../views/adminhome.vue'
import { authService } from '../services/authService'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/cases',
    name: 'Cases',
    component: Cases
  },
  {
    path: '/userhome',
    name: 'UserHome',
    component: UserHome,
    meta: { requiresAuth: true }
  },
  {
    path: '/adminhome',
    name: 'AdminHome',
    component: AdminHome,
    meta: { requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const user = authService.getUser()

  if (to.meta.requiresAdmin && (!user || user.role !== 'admin')) {
    return next({ path: '/' })
  }

  if (to.meta.requiresAuth && !user) {
    return next({ path: '/' })
  }

  next()
})

export default router
