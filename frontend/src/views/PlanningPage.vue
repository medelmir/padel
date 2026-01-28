<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Planning des Événements</h1>

    <!-- Navigation mois -->
    <div class="bg-white shadow rounded-lg p-4 mb-6">
      <div class="flex justify-between items-center">
        <button 
          @click="previousMonth"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg"
        >
          ← Mois précédent
        </button>
        
        <h2 class="text-xl font-bold">
          {{ currentMonthName }} {{ currentYear }}
        </h2>
        
        <button 
          @click="nextMonth"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg"
        >
          Mois suivant →
        </button>
      </div>
    </div>

    <!-- Bouton ajouter événement (admin) -->
    <div v-if="isAdmin" class="mb-6">
      <button 
        @click="openCreateModal"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span> Nouvel événement
      </button>
    </div>

    <!-- Calendrier -->
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-600">Chargement...</p>
    </div>

    <div v-else class="bg-white shadow rounded-lg overflow-hidden">
      <!-- En-têtes jours -->
      <div class="grid grid-cols-7 bg-gray-100">
        <div v-for="day in daysOfWeek" :key="day" class="p-3 text-center font-semibold text-gray-700">
          {{ day }}
        </div>
      </div>

      <!-- Jours du mois -->
      <div class="grid grid-cols-7 border-t">
        <div 
          v-for="day in calendarDays" 
          :key="day.date"
          :class="[
            'min-h-24 p-2 border-r border-b',
            day.isCurrentMonth ? 'bg-white' : 'bg-gray-50',
            day.isToday ? 'bg-blue-50' : ''
          ]"
        >
          <div class="flex justify-between items-start mb-1">
            <span :class="[
              'text-sm font-semibold',
              day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400',
              day.isToday ? 'text-blue-600' : ''
            ]">
              {{ day.day }}
            </span>
          </div>

          <!-- Événements du jour -->
          <div class="space-y-1">
            <div 
              v-for="event in day.events" 
              :key="event.id"
              @click="showEventDetails(event)"
              class="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded cursor-pointer"
            >
              {{ event.event_time.substring(0, 5) }} - {{ event.matches.length }} match(es)
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal détails événement -->
    <div v-if="selectedEvent" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-2xl font-bold">
            Événement du {{ formatDate(selectedEvent.event_date) }}
          </h2>
          <button @click="selectedEvent = null" class="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <p class="text-gray-600 mb-4">Heure : {{ selectedEvent.event_time.substring(0, 5) }}</p>

        <div class="space-y-4">
          <h3 class="font-bold text-lg">Matchs :</h3>
          <div 
            v-for="match in selectedEvent.matches" 
            :key="match.id"
            class="border rounded-lg p-4"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="font-semibold">Piste {{ match.court_number }}</span>
              <span :class="getStatusClass(match.status)">
                {{ getStatusLabel(match.status) }}
              </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="font-medium text-blue-600">{{ match.team1.company }}</p>
                <p v-if="match.score_team1" class="text-sm">Score : {{ match.score_team1 }}</p>
              </div>
              <div>
                <p class="font-medium text-green-600">{{ match.team2.company }}</p>
                <p v-if="match.score_team2" class="text-sm">Score : {{ match.score_team2 }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="isAdmin" class="flex justify-end space-x-3 mt-6">
          <button 
            @click="editEvent(selectedEvent)"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Modifier
          </button>
          <button 
            @click="confirmDeleteEvent(selectedEvent)"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <!-- Modal création/édition événement -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <div class="bg-white rounded-lg p-6 w-full max-w-3xl my-8">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingEvent ? 'Modifier' : 'Nouvel' }} événement
        </h2>
        
        <form @submit.prevent="saveEvent">
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Date *</label>
                <input 
                  v-model="form.event_date"
                  type="date"
                  required
                  :min="today"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Heure *</label>
                <input 
                  v-model="form.event_time"
                  type="time"
                  required
                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>

            <div v-if="!editingEvent">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Nombre de matchs (1-3)
              </label>
              <select 
                v-model="matchCount"
                @change="updateMatchesArray"
                class="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option :value="1">1 match</option>
                <option :value="2">2 matchs</option>
                <option :value="3">3 matchs</option>
              </select>
            </div>

            <!-- Matchs -->
            <div v-if="!editingEvent" class="space-y-4">
              <div 
                v-for="(match, index) in form.matches" 
                :key="index"
                class="border rounded-lg p-4"
              >
                <h4 class="font-bold mb-3">Match {{ index + 1 }}</h4>
                
                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Piste *</label>
                    <select 
                      v-model="match.court_number"
                      required
                      class="w-full border border-gray-300 rounded-lg px-3 py-2"
                    >
                      <option value="">--</option>
                      <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Équipe 1 *</label>
                    <select 
                      v-model="match.team1_id"
                      required
                      class="w-full border border-gray-300 rounded-lg px-3 py-2"
                    >
                      <option value="">-- Sélectionner --</option>
                      <option 
                        v-for="team in teams" 
                        :key="team.id" 
                        :value="team.id"
                        :disabled="isTeamUsed(team.id, index)"
                      >
                        {{ team.company }}
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Équipe 2 *</label>
                    <select 
                      v-model="match.team2_id"
                      required
                      class="w-full border border-gray-300 rounded-lg px-3 py-2"
                    >
                      <option value="">-- Sélectionner --</option>
                      <option 
                        v-for="team in teams" 
                        :key="team.id" 
                        :value="team.id"
                        :disabled="isTeamUsed(team.id, index) || team.id === match.team1_id"
                      >
                        {{ team.company }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
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
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'ADMINISTRATEUR')

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())
const events = ref([])
const teams = ref([])
const loading = ref(false)
const selectedEvent = ref(null)
const showModal = ref(false)
const editingEvent = ref(null)
const saving = ref(false)
const error = ref('')
const matchCount = ref(1)

const daysOfWeek = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const form = ref({
  event_date: '',
  event_time: '',
  matches: [{ court_number: '', team1_id: '', team2_id: '' }]
})

const today = computed(() => {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

const currentMonthName = computed(() => {
  const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
  return months[currentMonth.value]
})


const parseLocalDate = (dateString) => {
  const [year, month, day] = dateString.split('-').map(Number)
  return new Date(year, month - 1, day)
}


const formatToDateString = (year, month, day) => {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

const calendarDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  
  let startDayOfWeek = firstDay.getDay() - 1
  if (startDayOfWeek === -1) startDayOfWeek = 6
  
  const daysInMonth = lastDay.getDate()
  const days = []
  

  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  const prevYear = currentMonth.value === 0 ? currentYear.value - 1 : currentYear.value
  const prevMonth = currentMonth.value === 0 ? 11 : currentMonth.value - 1
  
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    const dateStr = formatToDateString(prevYear, prevMonth, day)
    days.push({
      day,
      date: dateStr,
      isCurrentMonth: false,
      isToday: false,
      events: []
    })
  }
  

  const todayStr = today.value
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = formatToDateString(currentYear.value, currentMonth.value, day)
    
   
    const dayEvents = events.value.filter(e => {
      const eventDate = e.event_date
      return eventDate === dateStr
    })
    
    days.push({
      day,
      date: dateStr,
      isCurrentMonth: true,
      isToday: dateStr === todayStr,
      events: dayEvents
    })
  }
  
  // Jours du mois suivant
  const nextYear = currentMonth.value === 11 ? currentYear.value + 1 : currentYear.value
  const nextMonth = currentMonth.value === 11 ? 0 : currentMonth.value + 1
  const remainingDays = 35 - days.length
  
  for (let day = 1; day <= remainingDays; day++) {
    const dateStr = formatToDateString(nextYear, nextMonth, day)
    days.push({
      day,
      date: dateStr,
      isCurrentMonth: false,
      isToday: false,
      events: []
    })
  }
  
  return days
})

const loadEvents = async () => {
  loading.value = true
  try {
    const monthStr = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`
    const response = await api.get('/events', { params: { month: monthStr } })
    
   
    events.value = response.data.map(event => ({
      ...event,
      event_date: event.event_date 
    }))
    
    console.log('Events loaded:', events.value)
  } catch (err) {
    console.error('Erreur chargement événements:', err)
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

const previousMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
  loadEvents()
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  loadEvents()
}

const showEventDetails = (event) => {
  selectedEvent.value = event
}

const openCreateModal = () => {
  editingEvent.value = null
  form.value = {
    event_date: '',
    event_time: '19:00',
    matches: [{ court_number: '', team1_id: '', team2_id: '' }]
  }
  matchCount.value = 1
  error.value = ''
  showModal.value = true
}

const editEvent = (event) => {
  selectedEvent.value = null
  editingEvent.value = event
  form.value = {
    event_date: event.event_date,
    event_time: event.event_time.substring(0, 5)
  }
  error.value = ''
  showModal.value = true
}

const updateMatchesArray = () => {
  const count = parseInt(matchCount.value)
  form.value.matches = Array.from({ length: count }, () => ({
    court_number: '',
    team1_id: '',
    team2_id: ''
  }))
}

const isTeamUsed = (teamId, currentIndex) => {
  return form.value.matches.some((m, idx) => 
    idx !== currentIndex && (m.team1_id === teamId || m.team2_id === teamId)
  )
}

const saveEvent = async () => {
  saving.value = true
  error.value = ''
  
  try {
    const data = {
      event_date: form.value.event_date,
      event_time: form.value.event_time
    }
    
    console.log('Sending event data:', data)
    
    if (editingEvent.value) {
      await api.put(`/events/${editingEvent.value.id}`, data)
    } else {
      data.matches = form.value.matches.map(m => ({
        court_number: parseInt(m.court_number),
        team1_id: parseInt(m.team1_id),
        team2_id: parseInt(m.team2_id)
      }))
      await api.post('/events', data)
    }
    
    await loadEvents()
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

const confirmDeleteEvent = async (event) => {
  if (!confirm(`Confirmer la suppression de l'événement du ${formatDate(event.event_date)} ?`)) {
    return
  }
  
  try {
    await api.delete(`/events/${event.id}`)
    await loadEvents()
    selectedEvent.value = null
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const closeModal = () => {
  showModal.value = false
  editingEvent.value = null
  error.value = ''
}

const formatDate = (dateStr) => {
  const date = parseLocalDate(dateStr)
  return date.toLocaleDateString('fr-FR', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
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
    'A_VENIR': 'bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs',
    'TERMINE': 'bg-green-100 text-green-800 px-2 py-1 rounded text-xs',
    'ANNULE': 'bg-red-100 text-red-800 px-2 py-1 rounded text-xs'
  }
  return classes[status] || ''
}

onMounted(async () => {
  await Promise.all([loadEvents(), loadTeams()])
})
</script>