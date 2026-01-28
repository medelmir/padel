// ============================================
// FICHIER : frontend/src/views/HomePage.vue
// ============================================

<template>
  <div class="home-page">
    <div class="home-shell">
      <header class="hero">
        <h1 class="hero-title">Bienvenue sur Corpo Padel</h1>
        <p class="hero-subtitle">
          Gérez vos tournois corporatifs de padel en toute simplicité.
        </p>
      </header>

      <div v-if="!authStore.isAuthenticated" class="cta-panel">
        <p class="cta-text">
          Connectez-vous pour accéder à votre planning, vos matchs et vos résultats.
        </p>
        <router-link to="/login" class="btn btn-primary">
          Se connecter
        </router-link>
      </div>

      <div v-else class="space-y-10">
        <p class="welcome-line">
          Bonjour <span class="welcome-name">{{ authStore.user?.email }}</span> !
          <span aria-hidden="true">&#x1F44B;</span>
        </p>

        <section class="action-section">
          <div class="section-head">
            <h2>Accès rapide</h2>
            <p>Planifiez, suivez et analysez vos compétitions.</p>
          </div>

          <div class="action-grid">
            <router-link to="/planning" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F4C5;</span>
              <h3 class="action-title">Planning</h3>
              <p class="action-copy">Consultez vos prochains matchs</p>
            </router-link>

            <router-link to="/matches" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x26A1;</span>
              <h3 class="action-title">Matchs</h3>
              <p class="action-copy">Suivez vos rencontres</p>
            </router-link>

            <router-link to="/results" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F4CA;</span>
              <h3 class="action-title">Résultats</h3>
              <p class="action-copy">Classement et statistiques</p>
            </router-link>

            <router-link to="/profile" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F464;</span>
              <h3 class="action-title">Profil</h3>
              <p class="action-copy">Gérez vos informations personnelles</p>
            </router-link>
             <div v-if="authStore.isAdmin" class="admin-panel">
            <router-link to="/teams" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F91D;</span>
              <h3 class="action-title">équipes</h3>
              <p class="action-copy">Gérez vos équipes de padel</p>
            </router-link>
          </div>
           <div v-if="authStore.isAdmin" class="admin-panel">
            <router-link to="/players" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F3AF;</span>
              <h3 class="action-title">Joueurs</h3>
              <p class="action-copy">Gérez les joueurs participants</p>
            </router-link>
        </div>
           <div v-if="authStore.isAdmin" class="admin-panel">
            <router-link to="/pools" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F3C6;</span>
              <h3 class="action-title">Poules</h3>
              <p class="action-copy">Organisez les poules de competition</p>
            </router-link>
        </div>
            <div v-if="authStore.isAdmin" class="admin-panel">
            <router-link to="/admin" class="action-card">
              <span class="action-icon" aria-hidden="true">&#x1F4BC;</span>
              <h3 class="action-title">Administration</h3>
              <p class="action-copy">Acceder a l'administration</p>
            </router-link>
        </div>
          </div>
        </section>

        
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  font-family: 'Space Grotesk', 'Sora', sans-serif;
  color: #1f2a44;
  background: linear-gradient(135deg, #f3f6ff 0%, #edf7f4 100%);
}

.home-page * {
  box-sizing: border-box;
}

.home-page::before {
  content: '';
  position: absolute;
  inset: -120px auto auto -120px;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(47, 105, 255, 0.18), transparent 70%);
  pointer-events: none;
}

.home-page::after {
  content: '';
  position: absolute;
  right: -140px;
  top: 220px;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(52, 202, 165, 0.16), transparent 70%);
  pointer-events: none;
}

.home-shell {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  margin: 0 auto;
  padding: 48px 24px 72px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.hero,
.cta-panel,
.action-section {
  animation: rise-in 0.6s ease both;
}


.cta-panel {
  animation-delay: 0.08s;
}

.action-section {
  animation-delay: 0.16s;
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}


.hero-title {
  font-size: clamp(2.2rem, 3vw + 1rem, 3.1rem);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  max-width: 560px;
  font-size: 1.1rem;
  color: #5d6a80;
}

.cta-panel {
  max-width: 560px;
  margin: 0 auto;
  padding: 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(60, 72, 95, 0.12);
  box-shadow: 0 18px 32px rgba(25, 35, 65, 0.08);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cta-text {
  color: #4f5d75;
}

.welcome-line {
  text-align: center;
  font-size: 1.15rem;
  color: #2a3347;
}

.welcome-name {
  font-weight: 600;
  color: #2f69ff;
}

.action-section {
  padding: 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(60, 72, 95, 0.1);
  box-shadow: 0 16px 30px rgba(28, 36, 68, 0.06);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-head h2 {
  font-size: 1.4rem;
  font-weight: 600;
}

.section-head p {
  color: #5b677f;
  margin-top: 4px;
}

.action-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}

.action-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 20px;
  border: 1px solid rgba(60, 72, 95, 0.12);
  box-shadow: 0 10px 20px rgba(28, 36, 68, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: card-in 0.5s ease both;
}

.action-card:nth-child(1) {
  animation-delay: 0.05s;
}

.action-card:nth-child(2) {
  animation-delay: 0.1s;
}

.action-card:nth-child(3) {
  animation-delay: 0.15s;
}

.action-card:nth-child(4) {
  animation-delay: 0.2s;
}

.action-card:nth-child(5) {
  animation-delay: 0.25s;
}

.action-card:nth-child(6) {
  animation-delay: 0.3s;
}

.action-card:nth-child(7) {
  animation-delay: 0.35s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 28px rgba(28, 36, 68, 0.12);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(47, 105, 255, 0.16), rgba(53, 199, 162, 0.14));
  font-size: 1.2rem;
}

.action-title {
  font-size: 1.05rem;
  font-weight: 600;
}

.action-copy {
  color: #5f6b82;
  font-size: 0.95rem;
}

.admin-panel {
  display: flex;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary {
  background: #2f69ff;
  color: #ffffff;
  box-shadow: 0 16px 30px rgba(47, 105, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 20px 36px rgba(47, 105, 255, 0.35);
}



@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero,
  .cta-panel,
  .action-section,
  .action-card,
  .btn {
    animation: none;
    transition: none;
  }
}

@media (min-width: 1024px) {
  .hero {
    align-items: flex-start;
    text-align: left;
  }

  .cta-panel {
    margin-left: 0;
  }

  .welcome-line {
    text-align: left;
  }

  .admin-panel {
    justify-content: flex-start;
  }
}
</style>
