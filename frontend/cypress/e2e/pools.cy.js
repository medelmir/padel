describe('Gestion des poules', () => {
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

  it('affiche la liste des poules', () => {
    const pools = [{ id: 1, name: 'Poule A', teams: [1, 2, 3, 4, 5, 6] }]

    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: pools }).as('getPools')

    cy.visit('/pools', { onBeforeLoad: seedAuth })
    cy.wait('@getPools')

    cy.contains('Poule A').should('be.visible')
    cy.contains('1, 2, 3, 4, 5, 6').should('be.visible')
  })

  it('bloque la creation avec un nom invalide', () => {
    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: [] }).as('getPools')

    cy.visit('/pools', { onBeforeLoad: seedAuth })
    cy.wait('@getPools')

    cy.contains('Nouvelle Poule').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Poule A"]').invoke('removeAttr', 'pattern').type('Pool A')
      cy.get('input[placeholder="1,2,3,4,5,6"]').type('1,2,3,4,5,6')
      cy.get('button[type="submit"]').click()
    })

    cy.contains('Le nom doit').should('be.visible')
  })

  it('bloque la creation avec un mauvais nombre d equipes', () => {
    cy.intercept('GET', '**/api/v1/pools', { statusCode: 200, body: [] }).as('getPools')

    cy.visit('/pools', { onBeforeLoad: seedAuth })
    cy.wait('@getPools')

    cy.contains('Nouvelle Poule').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Poule A"]').type('Poule B')
      cy.get('input[placeholder="1,2,3,4,5,6"]').type('1,2,3')
      cy.get('button[type="submit"]').click()
    })

    cy.contains('exactement 6').should('be.visible')
  })

  it('cree une poule valide', () => {
    let pools = []

    cy.intercept('GET', '**/api/v1/pools', (req) => {
      req.reply({ statusCode: 200, body: pools })
    }).as('getPools')

    cy.intercept('POST', '**/api/v1/pools', (req) => {
      const newPool = {
        id: 2,
        name: req.body.name,
        teams: req.body.team_ids
      }
      pools = [...pools, newPool]
      req.reply({ statusCode: 201, body: newPool })
    }).as('createPool')

    cy.visit('/pools', { onBeforeLoad: seedAuth })
    cy.wait('@getPools')

    cy.contains('Nouvelle Poule').click()
    cy.get('form').within(() => {
      cy.get('input[placeholder="Poule A"]').type('Poule C')
      cy.get('input[placeholder="1,2,3,4,5,6"]').type('1,2,3,4,5,6')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createPool')
    cy.wait('@getPools')
    cy.contains('Poule C').should('be.visible')
  })
})
