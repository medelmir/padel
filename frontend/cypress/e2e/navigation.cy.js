describe('Navigation', () => {
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
    cy.clearLocalStorage()
    cy.intercept('GET', '**/api/v1/profile/me', {
      statusCode: 200,
      body: {
        user: adminUser,
        player: { id: 1, first_name: 'Admin', last_name: 'User', photo_url: null }
      }
    }).as('getProfile')
  })

  it("Visiteur ne peut acceder qu'a l'accueil", () => {
    cy.visit('/')
    cy.contains('Bienvenue sur Corpo Padel').should('be.visible')
    cy.contains('Se connecter').should('be.visible')
  })

  it('Visiteur est redirige vers login pour les pages protegees', () => {
    cy.visit('/planning')
    cy.url().should('include', '/login')

    cy.visit('/matches')
    cy.url().should('include', '/login')

    cy.visit('/results')
    cy.url().should('include', '/login')

    cy.visit('/profile')
    cy.url().should('include', '/login')
  })

  it('Joueur connecte peut naviguer dans l application', () => {
    cy.visit('/', { onBeforeLoad: seedAuth })

    cy.contains('Corpo Padel').should('be.visible')
    cy.contains('Planning').should('be.visible')
    cy.contains('Matchs').should('be.visible')
    cy.contains(/R.?sultats/).should('be.visible')
    cy.contains('admin@padel.com').should('be.visible')
  })

  it('Navbar affiche le menu admin pour les administrateurs', () => {
    cy.visit('/', { onBeforeLoad: seedAuth })

    cy.contains('Administration').should('be.visible')
  })
})
