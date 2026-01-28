// ============================================
// FICHIER : frontend/src/views/NotFoundPage.vue
// ============================================

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="text-center p-8">
      <div class="text-6xl font-bold text-gray-800 mb-3">404</div>
      <h1 class="text-2xl font-semibold text-gray-700 mb-2">Page inaccessible</h1>
      <p class="text-gray-600 mb-6">
        La page que vous cherchez est introuvable ou vous n'avez pas les droits.
      </p>
      <router-link
        to="/"
        class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
      >
        Retour a l'accueil
      </router-link>
    </div>
  </div>
</template>
