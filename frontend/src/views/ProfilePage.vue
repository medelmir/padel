<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <h1 class="text-3xl font-bold mb-6">Mon Profil</h1>

    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-600">Chargement...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Informations générales -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center gap-6 mb-6">
          <!-- Photo de profil -->
          <div class="flex-shrink-0">
            <div class="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
              <img 
                v-if="profile.player?.photo_url" 
                :src="getPhotoUrl(profile.player.photo_url)"
                alt="Photo de profil"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-4xl text-gray-400">👤</span>
            </div>
            <div class="mt-3 flex gap-2">
              <label class="cursor-pointer">
                <input 
                  type="file"
                  accept="image/jpeg,image/png,image/jpg"
                  @change="uploadPhoto"
                  class="hidden"
                />
                <span class="text-sm text-blue-600 hover:text-blue-800">Changer</span>
              </label>
              <button 
                v-if="profile.player?.photo_url"
                @click="deletePhoto"
                class="text-sm text-red-600 hover:text-red-800"
              >
                Supprimer
              </button>
            </div>
          </div>

          <!-- Infos principales -->
          <div class="flex-1">
            <h2 class="text-2xl font-bold">
              {{ profile.player?.first_name }} {{ profile.player?.last_name }}
            </h2>
            <p class="text-gray-600">{{ profile.player?.company }}</p>
            <p class="text-sm text-gray-500 font-mono mt-1">
              Licence : {{ profile.player?.license_number }}
            </p>
            <span :class="getRoleBadgeClass(profile.user?.role)">
              {{ getRoleLabel(profile.user?.role) }}
            </span>
          </div>
        </div>

        <!-- Formulaire de modification -->
        <form @submit.prevent="saveProfile" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Prénom *</label>
              <input 
                v-model="form.first_name"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
              <input 
                v-model="form.last_name"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input 
                v-model="form.email"
                type="email"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date de naissance</label>
              <input 
                v-model="form.birth_date"
                type="date"
                :max="maxBirthDate"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Entreprise (lecture seule)</label>
            <input 
              :value="profile.player?.company"
              type="text"
              disabled
              class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-100 cursor-not-allowed"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Numéro de licence (lecture seule)</label>
            <input 
              :value="profile.player?.license_number"
              type="text"
              disabled
              class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-100 cursor-not-allowed font-mono"
            />
          </div>

          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ error }}</p>
          </div>

          <div v-if="success" class="p-3 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-800 text-sm">{{ success }}</p>
          </div>

          <div class="flex justify-end">
            <button 
              type="submit"
              :disabled="saving"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ saving ? 'Enregistrement...' : 'Enregistrer les modifications' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Changement de mot de passe -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-xl font-bold mb-4">Changer le mot de passe</h3>
        
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe actuel *</label>
            <input 
              v-model="passwordForm.current_password"
              type="password"
              required
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nouveau mot de passe *</label>
            <input 
              v-model="passwordForm.new_password"
              type="password"
              required
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">
              Minimum 12 caractères, avec majuscule, minuscule, chiffre et caractère spécial
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmer le nouveau mot de passe *</label>
            <input 
              v-model="passwordForm.confirm_password"
              type="password"
              required
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div v-if="passwordError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ passwordError }}</p>
          </div>

          <div v-if="passwordSuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-800 text-sm">{{ passwordSuccess }}</p>
          </div>

          <div class="flex justify-end">
            <button 
              type="submit"
              :disabled="savingPassword"
              class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {{ savingPassword ? 'Modification...' : 'Changer le mot de passe' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const profile = ref({ user: null, player: null })
const loading = ref(false)
const saving = ref(false)
const savingPassword = ref(false)
const error = ref('')
const success = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  birth_date: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const maxBirthDate = computed(() => {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 16)
  return date.toISOString().split('T')[0]
})

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await api.get('/profile/me')
    profile.value = response.data
    
    // Remplir le formulaire
    if (response.data.player) {
      form.value = {
        first_name: response.data.player.first_name,
        last_name: response.data.player.last_name,
        email: response.data.user.email,
        birth_date: response.data.player.birth_date || ''
      }
    }
  } catch (err) {
    console.error('Erreur chargement profil:', err)
    alert('Erreur lors du chargement du profil')
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  error.value = ''
  success.value = ''
  
  try {
    await api.put('/profile/me', form.value)
    await loadProfile()
    success.value = 'Profil mis à jour avec succès'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

const uploadPhoto = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Vérifier la taille
  if (file.size > 2 * 1024 * 1024) {
    alert('Le fichier est trop volumineux (max 2MB)')
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    await api.post('/profile/me/photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadProfile()
    success.value = 'Photo mise à jour avec succès'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de l\'upload'
  }
}

const deletePhoto = async () => {
  if (!confirm('Confirmer la suppression de la photo ?')) return
  
  try {
    await api.delete('/profile/me/photo')
    await loadProfile()
    success.value = 'Photo supprimée avec succès'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la suppression'
  }
}

const changePassword = async () => {
  savingPassword.value = true
  passwordError.value = ''
  passwordSuccess.value = ''
  
  try {
    await api.post('/profile/me/change-password', passwordForm.value)
    passwordSuccess.value = 'Mot de passe modifié avec succès'
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
    setTimeout(() => { passwordSuccess.value = '' }, 3000)
  } catch (err) {
    passwordError.value = formatPasswordError(err.response?.data?.detail)
  } finally {
    savingPassword.value = false
  }
}
const formatPasswordError = (detail) => {
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0]
    if (first.loc?.includes('current_password')) return 'Mot de passe actuel incorrect.'
    if (first.loc?.includes('new_password')) return 'Le nouveau mot de passe doit contenir au moins 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.'
    if (first.loc?.includes('confirm_password')) return 'Les mots de passe ne correspondent pas.'
    return first.msg || 'Erreur lors de la modification'
  }
  if (typeof detail === 'string') {
    if (detail.toLowerCase().includes('incorrect') || detail.toLowerCase().includes('incorrecte')) return 'Mot de passe actuel incorrect.'
    return detail
  }
  if (detail?.message) return detail.message
  return 'Erreur lors de la modification'
}

const getPhotoUrl = (photoPath) => {
  if (!photoPath) return null
  if (photoPath.startsWith('http')) {
    return photoPath
  }
  const baseUrl = import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')
  return `${baseUrl}/${photoPath}`
}

const getRoleLabel = (role) => {
  return role === 'ADMINISTRATEUR' ? 'Administrateur' : 'Joueur'
}

const getRoleBadgeClass = (role) => {
  return role === 'ADMINISTRATEUR'
    ? 'inline-block mt-2 bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold'
    : 'inline-block mt-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold'
}

onMounted(() => {
  loadProfile()
})
</script>