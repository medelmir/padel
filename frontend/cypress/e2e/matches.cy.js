describe('Gestion des matchs', () => {
  const adminUser = {
    id: 1,
    email: 'admin@padel.com',
    role: 'ADMINISTRATEUR'
  }
  const authToken = 'cypress-test-token'

  const seedAuth = (win) => {
    win.localStorage.setItem('token', authToken)
    win.localStorage.setItem('user', JSON.stringify(adminUser))
  }

  const teams = [
    {
      id: 1,
      company: 'Alpha',
      player1: { first_name: 'Alex', last_name: 'Stone' },
      player2: { first_name: 'Blake', last_name: 'Stone' }
    },
    {
      id: 2,
      company: 'Bravo',
      player1: { first_name: 'Casey', last_name: 'Vale' },
      player2: { first_name: 'Dana', last_name: 'Vale' }
    }
  ]

  const buildMatch = (overrides = {}) => ({
    id: 200,
    event: {
      event_date: '2026-01-30',
      event_time: '10:00:00'
    },
    court_number: 1,
    status: 'A_VENIR',
    team1: teams[0],
    team2: teams[1],
    score_team1: null,
    score_team2: null,
    ...overrides
  })

  beforeEach(() => {
    cy.intercept('GET', '**/profile/me', {
      statusCode: 200,
      body: { user: adminUser, player: { id: 1, first_name: 'Admin', last_name: 'User' } }
    }).as('getProfile')
  })

  it('affiche les matchs a venir', () => {
    const matches = [buildMatch()]

    cy.intercept('GET', '**/api/v1/matches*', { statusCode: 200, body: matches }).as('getMatches')
    cy.intercept('GET', '**/api/v1/teams', { statusCode: 200, body: teams }).as('getTeams')

    cy.visit('/matches', { onBeforeLoad: seedAuth })
    cy.wait('@getMatches')

    cy.contains('Alpha').should('be.visible')
    cy.contains('Bravo').should('be.visible')
    cy.contains('Piste 1').should('be.visible')
  })

  it('cree un match', () => {
    let matches = []
    const eventDate = '2026-01-31'

    cy.intercept('GET', '**/api/v1/matches*', (req) => {
      req.reply({ statusCode: 200, body: matches })
    }).as('getMatches')
    cy.intercept('GET', '**/api/v1/teams', { statusCode: 200, body: teams }).as('getTeams')
    cy.intercept('POST', '**/api/v1/matches', (req) => {
      const newMatch = buildMatch({
        id: 201,
        event: { event_date: req.body.event_date, event_time: req.body.event_time },
        court_number: req.body.court_number
      })
      matches = [newMatch]
      req.reply({ statusCode: 201, body: newMatch })
    }).as('createMatch')

    cy.visit('/matches', { onBeforeLoad: seedAuth })
    cy.wait('@getMatches')

    cy.contains('Nouveau match').click()
    cy.get('form').within(() => {
      cy.get('input[type="date"]').type(eventDate)
      cy.get('input[type="time"]').clear().type('09:30')
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('1')
      cy.get('select').eq(2).select('2')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createMatch')
    cy.wait('@getMatches')
    cy.contains('Piste 1').should('be.visible')
  })

  it('saisit un resultat et met a jour le statut', () => {
    let matches = [buildMatch()]

    cy.intercept('GET', '**/api/v1/matches*', (req) => {
      req.reply({ statusCode: 200, body: matches })
    }).as('getMatches')
    cy.intercept('GET', '**/api/v1/teams', { statusCode: 200, body: teams }).as('getTeams')
    cy.intercept('PUT', '**/api/v1/matches/200', (req) => {
      matches = [
        buildMatch({
          status: 'TERMINE',
          score_team1: req.body.score_team1,
          score_team2: req.body.score_team2
        })
      ]
      req.reply({ statusCode: 200, body: matches[0] })
    }).as('saveScore')

    cy.visit('/matches', { onBeforeLoad: seedAuth })
    cy.wait('@getMatches')

    cy.contains('Saisir').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="6-4, 6-3"]').type('6-4, 6-4')
      cy.get('input[placeholder="4-6, 3-6"]').type('4-6, 4-6')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@saveScore')
    cy.wait('@getMatches')
    cy.contains('Score : 6-4, 6-4').should('be.visible')
  })
})
