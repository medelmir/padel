<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Gestion des Joueurs</h1>
      <button 
        @click="openCreateModal"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span> Nouveau joueur
      </button>
    </div>


    <!-- Liste des joueurs -->
    <div  class="bg-white shadow rounded-lg overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Nom</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Prénom</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Entreprise</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Licence</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Compte</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="player in players" :key="player.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm">{{ player.last_name }}</td>
            <td class="px-6 py-4 text-sm">{{ player.first_name }}</td>
            <td class="px-6 py-4 text-sm">{{ player.company }}</td>
            <td class="px-6 py-4 text-sm font-mono">{{ player.license_number }}</td>
            <td class="px-6 py-4 text-sm">
              <span v-if="player.has_account" class="text-green-600 font-semibold">✓ Oui</span>
              <span v-else class="text-gray-400">✗ Non</span>
            </td>
            <td class="px-6 py-4 text-right space-x-3">
              <button 
                @click="editPlayer(player)"
                class="text-blue-600 hover:text-blue-800 font-medium"
              >
                ✏️ Modifier
              </button>
              <button 
                @click="confirmDelete(player)"
                class="text-red-600 hover:text-red-800 font-medium"
              >
                🗑️ Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="players.length === 0" class="text-center py-8 text-gray-500">
        Aucun joueur enregistré
      </div>
    </div>

    <!-- Modal de création/édition -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingPlayer ? 'Modifier' : 'Nouveau' }} joueur
        </h2>
        
        <form @submit.prevent="savePlayer">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Prénom *</label>
              <input 
                v-model="form.first_name" 
                @input="markTouched('first_name')"
                type="text" 
                required
                :class="[
                  'w-full rounded-lg px-3 py-2 border focus:ring-2 focus:border-transparent',
                  inputStatusClass('first_name')
                ]"
                placeholder="Jean"
              />
              <p v-if="fieldError('first_name')" class="text-xs text-red-600 mt-1">
                {{ fieldError('first_name') }}
              </p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
              <input 
                v-model="form.last_name" 
                @input="markTouched('last_name')"
                type="text" 
                required
                :class="[
                  'w-full rounded-lg px-3 py-2 border focus:ring-2 focus:border-transparent',
                  inputStatusClass('last_name')
                ]"
                placeholder="Dupont"
              />
              <p v-if="fieldError('last_name')" class="text-xs text-red-600 mt-1">
                {{ fieldError('last_name') }}
              </p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Entreprise *</label>
              <input 
                v-model="form.company" 
                @input="markTouched('company')"
                type="text" 
                required
                :class="[
                  'w-full rounded-lg px-3 py-2 border focus:ring-2 focus:border-transparent',
                  inputStatusClass('company')
                ]"
                placeholder="Tech Corp"
              />
              <p v-if="fieldError('company')" class="text-xs text-red-600 mt-1">
                {{ fieldError('company') }}
              </p>
            </div>
            
            <div v-if="!editingPlayer">
              <label class="block text-sm font-medium text-gray-700 mb-1">N° de licence *</label>
              <input 
                v-model="form.license_number" 
                @input="markTouched('license_number')"
                type="text" 
                required
                pattern="L[0-9]{6}" 
                placeholder="L123456"
                :class="[
                  'w-full rounded-lg px-3 py-2 border focus:ring-2 focus:border-transparent font-mono',
                  inputStatusClass('license_number')
                ]"
              />
              <p v-if="fieldError('license_number')" class="text-xs text-red-600 mt-1">
                {{ fieldError('license_number') }}
              </p>
              <p class="text-xs text-gray-500 mt-1">Format : LXXXXXX (ex: L123456)</p>
            </div>
            
            <div v-if="!editingPlayer">
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input 
                v-model="form.email" 
                @input="markTouched('email')"
                type="email" 
                required
                :class="[
                  'w-full rounded-lg px-3 py-2 border focus:ring-2 focus:border-transparent',
                  inputStatusClass('email')
                ]"
                placeholder="jean.dupont@example.com"
              />
              <p v-if="fieldError('email')" class="text-xs text-red-600 mt-1">
                {{ fieldError('email') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date de naissance</label>
              <input 
                v-model="form.birth_date" 
                type="date"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ error }}</p>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button 
              type="button" 
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
            >
              Annuler
            </button>
            <button 
              type="submit"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const players = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingPlayer = ref(null)
const saving = ref(false)
const error = ref('')
const touched = ref({
  first_name: false,
  last_name: false,
  company: false,
  license_number: false,
  email: false
})

const form = ref({
  first_name: '',
  last_name: '',
  company: '',
  license_number: '',
  email: '',
  birth_date: ''
})

const validators = {
  first_name: (value) =>
    value && value.trim().length >= 2 ? '' : 'Le prenom doit contenir au moins 2 caracteres.',
  last_name: (value) =>
    value && value.trim().length >= 2 ? '' : 'Le nom doit contenir au moins 2 caracteres.',
  company: (value) =>
    value && value.trim().length >= 2 ? '' : "L'entreprise est obligatoire.",
  license_number: (value) =>
    /^L[0-9]{6}$/.test((value || '').trim()) ? '' : 'Format de licence invalide (ex: L123456).',
  email: (value) =>
    /\S+@\S+\.\S+/.test((value || '').trim()) ? '' : 'Email invalide.'
}

const markTouched = (field) => {
  touched.value[field] = true
}

const validationMessage = (field) => {
  const validator = validators[field]
  return validator ? validator(form.value[field] || '') : ''
}

const isFieldValid = (field) => validationMessage(field) === ''

const inputStatusClass = (field) => {
  if (!touched.value[field]) {
    return 'border-gray-300 focus:ring-blue-500'
  }
  return isFieldValid(field)
    ? 'border-green-500 focus:ring-green-500'
    : 'border-red-500 focus:ring-red-500'
}

const fieldError = (field) => {
  if (!touched.value[field]) return ''
  return validationMessage(field)
}

const formatErrorMessage = (detail) => {
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0]
    if (first.loc?.includes('first_name') && first.type === 'string_too_short') {
      return 'Le prenom doit contenir au moins 2 caracteres.'
    }
    if (first.loc?.includes('last_name') && first.type === 'string_too_short') {
      return 'Le nom doit contenir au moins 2 caracteres.'
    }
    return first.msg || 'Erreur lors de la sauvegarde'
  }
  if (typeof detail === 'string') return detail
  if (detail?.message) return detail.message
  return 'Erreur lors de la sauvegarde'
}

const loadPlayers = async () => {
  loading.value = true
  try {
    const response = await api.get('/players')
    players.value = response.data
  } catch (err) {
    console.error('Erreur chargement joueurs:', err)
    alert('Erreur lors du chargement des joueurs')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingPlayer.value = null
  form.value = {
    first_name: '',
    last_name: '',
    company: '',
    license_number: '',
    email: '',
    birth_date: ''
  }
  touched.value = {
    first_name: false,
    last_name: false,
    company: false,
    license_number: false,
    email: false
  }
  error.value = ''
  showModal.value = true
}

const editPlayer = (player) => {
  editingPlayer.value = player
  form.value = {
    first_name: player.first_name,
    last_name: player.last_name,
    company: player.company,
    birth_date: player.birth_date || ''
  }
  touched.value = {
    first_name: false,
    last_name: false,
    company: false,
    license_number: false,
    email: false
  }
  error.value = ''
  showModal.value = true
}

const savePlayer = async () => {
  saving.value = true
  error.value = ''

  const fieldsToCheck = ['first_name', 'last_name', 'company']
  if (!editingPlayer.value) {
    fieldsToCheck.push('license_number', 'email')
  }
  const firstInvalid = fieldsToCheck.find((field) => !isFieldValid(field))
  if (firstInvalid) {
    fieldsToCheck.forEach((field) => markTouched(field))
    error.value = validationMessage(firstInvalid)
    saving.value = false
    return
  }
  
  try {
    if (editingPlayer.value) {
      await api.put(`/players/${editingPlayer.value.id}`, form.value)
    } else {
      await api.post('/players', form.value)
    }
    await loadPlayers()
    closeModal()
  } catch (err) {
    error.value = formatErrorMessage(err.response?.data?.detail)
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (player) => {
  if (!confirm(`Confirmer la suppression de ${player.first_name} ${player.last_name} ?`)) {
    return
  }
  
  try {
    await api.delete(`/players/${player.id}`)
    await loadPlayers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const closeModal = () => {
  showModal.value = false
  editingPlayer.value = null
  error.value = ''
}

onMounted(() => {
  loadPlayers()
})
</script>
