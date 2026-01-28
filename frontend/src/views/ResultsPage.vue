<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Résultats</h1>

    <!-- Onglets -->
    <div class="bg-white shadow rounded-lg mb-6">
      <div class="flex border-b">
        <button 
          @click="activeTab = 'my-results'"
          :class="[
            'px-6 py-3 font-medium',
            activeTab === 'my-results' 
              ? 'border-b-2 border-blue-600 text-blue-600' 
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Mes résultats
        </button>
        <button 
          @click="activeTab = 'rankings'"
          :class="[
            'px-6 py-3 font-medium',
            activeTab === 'rankings' 
              ? 'border-b-2 border-blue-600 text-blue-600' 
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Classement général
        </button>
      </div>
    </div>

    <!-- Onglet : Mes résultats -->
    <div v-if="activeTab === 'my-results'">
      <div v-if="loadingMyResults" class="text-center py-8">
        <p class="text-gray-600">Chargement...</p>
      </div>

      <div v-else>
        <!-- Statistiques -->
        <div v-if="myResults.statistics" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-white shadow rounded-lg p-4">
            <p class="text-gray-600 text-sm">Matchs joués</p>
            <p class="text-3xl font-bold text-blue-600">{{ myResults.statistics.total_matches }}</p>
          </div>
          
          <div class="bg-white shadow rounded-lg p-4">
            <p class="text-gray-600 text-sm">Victoires</p>
            <p class="text-3xl font-bold text-green-600">{{ myResults.statistics.wins }}</p>
          </div>
          
          <div class="bg-white shadow rounded-lg p-4">
            <p class="text-gray-600 text-sm">Défaites</p>
            <p class="text-3xl font-bold text-red-600">{{ myResults.statistics.losses }}</p>
          </div>
          
          <div class="bg-white shadow rounded-lg p-4">
            <p class="text-gray-600 text-sm">Taux de victoire</p>
            <p class="text-3xl font-bold text-purple-600">{{ myResults.statistics.win_rate }}%</p>
          </div>
        </div>

        <!-- Liste des résultats -->
        <div class="space-y-4">
          <div 
            v-for="result in myResults.results" 
            :key="result.match_id"
            class="bg-white shadow rounded-lg p-6"
          >
            <div class="flex justify-between items-start mb-3">
              <div>
                <p class="text-lg font-bold">{{ formatDate(result.date) }}</p>
                <p class="text-sm text-gray-600">Piste {{ result.court_number }}</p>
              </div>
              <span :class="getResultClass(result.result)">
                {{ result.result }}
              </span>
            </div>

            <div class="mb-2">
              <p class="text-gray-700 font-medium">Adversaires :</p>
              <p class="text-gray-900">{{ result.opponents.company }}</p>
              <p class="text-sm text-gray-600">
                {{ result.opponents.players.join(' & ') }}
              </p>
            </div>

            <div>
              <p class="text-gray-700 font-medium">Score :</p>
              <p class="text-lg font-mono">{{ result.score }}</p>
            </div>
          </div>
        </div>

        <div v-if="myResults.results && myResults.results.length === 0" class="text-center py-8 text-gray-500">
          Aucun résultat pour le moment
        </div>
      </div>
    </div>

    <!-- Onglet : Classement -->
    <div v-if="activeTab === 'rankings'">
      <div v-if="loadingRankings" class="text-center py-8">
        <p class="text-gray-600">Chargement...</p>
      </div>

      <div v-else class="bg-white shadow rounded-lg overflow-hidden">
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Pos</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Entreprise</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">Matchs</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">V</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">D</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">Points</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">Sets +</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">Sets -</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr 
              v-for="entry in rankings.rankings" 
              :key="entry.position"
              :class="entry.position <= 3 ? 'bg-yellow-50' : ''"
            >
              <td class="px-6 py-4 text-center">
                <span :class="[
                  'font-bold text-lg',
                  entry.position === 1 ? 'text-yellow-500' : '',
                  entry.position === 2 ? 'text-gray-400' : '',
                  entry.position === 3 ? 'text-orange-600' : ''
                ]">
                  {{ entry.position === 1 ? '🥇' : entry.position === 2 ? '🥈' : entry.position === 3 ? '🥉' : entry.position }}
                </span>
              </td>
              <td class="px-6 py-4 font-medium">{{ entry.company }}</td>
              <td class="px-6 py-4 text-center">{{ entry.matches_played }}</td>
              <td class="px-6 py-4 text-center text-green-600 font-semibold">{{ entry.wins }}</td>
              <td class="px-6 py-4 text-center text-red-600 font-semibold">{{ entry.losses }}</td>
              <td class="px-6 py-4 text-center font-bold text-blue-600">{{ entry.points }}</td>
              <td class="px-6 py-4 text-center">{{ entry.sets_won }}</td>
              <td class="px-6 py-4 text-center">{{ entry.sets_lost }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="rankings.rankings && rankings.rankings.length === 0" class="text-center py-8 text-gray-500">
          Aucun classement disponible
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const activeTab = ref('my-results')
const myResults = ref({ results: [], statistics: null })
const rankings = ref({ rankings: [] })
const loadingMyResults = ref(false)
const loadingRankings = ref(false)

const loadMyResults = async () => {
  loadingMyResults.value = true
  try {
    const response = await api.get('/results/my-results')
    myResults.value = response.data
  } catch (err) {
    console.error('Erreur chargement résultats:', err)
    if (err.response?.status !== 404) {
      alert('Erreur lors du chargement des résultats')
    }
  } finally {
    loadingMyResults.value = false
  }
}

const loadRankings = async () => {
  loadingRankings.value = true
  try {
    const response = await api.get('/results/rankings')
    rankings.value = response.data
  } catch (err) {
    console.error('Erreur chargement classement:', err)
    alert('Erreur lors du chargement du classement')
  } finally {
    loadingRankings.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

const getResultClass = (result) => {
  return result === 'VICTOIRE' 
    ? 'bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold'
    : 'bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold'
}

onMounted(async () => {
  await Promise.all([loadMyResults(), loadRankings()])
})
</script>