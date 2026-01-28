<template>
    <div class="container mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Gestion des Équipes</h1>
        <button 
          @click="openCreateModal"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <span>+</span> Nouvelle équipe
        </button>
      </div>
  
      <!--<div v-if="loading" class="text-center py-8 text-gray-600">Chargement...</div>-->
  
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Entreprise</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Joueur 1</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Joueur 2</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Poule</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="team in teams" :key="team.id" class="hover:bg-gray-50">
              <td class="px-6 py-7 text-sm">{{ team.id }}</td>
              <td class="px-6 py-4 text-sm">{{ team.company }}</td>
              <td class="px-6 py-4 text-sm">{{ team.player1.first_name }} {{ team.player1.last_name }}</td>
              <td class="px-6 py-4 text-sm">{{ team.player2.first_name }} {{ team.player2.last_name }}</td>
              <td class="px-6 py-4 text-sm">{{ team.pool?.name || '—' }}</td>
              <td class="px-6 py-4 text-right space-x-3">
                <button @click="editTeam(team)" class="text-blue-600 hover:text-blue-800 font-medium">✏️ Modifier</button>
                <button @click="confirmDelete(team)" class="text-red-600 hover:text-red-800 font-medium">🗑️ Supprimer</button>
              </td>
            </tr>
          </tbody>
        </table>
  
        <div v-if="teams.length === 0" class="text-center py-8 text-gray-500">Aucune équipe enregistrée</div>
      </div>
  
      <!-- Modal -->
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md">
          <h2 class="text-2xl font-bold mb-4">{{ editingTeam ? 'Modifier' : 'Nouvelle' }} équipe</h2>
  
          <form @submit.prevent="saveTeam">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Joueur 1 *</label>
                <select v-model="form.player1_id" required class="w-full border rounded px-3 py-2">
                  <option disabled value="">Sélectionner</option>
                  <option v-for="player in players" :key="player.id" :value="player.id">
                    {{ player.first_name }} {{ player.last_name }} ({{ player.company }})
                  </option>
                </select>
              </div>
  
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Joueur 2 *</label>
                <select v-model="form.player2_id" required class="w-full border rounded px-3 py-2">
                  <option disabled value="">Sélectionner</option>
                  <option v-for="player in players" :key="player.id" :value="player.id">
                    {{ player.first_name }} {{ player.last_name }} ({{ player.company }})
                  </option>
                </select>
              </div>
  
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Poule</label>
                <select v-model="form.pool_id" class="w-full border rounded px-3 py-2">
                  <option :value="null">—</option>
                  <option
                    v-for="pool in pools"
                    :key="pool.id"
                    :value="pool.id"
                    :disabled="isPoolOptionDisabled(pool)"
                  >
                    {{ pool.name }} ({{ pool.teams?.length || 0 }}/6{{ isPoolOptionDisabled(pool) ? ' - complet' : '' }})
                  </option>
                </select>
              </div>
            </div>
  
            <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-red-800 text-sm">{{ error }}</p>
            </div>
  
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="closeModal" class="px-4 py-2 border rounded hover:bg-gray-100">Annuler</button>
              <button type="submit" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
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
  
  const teams = ref([])
  const players = ref([])
const pools = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingTeam = ref(null)
const saving = ref(false)
const error = ref('')

const normalizeId = (value) => {
  if (value === '' || value === null || value === undefined) {
    return null
  }
  return Number(value)
}

const isPoolOptionDisabled = (pool) => {
  if (!pool?.teams) {
    return false
  }
  if (editingTeam.value?.pool?.id === pool.id) {
    return false
  }
  return pool.teams.length >= 6
}

const form = ref({
  player1_id: '',
  player2_id: '',
  pool_id: null
})
  
  const loadTeams = async () => {
    loading.value = true
    try {
      const response = await api.get('/teams')
      teams.value = response.data
    } catch (err) {
      console.error('Erreur chargement équipes:', err)
    } finally {
      loading.value = false
    }
  }
  
  const loadPlayers = async () => {
    try {
      const response = await api.get('/players')
      players.value = response.data
    } catch (err) {
      console.error('Erreur chargement joueurs:', err)
    }
  }
  
const loadPools = async () => {
  try {
    const response = await api.get('/pools')
    pools.value = response.data.map(pool => ({
      ...pool,
      teams: pool.teams ?? []
    }))
  } catch (err) {
    console.error('Erreur chargement poules:', err)
  }
}
  
  const openCreateModal = () => {
    editingTeam.value = null
    form.value = {
      player1_id: '',
      player2_id: '',
      pool_id: null
    }
    error.value = ''
    showModal.value = true
  }
  
  const editTeam = (team) => {
    editingTeam.value = team
    form.value = {
      player1_id: team.player1.id,
      player2_id: team.player2.id,
      pool_id: team.pool?.id ?? null
    }
    error.value = ''
    showModal.value = true
  }
  
const saveTeam = async () => {
  saving.value = true
  error.value = ''
  const payload = {
    player1_id: normalizeId(form.value.player1_id),
    player2_id: normalizeId(form.value.player2_id),
    pool_id: normalizeId(form.value.pool_id)
  }

  if (payload.player1_id === null || payload.player2_id === null) {
    error.value = 'Les deux joueurs sont obligatoires'
    saving.value = false
    return
  }

  try {
    if (editingTeam.value) {
      await api.put(`/teams/${editingTeam.value.id}`, payload)
    } else {
      await api.post('/teams', payload)
    }
    await loadTeams()
    await loadPools()
    closeModal()
  } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
    } finally {
      saving.value = false
    }
  }
  
  const confirmDelete = async (team) => {
    if (!confirm(`Supprimer l'équipe de ${team.player1.first_name} et ${team.player2.first_name} ?`)) return
    try {
      await api.delete(`/teams/${team.id}`)
      await loadTeams()
      await loadPools()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }
  
  const closeModal = () => {
    showModal.value = false
    editingTeam.value = null
    error.value = ''
  }
  
  onMounted(() => {
    loadTeams()
    loadPlayers()
    loadPools()
  })
  </script>
  
