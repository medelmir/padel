describe('Gestion des joueurs', () => {
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

  beforeEach(() => {
    cy.intercept('GET', '**/api/v1/profile/me', {
      statusCode: 200,
      body: { user: adminUser, player: { id: 1, first_name: 'Admin', last_name: 'User' } }
    }).as('getProfile')
  })

  it('affiche la liste des joueurs', () => {
    const players = [
      {
        id: 1,
        first_name: 'Alice',
        last_name: 'Martin',
        company: 'Padel Corp',
        license_number: 'L999999',
        has_account: true
      }
    ]

    cy.intercept('GET', '**/api/v1/players', { statusCode: 200, body: players }).as('getPlayers')

    cy.visit('/players', { onBeforeLoad: seedAuth })
    cy.wait('@getPlayers')

    cy.contains('Alice').should('be.visible')
    cy.contains('L999999').should('be.visible')
  })

  it('bloque la creation avec licence invalide', () => {
    cy.intercept('GET', '**/api/v1/players', { statusCode: 200, body: [] }).as('getPlayers')

    cy.visit('/players', { onBeforeLoad: seedAuth })
    cy.wait('@getPlayers')

    cy.contains('Nouveau joueur').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Jean"]').type('Marie')
      cy.get('input[placeholder="Dupont"]').type('Durand')
      cy.get('input[placeholder="Tech Corp"]').type('Padel Club')
      cy.get('input[placeholder="L123456"]').type('123')
      cy.get('input[type="email"]').type('marie@example.com')
      cy.get('button[type="submit"]').click()
    })

    cy.contains('Format de licence invalide').should('be.visible')
  })

  it('cree un joueur valide', () => {
    let players = [
      {
        id: 1,
        first_name: 'Alice',
        last_name: 'Martin',
        company: 'Padel Corp',
        license_number: 'L999999',
        has_account: true
      }
    ]

    cy.intercept('GET', '**/api/v1/players', (req) => {
      req.reply({ statusCode: 200, body: players })
    }).as('getPlayers')

    cy.intercept('POST', '**/api/v1/players', (req) => {
      const newPlayer = {
        id: 2,
        first_name: req.body.first_name,
        last_name: req.body.last_name,
        company: req.body.company,
        license_number: req.body.license_number,
        has_account: false
      }
      players = [...players, newPlayer]
      req.reply({ statusCode: 201, body: newPlayer })
    }).as('createPlayer')

    cy.visit('/players', { onBeforeLoad: seedAuth })
    cy.wait('@getPlayers')

    cy.contains('Nouveau joueur').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Jean"]').type('Jean')
      cy.get('input[placeholder="Dupont"]').type('Doe')
      cy.get('input[placeholder="Tech Corp"]').type('ACME')
      cy.get('input[placeholder="L123456"]').type('L123456')
      cy.get('input[type="email"]').type('jean.doe@example.com')
      cy.get('input[type="date"]').type('1990-05-20')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createPlayer')
    cy.wait('@getPlayers')
    cy.contains('Jean').should('be.visible')
    cy.contains('L123456').should('be.visible')
  })
})
