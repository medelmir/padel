describe('Gestion des equipes', () => {
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

  const players = [
    { id: 1, first_name: 'Alex', last_name: 'Stone', company: 'Alpha' },
    { id: 2, first_name: 'Blake', last_name: 'Stone', company: 'Alpha' },
    { id: 3, first_name: 'Casey', last_name: 'Vale', company: 'Bravo' }
  ]

  beforeEach(() => {
    cy.intercept('GET', '**/api/v1/profile/me', {
      statusCode: 200,
      body: { user: adminUser, player: { id: 1, first_name: 'Admin', last_name: 'User' } }
    }).as('getProfile')
  })

  it('affiche les equipes', () => {
    const teams = [
      {
        id: 10,
        company: 'Alpha',
        player1: players[0],
        player2: players[1],
        pool: { id: 1, name: 'Poule A' }
      }
    ]
    const pools = [{ id: 1, name: 'Poule A', teams: [10] }]

    cy.intercept('GET', '**/api/v1/teams', { statusCode: 200, body: teams }).as('getTeams')
    cy.intercept('GET', '**/api/v1/players', { statusCode: 200, body: players }).as('getPlayers')
    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: pools }).as('getPools')

    cy.visit('/teams', { onBeforeLoad: seedAuth })
    cy.wait('@getTeams')

    cy.contains('Alpha').should('be.visible')
    cy.contains('Alex Stone').should('be.visible')
    cy.contains('Blake Stone').should('be.visible')
  })

  it('bloque la creation sans joueurs', () => {
    cy.intercept('GET', '**/api/v1/teams', { statusCode: 200, body: [] }).as('getTeams')
    cy.intercept('GET', '**/api/v1/players', { statusCode: 200, body: players }).as('getPlayers')
    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: [] }).as('getPools')

    cy.visit('/teams', { onBeforeLoad: seedAuth })
    cy.wait('@getTeams')

    cy.contains('Nouvelle').click()
    cy.get('form').within(() => {
      cy.get('select').invoke('removeAttr', 'required')
      cy.get('button[type="submit"]').click()
    })

    cy.contains('joueurs').should('be.visible')
  })

  it('cree une equipe valide', () => {
    let teams = []
    const pools = [{ id: 1, name: 'Poule A', teams: [] }]

    cy.intercept('GET', '**/api/v1/teams', (req) => {
      req.reply({ statusCode: 200, body: teams })
    }).as('getTeams')
    cy.intercept('GET', '**/api/v1/players', { statusCode: 200, body: players }).as('getPlayers')
    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: pools }).as('getPools')

    cy.intercept('POST', '**/api/v1/teams', (req) => {
      const newTeam = {
        id: 11,
        company: 'Alpha',
        player1: players.find((p) => p.id === req.body.player1_id),
        player2: players.find((p) => p.id === req.body.player2_id),
        pool: { id: 1, name: 'Poule A' }
      }
      teams = [...teams, newTeam]
      req.reply({ statusCode: 201, body: newTeam })
    }).as('createTeam')

    cy.visit('/teams', { onBeforeLoad: seedAuth })
    cy.wait('@getTeams')

    cy.contains('Nouvelle').click()
    cy.get('form').within(() => {
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('2')
      cy.get('select').eq(2).select('1')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createTeam')
    cy.wait('@getTeams')
    cy.contains('Alpha').should('be.visible')
  })
})
