// ============================================
// FICHIER : frontend/src/router/index.js
// ============================================

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import TeamsPage from '../views/TeamsPage.vue'
import PlayersPage from '../views/PlayersPage.vue'
import PoolPage from '../views/PoolPage.vue'
import AdminPage from '../views/AdminPage.vue'
import NotFoundPage from '../views/NotFoundPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import PlanningPage from '../views/PlanningPage.vue'
import MatchesPage from '../views/MatchesPage.vue'
import ResultsPage from '../views/ResultsPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/teams',
    name: 'teams',
    component: TeamsPage,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/players',
    name: 'Players',
    component: PlayersPage,
    meta: { requiresAuth: true , requiresAdmin: true }
  },
  {
    path: '/pools',
    name: 'pools',
    component: PoolPage,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/404',
    name: 'not-found',
    component: NotFoundPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found-catch',
    component: NotFoundPage,
    meta: { requiresAuth: false }
  }
  ,
  {
  path: '/profile',
  name: 'Profile',
  component: ProfilePage,
  meta: { requiresAuth: true }
  },
  {
  path: '/planning',
  name: 'Planning',
  component: PlanningPage,
  meta: { requiresAuth: true }
  },
  {
  path: '/matches',
  name: 'Matches',
  component: MatchesPage,
  meta: { requiresAuth: true }
  },
  {
  path: '/results',
  name: 'Results',
  component: ResultsPage,
  meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard pour protAcger les routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'not-found' })
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router

