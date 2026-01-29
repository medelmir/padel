describe('Admin full flow', () => {
  const adminUser = {
    id: 1,
    email: 'admin@padel.com',
    role: 'ADMINISTRATEUR'
  }
  const authToken = 'cypress-test-token'

  it('admin login and manage all features', () => {
    let accounts = [
      {
        id: 10,
        email: 'player1@example.com',
        player_name: 'Sam Stone',
        company: 'ACME',
        role: 'JOUEUR',
        is_active: true
      }
    ]
    let playersWithout = [
      {
        id: 21,
        first_name: 'Alice',
        last_name: 'Woods',
        company: 'Forest Corp',
        license_number: 'L444444'
      }
    ]
    let players = [
      {
        id: 1,
        first_name: 'Alex',
        last_name: 'Stone',
        company: 'Alpha',
        license_number: 'L100001',
        has_account: false
      },
      {
        id: 2,
        first_name: 'Blake',
        last_name: 'Stone',
        company: 'Alpha',
        license_number: 'L100002',
        has_account: false
      },
      {
        id: 3,
        first_name: 'Casey',
        last_name: 'Vale',
        company: 'Bravo',
        license_number: 'L100003',
        has_account: false
      },
      {
        id: 4,
        first_name: 'Dana',
        last_name: 'Vale',
        company: 'Bravo',
        license_number: 'L100004',
        has_account: false
      }
    ]
    let teams = []
    let pools = []
    let events = []
    let matches = []

    const adminProfile = {
      user: adminUser,
      player: {
        id: 99,
        first_name: 'Admin',
        last_name: 'User',
        company: 'Padel Corp',
        license_number: 'L000001',
        photo_url: null
      }
    }

    cy.intercept('POST', '**/api/v1/auth/login', {
      statusCode: 200,
      body: {
        access_token: authToken,
        token_type: 'bearer',
        user: adminUser
      }
    }).as('login')

    cy.intercept('GET', '**/api/v1/profile/me', (req) => {
      req.reply({ statusCode: 200, body: adminProfile })
    }).as('getProfile')

    cy.intercept('GET', '**/api/v1/admin/accounts', (req) => {
      req.reply({ statusCode: 200, body: accounts })
    }).as('getAccounts')
    cy.intercept('GET', '**/api/v1/admin/players-without-account', (req) => {
      req.reply({ statusCode: 200, body: playersWithout })
    }).as('getPlayersWithout')
    cy.intercept('POST', '**/api/v1/admin/accounts/create', (req) => {
      const newAccount = {
        id: 22,
        email: 'l444444@padel.com',
        player_name: 'Alice Woods',
        company: 'Forest Corp',
        role: req.body.role,
        is_active: true
      }
      accounts = [...accounts, newAccount]
      playersWithout = []
      req.reply({
        statusCode: 201,
        body: {
          email: newAccount.email,
          temporary_password: 'TempPass123!'
        }
      })
    }).as('createAccount')
    cy.intercept('POST', '**/api/v1/admin/accounts/22/reset-password', {
      statusCode: 200,
      body: { temporary_password: 'Reset123!' }
    }).as('resetPassword')
    cy.intercept('PUT', '**/api/v1/admin/accounts/22/toggle-active', (req) => {
      accounts = accounts.map((account) =>
        account.id === 22 ? { ...account, is_active: false } : account
      )
      req.reply({ statusCode: 200, body: { success: true } })
    }).as('toggleActive')
    cy.intercept('DELETE', '**/api/v1/admin/accounts/22', (req) => {
      accounts = accounts.filter((account) => account.id !== 22)
      req.reply({ statusCode: 204, body: {} })
    }).as('deleteAccount')

    cy.intercept('GET', '**/api/v1/players', (req) => {
      req.reply({ statusCode: 200, body: players })
    }).as('getPlayers')
    cy.intercept('POST', '**/api/v1/players', (req) => {
      const newPlayer = {
        id: players.length + 1,
        first_name: req.body.first_name,
        last_name: req.body.last_name,
        company: req.body.company,
        license_number: req.body.license_number,
        has_account: false
      }
      players = [...players, newPlayer]
      req.reply({ statusCode: 201, body: newPlayer })
    }).as('createPlayer')

    cy.intercept('GET', '**/api/v1/pools', (req) => {
      req.reply({ statusCode: 200, body: pools })
    }).as('getPools')
    cy.intercept('POST', '**/api/v1/pools', (req) => {
      const newPool = {
        id: pools.length + 1,
        name: req.body.name,
        teams: req.body.team_ids
      }
      pools = [...pools, newPool]
      req.reply({ statusCode: 201, body: newPool })
    }).as('createPool')

    cy.intercept('GET', '**/api/v1/teams', (req) => {
      req.reply({ statusCode: 200, body: teams })
    }).as('getTeams')
    cy.intercept('POST', '**/api/v1/teams', (req) => {
      const player1 = players.find((p) => p.id === req.body.player1_id)
      const player2 = players.find((p) => p.id === req.body.player2_id)
      const newTeam = {
        id: teams.length + 1,
        company: player1?.company || 'Equipe',
        player1,
        player2,
        pool: null
      }
      teams = [...teams, newTeam]
      req.reply({ statusCode: 201, body: newTeam })
    }).as('createTeam')

    cy.intercept('GET', '**/api/v1/events*', (req) => {
      req.reply({ statusCode: 200, body: events })
    }).as('getEvents')
    cy.intercept('POST', '**/api/v1/events', (req) => {
      const newEvent = {
        id: events.length + 1,
        event_date: req.body.event_date,
        event_time: req.body.event_time,
        matches: (req.body.matches || []).map((match, index) => ({
          id: 100 + index,
          court_number: match.court_number,
          status: 'A_VENIR',
          team1: teams.find((t) => t.id === match.team1_id),
          team2: teams.find((t) => t.id === match.team2_id),
          score_team1: null,
          score_team2: null
        }))
      }
      events = [...events, newEvent]
      req.reply({ statusCode: 201, body: newEvent })
    }).as('createEvent')

    cy.intercept('GET', '**/api/v1/matches*', (req) => {
      req.reply({ statusCode: 200, body: matches })
    }).as('getMatches')
    cy.intercept('POST', '**/api/v1/matches', (req) => {
      const newMatch = {
        id: matches.length + 1,
        event: {
          event_date: req.body.event_date,
          event_time: req.body.event_time
        },
        court_number: req.body.court_number,
        status: 'A_VENIR',
        team1: teams.find((t) => t.id === req.body.team1_id),
        team2: teams.find((t) => t.id === req.body.team2_id),
        score_team1: null,
        score_team2: null
      }
      matches = [newMatch]
      req.reply({ statusCode: 201, body: newMatch })
    }).as('createMatch')
    cy.intercept('PUT', '**/api/v1/matches/*', (req) => {
      const matchId = Number(req.url.split('/').pop())
      matches = matches.map((match) =>
        match.id === matchId
          ? {
              ...match,
              status: req.body.status || match.status,
              score_team1: req.body.score_team1 ?? match.score_team1,
              score_team2: req.body.score_team2 ?? match.score_team2
            }
          : match
      )
      req.reply({ statusCode: 200, body: matches.find((m) => m.id === matchId) })
    }).as('updateMatch')

    cy.intercept('GET', '**/api/v1/results/my-results', {
      statusCode: 200,
      body: {
        statistics: { total_matches: 1, wins: 1, losses: 0, win_rate: 100.0 },
        results: [
          {
            match_id: 1,
            date: '2026-02-01',
            result: 'VICTOIRE',
            score: '6-4,6-4 vs 4-6,4-6',
            opponents: { company: 'Bravo', players: ['Casey Vale', 'Dana Vale'] },
            court_number: 1
          }
        ]
      }
    }).as('getMyResults')
    cy.intercept('GET', '**/api/v1/results/rankings', {
      statusCode: 200,
      body: {
        rankings: [
          {
            position: 1,
            company: 'Alpha',
            matches_played: 1,
            wins: 1,
            losses: 0,
            points: 3,
            sets_won: 2,
            sets_lost: 0
          }
        ]
      }
    }).as('getRankings')

    cy.intercept('PUT', '**/api/v1/profile/me', (req) => {
      adminProfile.user.email = req.body.email
      adminProfile.player.first_name = req.body.first_name
      adminProfile.player.last_name = req.body.last_name
      req.reply({ statusCode: 200, body: adminProfile })
    }).as('updateProfile')
    cy.intercept('POST', '**/api/v1/profile/me/change-password', {
      statusCode: 422,
      body: { detail: [{ loc: ['body', 'new_password'], msg: 'invalid' }] }
    }).as('changePassword')

    cy.on('window:confirm', () => true)

    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    cy.wait('@login')

    cy.location('pathname').should('eq', '/')

    cy.visit('/admin')
    cy.wait('@getAccounts')
    cy.contains('player1@example.com').should('be.visible')

    cy.get('div.flex.border-b button').eq(1).click()
    cy.get('form').within(() => {
      cy.get('select').first().select('21')
      cy.get('select').eq(1).select('JOUEUR')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createAccount')
    cy.contains('TempPass123!').should('be.visible')
    cy.contains("J'ai not").click()

    cy.get('div.flex.border-b button').eq(0).click()
    cy.contains('l444444@padel.com')
      .parents('tr')
      .within(() => {
        cy.contains('R').click()
      })
    cy.wait('@resetPassword')
    cy.contains('Reset123!').should('be.visible')
    cy.contains("J'ai not").click()

    cy.contains('l444444@padel.com')
      .parents('tr')
      .within(() => {
        cy.contains('D').click()
      })
    cy.wait('@toggleActive')
    cy.wait('@getAccounts')
    cy.contains('Inactif').should('be.visible')

    cy.contains('l444444@padel.com')
      .parents('tr')
      .within(() => {
        cy.contains('Supprimer').click()
      })
    cy.wait('@deleteAccount')
    cy.wait('@getAccounts')

    cy.visit('/players')
    cy.wait('@getPlayers')
    cy.contains('Nouveau joueur').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Jean"]').type('Jean')
      cy.get('input[placeholder="Dupont"]').type('Doe')
      cy.get('input[placeholder="Tech Corp"]').type('Alpha')
      cy.get('input[placeholder="L123456"]').type('L200001')
      cy.get('input[type="email"]').type('jean.doe@example.com')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createPlayer')
    cy.wait('@getPlayers')
    cy.contains('Jean').should('be.visible')

    cy.visit('/teams')
    cy.wait('@getTeams')
    cy.contains('Nouvelle').click()
    cy.get('form').within(() => {
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('2')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createTeam')
    cy.wait('@getTeams')
    cy.contains('Alpha').should('be.visible')

    cy.contains('Nouvelle').click()
    cy.get('form').within(() => {
      cy.get('select').eq(0).select('3')
      cy.get('select').eq(1).select('4')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createTeam')
    cy.wait('@getTeams')
    cy.contains('Bravo').should('be.visible')

    cy.visit('/pools')
    cy.wait('@getPools')
    cy.contains('Nouvelle').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Poule A"]').type('Poule C')
      cy.get('input[placeholder="1,2,3,4,5,6"]').type('1,2,3,4,5,6')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createPool')
    cy.wait('@getPools')
    cy.contains('Poule C').should('be.visible')

    cy.visit('/planning')
    cy.wait('@getEvents')
    cy.contains('Nouvel').click()
    cy.get('form').within(() => {
      cy.get('input[type="date"]').type('2026-01-29')
      cy.get('input[type="time"]').clear().type('09:00')
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('1')
      cy.get('select').eq(2).select('1')
      cy.get('select').eq(3).select('2')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createEvent')
    cy.wait('@getEvents')
    cy.contains('09:00').should('be.visible')

    cy.visit('/matches')
    cy.wait('@getMatches')
    cy.contains('Nouveau match').click()
    cy.get('form').within(() => {
      cy.get('input[type="date"]').type('2026-02-01')
      cy.get('input[type="time"]').clear().type('10:00')
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('1')
      cy.get('select').eq(2).select('2')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@createMatch')
    cy.wait('@getMatches')
    cy.contains('Piste 1').should('be.visible')

    cy.contains('Saisir').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="6-4, 6-3"]').type('6-4, 6-4')
      cy.get('input[placeholder="4-6, 3-6"]').type('4-6, 4-6')
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@updateMatch')
    cy.wait('@getMatches')
    cy.contains('Score : 6-4, 6-4').should('be.visible')

    cy.visit('/results')
    cy.wait('@getMyResults')
    cy.contains('VICTOIRE').should('be.visible')
    cy.contains(/Classement/).click()
    cy.wait('@getRankings')
    cy.contains('Alpha').should('be.visible')

    cy.visit('/profile')
    cy.wait('@getProfile')
    cy.get('input[type="text"]').first().clear().type('Admin')
    cy.get('input[type="text"]').eq(1).clear().type('User')
    cy.get('input[type="email"]').clear().type('admin@padel.com')
    cy.contains('Enregistrer les modifications').click()
    cy.wait('@updateProfile')

    cy.get('input[type="password"]').eq(0).type('OldPass123!')
    cy.get('input[type="password"]').eq(1).type('short')
    cy.get('input[type="password"]').eq(2).type('short')
    cy.get('form').last().within(() => {
      cy.get('button[type="submit"]').click()
    })
    cy.wait('@changePassword')
    cy.contains('Le nouveau mot de passe').should('be.visible')
  })
})
