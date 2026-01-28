<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Administration</h1>

    <!-- Onglets -->
    <div class="bg-white shadow rounded-lg mb-6">
      <div class="flex border-b">
        <button
          @click="activeTab = 'accounts'"
          :class="[
            'px-6 py-3 font-medium',
            activeTab === 'accounts'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Comptes utilisateurs
        </button>
        <button
          @click="activeTab = 'create'"
          :class="[
            'px-6 py-3 font-medium',
            activeTab === 'create'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Créer un compte
        </button>
      </div>
    </div>

    <!-- Onglet : Liste des comptes -->
    <div v-if="activeTab === 'accounts'">
      <div v-if="loadingAccounts" class="text-center py-8">
        <p class="text-gray-600">Chargement...</p>
      </div>

      <div v-else class="bg-white shadow rounded-lg overflow-hidden">
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Joueur</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Entreprise</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Rôle</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Statut</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="account in accounts" :key="account.id">
              <td class="px-6 py-4 text-sm">{{ account.email }}</td>
              <td class="px-6 py-4 text-sm">{{ account.player_name || '-' }}</td>
              <td class="px-6 py-4 text-sm">{{ account.company || '-' }}</td>
              <td class="px-6 py-4">
                <span :class="getRoleBadge(account.role)">
                  {{ account.role === 'ADMINISTRATEUR' ? 'Admin' : 'Joueur' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="account.is_active ? 'text-green-600' : 'text-red-600'">
                  {{ account.is_active ? '✓ Actif' : '✗ Inactif' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right space-x-2">
                <button
                  @click="resetPassword(account)"
                  class="text-orange-600 hover:text-orange-800 text-sm font-medium"
                >
                  Réinitialiser
                </button>
                <button
                  @click="toggleActive(account)"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {{ account.is_active ? 'Désactiver' : 'Activer' }}
                </button>
                <button
                  v-if="account.id !== currentUserId"
                  @click="deleteAccount(account)"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Supprimer
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="accounts.length === 0" class="text-center py-8 text-gray-500">
          Aucun compte
        </div>
      </div>
    </div>

    <!-- Onglet : Créer un compte -->
    <div v-if="activeTab === 'create'">
      <div class="bg-white shadow rounded-lg p-6 max-w-2xl">
        <h2 class="text-xl font-bold mb-4">Créer un compte pour un joueur</h2>

        <div v-if="loadingPlayers" class="text-center py-8">
          <p class="text-gray-600">Chargement...</p>
        </div>

        <form v-else @submit.prevent="createAccount">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Sélectionner un joueur *
              </label>
              <select
                v-model="createForm.player_id"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Sélectionner un joueur --</option>
                <option
                  v-for="player in playersWithoutAccount"
                  :key="player.id"
                  :value="player.id"
                >
                  {{ player.first_name }} {{ player.last_name }} ({{ player.company }}) - {{ player.license_number }}
                </option>
              </select>
              <p v-if="playersWithoutAccount.length === 0" class="text-sm text-orange-600 mt-1">
                Tous les joueurs ont déjà un compte
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rôle *</label>
              <select
                v-model="createForm.role"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                <option value="JOUEUR">Joueur</option>
                <option value="ADMINISTRATEUR">Administrateur</option>
              </select>
            </div>
          </div>

          <div v-if="createError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ createError }}</p>
          </div>

          <div class="flex justify-end mt-6">
            <button
              type="submit"
              :disabled="creating || playersWithoutAccount.length === 0"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ creating ? 'Création...' : 'Créer le compte' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal mot de passe temporaire -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4 text-green-600">Compte créé / Mot de passe réinitialisé</h2>

        <div class="space-y-4">
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-yellow-800 font-semibold mb-2">IMPORTANT</p>
            <p class="text-sm text-yellow-700">
              Ce mot de passe ne sera affiché qu'une seule fois.
              Notez-le précieusement et communiquez-le à l'utilisateur.
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email :</label>
            <div class="bg-gray-100 rounded-lg px-3 py-2 font-mono text-sm">
              {{ tempCredentials.email }}
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe temporaire :</label>
            <div class="bg-gray-100 rounded-lg px-3 py-2 font-mono text-lg font-bold break-all">
              {{ tempCredentials.password }}
            </div>
            <button
              @click="copyPassword"
              class="mt-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Copier le mot de passe
            </button>
          </div>

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p class="text-sm text-blue-800">
              L'utilisateur devra changer ce mot de passe lors de sa première connexion.
            </p>
          </div>
        </div>

        <div class="flex justify-end mt-6">
          <button
            @click="closePasswordModal"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            J'ai noté le mot de passe
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const activeTab = ref('accounts')
const accounts = ref([])
const playersWithoutAccount = ref([])
const loadingAccounts = ref(false)
const loadingPlayers = ref(false)
const creating = ref(false)
const createError = ref('')
const showPasswordModal = ref(false)

const createForm = ref({
  player_id: '',
  role: 'JOUEUR'
})

const tempCredentials = ref({
  email: '',
  password: ''
})

const loadAccounts = async () => {
  loadingAccounts.value = true
  try {
    const response = await api.get('/admin/accounts')
    accounts.value = response.data
  } catch (err) {
    console.error('Erreur chargement comptes:', err)
    alert('Erreur lors du chargement des comptes')
  } finally {
    loadingAccounts.value = false
  }
}

const loadPlayersWithoutAccount = async () => {
  loadingPlayers.value = true
  try {
    const response = await api.get('/admin/players-without-account')
    playersWithoutAccount.value = response.data
  } catch (err) {
    console.error('Erreur chargement joueurs:', err)
  } finally {
    loadingPlayers.value = false
  }
}

const createAccount = async () => {
  creating.value = true
  createError.value = ''

  try {
    const response = await api.post('/admin/accounts/create', {
      player_id: parseInt(createForm.value.player_id),
      role: createForm.value.role
    })

    tempCredentials.value = {
      email: response.data.email,
      password: response.data.temporary_password
    }

    showPasswordModal.value = true

    createForm.value = {
      player_id: '',
      role: 'JOUEUR'
    }

    await Promise.all([loadAccounts(), loadPlayersWithoutAccount()])
  } catch (err) {
    createError.value = err.response?.data?.detail || 'Erreur lors de la création'
  } finally {
    creating.value = false
  }
}

const resetPassword = async (account) => {
  if (!confirm(`Réinitialiser le mot de passe de ${account.email} ?`)) {
    return
  }

  try {
    const response = await api.post(`/admin/accounts/${account.id}/reset-password`)

    tempCredentials.value = {
      email: account.email,
      password: response.data.temporary_password
    }

    showPasswordModal.value = true
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la réinitialisation')
  }
}

const toggleActive = async (account) => {
  const action = account.is_active ? 'désactiver' : 'activer'
  if (!confirm(`Confirmer ${action} le compte de ${account.email} ?`)) {
    return
  }

  try {
    await api.put(`/admin/accounts/${account.id}/toggle-active`)
    await loadAccounts()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la modification')
  }
}

const deleteAccount = async (account) => {
  if (!confirm(`⚠️ ATTENTION : Supprimer définitivement le compte de ${account.email} ?`)) {
    return
  }

  try {
    await api.delete(`/admin/accounts/${account.id}`)
    await loadAccounts()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const copyPassword = () => {
  navigator.clipboard.writeText(tempCredentials.value.password)
  alert('Mot de passe copié dans le presse-papiers')
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  tempCredentials.value = { email: '', password: '' }
}

const getRoleBadge = (role) => {
  return role === 'ADMINISTRATEUR'
    ? 'bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-semibold'
    : 'bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold'
}

onMounted(async () => {
  await Promise.all([loadAccounts(), loadPlayersWithoutAccount()])
})
</script>