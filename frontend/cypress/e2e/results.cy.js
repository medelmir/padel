describe('Resultats', () => {
  const user = {
    id: 2,
    email: 'user@example.com',
    role: 'JOUEUR'
  }
  const authToken = 'cypress-test-token'

  const seedAuth = (win) => {
    win.localStorage.setItem('token', authToken)
    win.localStorage.setItem('user', JSON.stringify(user))
  }

  beforeEach(() => {
    cy.intercept('GET', '**/profile/me', {
      statusCode: 200,
      body: { user, player: { id: 10, first_name: 'Jean', last_name: 'Doe' } }
    }).as('getProfile')
  })

  it('affiche les statistiques et resultats du joueur', () => {
    const myResults = {
      statistics: { total_matches: 2, wins: 1, losses: 1, win_rate: 50.0 },
      results: [
        {
          match_id: 1,
          date: '2025-01-02',
          result: 'DEFAITE',
          score: '1-6,2-6 vs 6-1,6-2',
          opponents: { company: 'Ninjas', players: ['Cody Lane', 'Mia Vale'] },
          court_number: 3
        }
      ]
    }
    const rankings = {
      rankings: [
        {
          position: 1,
          company: 'Alpha',
          matches_played: 2,
          wins: 2,
          losses: 0,
          points: 6,
          sets_won: 4,
          sets_lost: 0
        }
      ]
    }

    cy.intercept('GET', '**/results/my-results', { statusCode: 200, body: myResults }).as('getMyResults')
    cy.intercept('GET', '**/results/rankings', { statusCode: 200, body: rankings }).as('getRankings')

    cy.visit('/results', { onBeforeLoad: seedAuth })
    cy.wait('@getMyResults')

    cy.contains('Matchs').should('be.visible')
    cy.contains('Ninjas').should('be.visible')
    cy.contains('1-6,2-6').should('be.visible')
  })

  it('affiche le classement general', () => {
    const myResults = { statistics: { total_matches: 0, wins: 0, losses: 0, win_rate: 0.0 }, results: [] }
    const rankings = {
      rankings: [
        {
          position: 1,
          company: 'Alpha',
          matches_played: 2,
          wins: 2,
          losses: 0,
          points: 6,
          sets_won: 4,
          sets_lost: 0
        },
        {
          position: 2,
          company: 'Bravo',
          matches_played: 2,
          wins: 0,
          losses: 2,
          points: 0,
          sets_won: 0,
          sets_lost: 4
        }
      ]
    }

    cy.intercept('GET', '**/results/my-results', { statusCode: 200, body: myResults }).as('getMyResults')
    cy.intercept('GET', '**/results/rankings', { statusCode: 200, body: rankings }).as('getRankings')

    cy.visit('/results', { onBeforeLoad: seedAuth })
    cy.wait('@getRankings')

    cy.contains('Classement').click()
    cy.contains('Alpha').should('be.visible')
    cy.contains('Bravo').should('be.visible')
  })
})
