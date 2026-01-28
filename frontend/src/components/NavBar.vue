<template>
  <nav class="nav-shell">
    <div class="nav-inner">
      <router-link to="/" class="brand">
        <div class="brand-icon">🎾</div>
        <span class="brand-text">Corpo Padel</span>
        <span class="brand-dot" aria-hidden="true"></span>
        <span class="brand-tag">Tournois d'entreprise</span>
      </router-link>

      <div class="nav-actions">
        <router-link to="/profile" class="nav-link">
          <span class="avatar">
            <img
              v-if="profilePhoto"
              :src="getPhotoUrl(profilePhoto)"
              alt="Photo de profil"
              class="avatar-img"
            />
            <span v-else class="avatar-fallback" aria-hidden="true">&#x1F464;</span>
          </span>
          <span>Profil</span>
        </router-link>
        <button type="button" class="btn-logout" @click="handleLogout">
          Déconnexion
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const authStore = useAuthStore()
const router = useRouter()

const profilePhoto = ref(null)

const loadProfile = async () => {
  try {
    const response = await api.get('/profile/me')
    profilePhoto.value = response.data.player?.photo_url || null
  } catch (err) {
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) loadProfile()
})

const getPhotoUrl = (photoPath) => {
  if (!photoPath) return null
  if (photoPath.startsWith('http')) {
    return photoPath
  }
  const baseUrl = import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')
  return `${baseUrl}/${photoPath}`
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

.nav-shell {
  --nav-bg: linear-gradient(90deg, #2646f5 0%, #2d6bff 40%, #2ac3a0 100%);
  --nav-text: #f7f9ff;
  --nav-muted: rgba(255, 255, 255, 0.8);
  --nav-border: rgba(255, 255, 255, 0.18);
  --nav-shadow: rgba(16, 24, 40, 0.22);
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--nav-bg);
  color: var(--nav-text);
  border-bottom: 1px solid var(--nav-border);
  box-shadow: 0 16px 30px var(--nav-shadow);
  font-family: 'Space Grotesk', 'Sora', sans-serif;
  animation: nav-in 0.45s ease both;
}

.nav-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.08), transparent 60%);
  pointer-events: none;
}

.nav-inner {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  text-decoration: none;
}

.brand-icon {
  font-size: 1.6rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.brand-text {
  font-size: 1.1rem;
  font-weight: 600;
}

.brand-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #fce27c;
}

.brand-tag {
  font-size: 0.85rem;
  color: var(--nav-muted);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px 8px 8px;
  border-radius: 999px;
  color: inherit;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.nav-link:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 20px rgba(23, 36, 74, 0.25);
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.22);
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-fallback {
  font-size: 1rem;
}

.btn-logout {
  border: none;
  cursor: pointer;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #ff6a5c 0%, #f05568 60%, #e23c54 100%);
  box-shadow: 0 12px 24px rgba(224, 52, 80, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-logout:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(224, 52, 80, 0.4);
}

@keyframes nav-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 720px) {
  .nav-inner {
    padding: 14px 16px;
  }

  .brand-tag,
  .brand-dot {
    display: none;
  }

  .brand-text {
    font-size: 1rem;
  }

  .btn-logout {
    padding: 10px 14px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .nav-shell,
  .nav-link,
  .btn-logout {
    animation: none;
    transition: none;
  }
}
</style>
