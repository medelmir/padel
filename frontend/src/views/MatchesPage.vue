<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Matchs à venir (30 prochains jours)</h1>

    <!-- Filtres -->
    <div class="bg-white shadow rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-if="!isAdmin">
          <label class="flex items-center gap-2">
            <input 
              type="checkbox"
              v-model="showOnlyMyMatches"
              @change="loadMatches"
              class="w-4 h-4"
            />
            <span class="text-sm font-medium text-gray-700">
              Afficher uniquement mes matchs
            </span>
          </label>
        </div>

        <div v-if="isAdmin">
          <label class="block text-sm font-medium text-gray-700 mb-1">Filtrer par statut</label>
          <select 
            v-model="filters.status"
            @change="loadMatches"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="">Tous les statuts</option>
            <option value="A_VENIR">À venir</option>
            <option value="TERMINE">Terminé</option>
            <option value="ANNULE">Annulé</option>
          </select>
        </div>

        <div v-if="isAdmin">
          <label class="block text-sm font-medium text-gray-700 mb-1">Filtrer par équipe</label>
          <select 
            v-model="filters.team_id"
            @change="loadMatches"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          >
            <option :value="null">Toutes les équipes</option>
            <option v-for="team in teams" :key="team.id" :value="team.id">
              {{ team.company }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Bouton ajouter match (admin) -->
    <div v-if="isAdmin" class="mb-6">
      <button 
        @click="openCreateModal"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span> Nouveau match
      </button>
    </div>

    <!-- Liste des matchs -->
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-600">Chargement...</p>
    </div>

    <div v-else class="space-y-4">
      <div 
        v-for="match in matches" 
        :key="match.id"
        class="bg-white shadow rounded-lg p-6 hover:shadow-lg transition"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <p class="text-lg font-bold text-gray-900">
              {{ formatDateTime(match.event.event_date, match.event.event_time) }}
            </p>
            <p class="text-sm text-gray-600">Piste {{ match.court_number }}</p>
          </div>
          <span :class="getStatusClass(match.status)">
            {{ getStatusLabel(match.status) }}
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
          <!-- Équipe 1 -->
          <div class="border-l-4 border-blue-500 pl-4">
            <h3 class="font-bold text-blue-600 mb-2">{{ match.team1.company }}</h3>
            <div class="space-y-1 text-sm">
              <p>👤 {{ match.team1.player1.first_name }} {{ match.team1.player1.last_name }}</p>
              <p>👤 {{ match.team1.player2.first_name }} {{ match.team1.player2.last_name }}</p>
            </div>
            <p v-if="match.score_team1" class="mt-2 font-semibold text-lg">
              Score : {{ match.score_team1 }}
            </p>
          </div>

          <!-- VS -->
          <div class="flex items-center justify-center md:hidden text-2xl font-bold text-gray-400">
            VS
          </div>

          <!-- Équipe 2 -->
          <div class="border-l-4 border-green-500 pl-4">
            <h3 class="font-bold text-green-600 mb-2">{{ match.team2.company }}</h3>
            <div class="space-y-1 text-sm">
              <p>👤 {{ match.team2.player1.first_name }} {{ match.team2.player1.last_name }}</p>
              <p>👤 {{ match.team2.player2.first_name }} {{ match.team2.player2.last_name }}</p>
            </div>
            <p v-if="match.score_team2" class="mt-2 font-semibold text-lg">
              Score : {{ match.score_team2 }}
            </p>
          </div>
        </div>

        <!-- Actions admin -->
        <div v-if="isAdmin" class="flex justify-end space-x-3 pt-4 border-t">
          <button 
            @click="editMatch(match)"
            class="text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            ✏️ Modifier
          </button>
          <button 
            v-if="match.status === 'A_VENIR'"
            @click="updateMatchScore(match)"
            class="text-green-600 hover:text-green-800 font-medium text-sm"
          >
            📝 Saisir résultat
          </button>
          <button 
            @click="confirmDelete(match)"
            class="text-red-600 hover:text-red-800 font-medium text-sm"
          >
            🗑️ Supprimer
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && matches.length === 0" class="text-center py-8 text-gray-500">
      Aucun match à venir
    </div>

    <!-- Modal création/édition match -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingMatch ? 'Modifier' : 'Nouveau' }} match
        </h2>
        
        <form @submit.prevent="saveMatch">
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Date *</label>
                <input 
                  v-model="form.event_date"
                  type="date"
                  required
                  :min="today"
                  :disabled="editingMatch && editingMatch.status !== 'A_VENIR'"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Heure *</label>
                <input 
                  v-model="form.event_time"
                  type="time"
                  required
                  :disabled="editingMatch && editingMatch.status !== 'A_VENIR'"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Piste *</label>
              <select 
                v-model="form.court_number"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">-- Sélectionner --</option>
                <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>

            <div v-if="!editingMatch">
              <label class="block text-sm font-medium text-gray-700 mb-1">Équipe 1 *</label>
              <select 
                v-model="form.team1_id"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">-- Sélectionner --</option>
                <option 
                  v-for="team in teams" 
                  :key="team.id" 
                  :value="team.id"
                  :disabled="team.id === form.team2_id"
                >
                  {{ team.company }}
                </option>
              </select>
            </div>

            <div v-if="!editingMatch">
              <label class="block text-sm font-medium text-gray-700 mb-1">Équipe 2 *</label>
              <select 
                v-model="form.team2_id"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">-- Sélectionner --</option>
                <option v-for="team in teams"
:key="team.id"
:value="team.id"
:disabled="team.id === form.team1_id"
>
{{ team.company }}
</option>
</select>
</div>
<div v-if="editingMatch">
          <label class="block text-sm font-medium text-gray-700 mb-1">Statut</label>
          <select 
            v-model="form.status"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="A_VENIR">À venir</option>
            <option value="ANNULE">Annulé</option>
          </select>
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

<!-- Modal saisie score -->
<div v-if="showScoreModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 w-full max-w-md">
    <h2 class="text-2xl font-bold mb-4">Saisir le résultat</h2>
    
    <form @submit.prevent="saveScore">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Score {{ scoreForm.team1_name }} *
          </label>
          <input 
            v-model="scoreForm.score_team1"
            type="text"
            required
            placeholder="6-4, 6-3"
            pattern="^\d+-\d+(,\s*\d+-\d+){1,2}$"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          />
          <p class="text-xs text-gray-500 mt-1">Format : "6-4, 6-3" ou "6-4, 3-6, 7-5"</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Score {{ scoreForm.team2_name }} *
          </label>
          <input 
            v-model="scoreForm.score_team2"
            type="text"
            required
            placeholder="4-6, 3-6"
            pattern="^\d+-\d+(,\s*\d+-\d+){1,2}$"
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
          />
        </div>
      </div>
      
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 text-sm">{{ error }}</p>
      </div>
      
      <div class="flex justify-end space-x-3 mt-6">
        <button 
          type="button" 
          @click="closeScoreModal"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
        >
          Annuler
        </button>
        <button 
          type="submit"
          :disabled="saving"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {{ saving ? 'Enregistrement...' : 'Valider le résultat' }}
        </button>
      </div>
    </form>
  </div>
</div>
    </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'ADMINISTRATEUR')

const matches = ref([])
const teams = ref([])
const loading = ref(false)
const showModal = ref(false)
const showScoreModal = ref(false)
const editingMatch = ref(null)
const saving = ref(false)
const error = ref('')
const showOnlyMyMatches = ref(true)

const filters = ref({
  status: '',
  team_id: null
})

const form = ref({
  event_date: '',
  event_time: '19:00',
  court_number: '',
  team1_id: '',
  team2_id: '',
  status: 'A_VENIR'
})

const scoreForm = ref({
  match_id: null,
  team1_name: '',
  team2_name: '',
  score_team1: '',
  score_team2: ''
})

const today = computed(() => {
  const date = new Date()
  return date.toISOString().split('T')[0]
})

const loadMatches = async () => {
  loading.value = true
  try {
    const params = { upcoming: true }
    
    if (isAdmin.value) {
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.team_id) params.team_id = filters.value.team_id
    } else {
      if (showOnlyMyMatches.value) params.my_matches = true
    }
    
    const response = await api.get('/matches', { params })
    matches.value = response.data
  } catch (err) {
    console.error('Erreur chargement matchs:', err)
    alert('Erreur lors du chargement des matchs')
  } finally {
    loading.value = false
  }
}

const loadTeams = async () => {
  try {
    const response = await api.get('/teams')
    teams.value = response.data
  } catch (err) {
    console.error('Erreur chargement équipes:', err)
  }
}

const openCreateModal = () => {
  editingMatch.value = null
  form.value = {
    event_date: '',
    event_time: '19:00',
    court_number: '',
    team1_id: '',
    team2_id: '',
    status: 'A_VENIR'
  }
  error.value = ''
  showModal.value = true
}

const editMatch = (match) => {
  editingMatch.value = match
  form.value = {
    event_date: match.event.event_date,
    event_time: match.event.event_time.substring(0, 5),
    court_number: match.court_number,
    status: match.status
  }
  error.value = ''
  showModal.value = true
}

const updateMatchScore = (match) => {
  scoreForm.value = {
    match_id: match.id,
    team1_name: match.team1.company,
    team2_name: match.team2.company,
    score_team1: match.score_team1 || '',
    score_team2: match.score_team2 || ''
  }
  error.value = ''
  showScoreModal.value = true
}

const saveMatch = async () => {
  saving.value = true
  error.value = ''
  
  try {
    const data = {
      event_date: form.value.event_date,
      event_time: form.value.event_time,
      court_number: parseInt(form.value.court_number)
    }
    
    if (editingMatch.value) {
      data.status = form.value.status
      await api.put(`/matches/${editingMatch.value.id}`, data)
    } else {
      data.team1_id = parseInt(form.value.team1_id)
      data.team2_id = parseInt(form.value.team2_id)
      await api.post('/matches', data)
    }
    
    await loadMatches()
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

const saveScore = async () => {
  saving.value = true
  error.value = ''
  
  try {
    const data = {
      status: 'TERMINE',
      score_team1: scoreForm.value.score_team1,
      score_team2: scoreForm.value.score_team2
    }
    
    await api.put(`/matches/${scoreForm.value.match_id}`, data)
    await loadMatches()
    closeScoreModal()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (match) => {
  if (!confirm('Confirmer la suppression de ce match ?')) {
    return
  }
  
  try {
    await api.delete(`/matches/${match.id}`)
    await loadMatches()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const closeModal = () => {
  showModal.value = false
  editingMatch.value = null
  error.value = ''
}

const closeScoreModal = () => {
  showScoreModal.value = false
  scoreForm.value = {
    match_id: null,
    team1_name: '',
    team2_name: '',
    score_team1: '',
    score_team2: ''
  }
  error.value = ''
}

const formatDateTime = (dateStr, timeStr) => {
  const date = new Date(dateStr)
  const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
  const months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
  
  const dayName = days[date.getDay()]
  const day = date.getDate()
  const month = months[date.getMonth()]
  const year = date.getFullYear()
  const time = timeStr.substring(0, 5)
  
  return `${dayName} ${day} ${month} ${year} à ${time}`
}

const getStatusLabel = (status) => {
  const labels = {
    'A_VENIR': 'À venir',
    'TERMINE': 'Terminé',
    'ANNULE': 'Annulé'
  }
  return labels[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    'A_VENIR': 'bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold',
    'TERMINE': 'bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold',
    'ANNULE': 'bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold'
  }
  return classes[status] || ''
}

onMounted(async () => {
  await Promise.all([loadMatches(), loadTeams()])
})
</script>