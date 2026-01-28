<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Gestion des Poules</h1>
      <button 
        @click="openCreateModal"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span> Nouvelle Poule
      </button>
    </div>

    <!-- Message de chargement -->
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-600">Chargement...</p>
    </div>

    <!-- Liste des poules -->
    <div v-else class="bg-white shadow rounded-lg overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Nom</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Équipes (IDs)</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="pool in pools" :key="pool.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm">{{ pool.name }}</td>
            <td class="px-6 py-4 text-sm">{{ pool.teams.join(', ') }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="editPool(pool)" class="text-blue-600 hover:text-blue-800 font-medium">✏️ Modifier</button>
              <button @click="confirmDelete(pool)" class="text-red-600 hover:text-red-800 font-medium">🗑️ Supprimer</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="pools.length === 0" class="text-center py-8 text-gray-500">
        Aucune poule enregistrée
      </div>
    </div>

    <!-- Modal de création/édition -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingPool ? 'Modifier' : 'Nouvelle' }} poule
        </h2>

        <form @submit.prevent="savePool">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
              <input 
                v-model="form.name" 
                type="text" 
                required
                pattern="^[Pp]oule\s[A-Z]$"
                placeholder="Poule A"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 mt-1">Format : Poule X (ex: Poule A)</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">IDs des équipes *</label>
              <input 
                v-model="form.team_ids" 
                type="text" 
                required
                placeholder="1,2,3,4,5,6"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 mt-1">Séparez les IDs par des virgules. Exactement 6 équipes.</p>
            </div>
          </div>

          <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ error }}</p>
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100">Annuler</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
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

const pools = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingPool = ref(null)
const saving = ref(false)
const error = ref('')

const form = ref({ name: '', team_ids: '' })

const loadPools = async () => {
  loading.value = true
  try {
    const response = await api.get('/pools')
    pools.value = response.data
  } catch (err) {
    console.error('Erreur chargement poules:', err)
    alert('Erreur lors du chargement des poules')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingPool.value = null
  form.value = { name: '', team_ids: '' }
  error.value = ''
  showModal.value = true
}

const editPool = (pool) => {
  editingPool.value = pool
  form.value = { name: pool.name, team_ids: pool.teams.join(',') }
  error.value = ''
  showModal.value = true
}

const savePool = async () => {
  saving.value = true
  error.value = ''

  // Trim du nom et conversion des IDs en tableau d'entiers
  const nameTrimmed = form.value.name.trim()
  const teamIdsArray = form.value.team_ids
    .split(',')
    .map(id => parseInt(id.trim()))
    .filter(id => !isNaN(id))

  // Validation frontend
  if (!/^[Pp]oule\s[A-Z]$/.test(nameTrimmed)) {
    error.value = "Le nom doit être au format 'Poule X' (ex: Poule A)"
    saving.value = false
    return
  }

  if (teamIdsArray.length !== 6) {
    error.value = 'Une poule doit contenir exactement 6 équipes.'
    saving.value = false
    return
  }

  try {
    if (editingPool.value) {
      await api.put(`/pools/${editingPool.value.id}`, {
        name: nameTrimmed,
        team_ids: teamIdsArray
      })
    } else {
      await api.post('/pools', {
        name: nameTrimmed,
        team_ids: teamIdsArray
      })
    }
    await loadPools()
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (pool) => {
  if (!confirm(`Confirmer la suppression de ${pool.name} ?`)) return
  try {
    await api.delete(`/pools/${pool.id}`)
    await loadPools()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const closeModal = () => {
  showModal.value = false
  editingPool.value = null
  error.value = ''
}

onMounted(() => {
  loadPools()
})
</script>