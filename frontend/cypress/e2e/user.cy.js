describe('User full flow', () => {
  const user = {
    id: 2,
    email: 'user@example.com',
    role: 'JOUEUR'
  }
  const authToken = 'cypress-test-token-user'

  it('user login and main features', () => {
    const profile = {
      user,
      player: {
        id: 10,
        first_name: 'Jean',
        last_name: 'Dupont',
        company: 'ACME Corp',
        license_number: 'L123456',
        birth_date: '1990-05-20',
        photo_url: null
      }
    }

    const myMatch = {
      id: 1,
      event: { event_date: '2026-01-30', event_time: '10:00:00' },
      court_number: 1,
      status: 'A_VENIR',
      team1: {
        company: 'ACME Corp',
        player1: { first_name: 'Jean', last_name: 'Dupont' },
        player2: { first_name: 'Sam', last_name: 'Partner' }
      },
      team2: {
        company: 'Rivals',
        player1: { first_name: 'Olivia', last_name: 'Roe' },
        player2: { first_name: 'Nina', last_name: 'Rowe' }
      },
      score_team1: null,
      score_team2: null
    }

    cy.intercept('POST', '**/api/v1/auth/login', {
      statusCode: 200,
      body: {
        access_token: authToken,
        token_type: 'bearer',
        user
      }
    }).as('login')

    cy.intercept('GET', '**/api/v1/profile/me', {
      statusCode: 200,
      body: profile
    }).as('getProfile')

    cy.intercept('GET', '**/api/v1/matches*', {
      statusCode: 200,
      body: [myMatch]
    }).as('getMatches')

    cy.intercept('GET', '**/api/v1/results/my-results', {
      statusCode: 200,
      body: {
        statistics: { total_matches: 1, wins: 1, losses: 0, win_rate: 100.0 },
        results: [
          {
            match_id: 1,
            date: '2026-01-30',
            result: 'VICTOIRE',
            score: '6-4,6-4 vs 4-6,4-6',
            opponents: { company: 'Rivals', players: ['Olivia Roe', 'Nina Rowe'] },
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
            company: 'ACME Corp',
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
      profile.user.email = req.body.email
      profile.player.first_name = req.body.first_name
      profile.player.last_name = req.body.last_name
      req.reply({ statusCode: 200, body: profile })
    }).as('updateProfile')

    cy.intercept('POST', '**/api/v1/profile/me/change-password', {
      statusCode: 422,
      body: { detail: [{ loc: ['body', 'new_password'], msg: 'invalid' }] }
    }).as('changePassword')

    cy.visit('/login')
    cy.get('input[type="email"]').type('user@example.com')
    cy.get('input[type="password"]').type('UserPass123!')
    cy.get('button[type="submit"]').click()
    cy.wait('@login')

    cy.location('pathname').should('eq', '/')

    cy.visit('/matches')
    cy.wait('@getMatches')
    cy.contains('ACME Corp').should('be.visible')
    cy.contains('Rivals').should('be.visible')

    cy.visit('/results')
    cy.wait('@getMyResults')
    cy.contains('VICTOIRE').should('be.visible')
    cy.contains(/Classement/).click()
    cy.wait('@getRankings')
    cy.contains('ACME Corp').should('be.visible')

    cy.visit('/profile')
    cy.wait('@getProfile')
    cy.get('input[type="text"]').first().clear().type('Jean')
    cy.get('input[type="text"]').eq(1).clear().type('Dupont')
    cy.get('input[type="email"]').clear().type('user@example.com')
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
