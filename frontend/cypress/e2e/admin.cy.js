describe('Administration', () => {
  const adminUser = {
    id: 1,
    email: 'admin@padel.com',
    role: 'ADMINISTRATEUR'
  }
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
  const authToken = 'cypress-test-token'

  const seedAuth = (win) => {
    win.localStorage.setItem('token', authToken)
    win.localStorage.setItem('user', JSON.stringify(adminUser))
  }

  beforeEach(() => {
    cy.intercept('GET', '**/profile/me', {
      statusCode: 200,
      body: adminProfile
    }).as('getProfile')
    cy.on('window:confirm', () => true)
  })

  it('affiche les comptes avec les donnees joueur', () => {
    const accounts = [
      {
        id: 10,
        email: 'player1@example.com',
        player_name: 'Sam Stone',
        company: 'ACME',
        role: 'JOUEUR',
        is_active: true
      }
    ]
    const playersWithout = [
      {
        id: 20,
        first_name: 'Alex',
        last_name: 'Doe',
        company: 'Solo Corp',
        license_number: 'L111111'
      }
    ]

    cy.intercept('GET', '**/admin/accounts', { statusCode: 200, body: accounts }).as('getAccounts')
    cy.intercept('GET', '**/admin/players-without-account', { statusCode: 200, body: playersWithout }).as('getPlayersWithout')

    cy.visit('/admin', { onBeforeLoad: seedAuth })
    cy.wait('@getAccounts')

    cy.contains('player1@example.com').should('be.visible')
    cy.contains('Sam Stone').should('be.visible')
    cy.contains('ACME').should('be.visible')
  })

  it('cree un compte et affiche le mot de passe temporaire', () => {
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

    cy.intercept('GET', '**/admin/accounts', (req) => {
      req.reply({ statusCode: 200, body: accounts })
    }).as('getAccounts')
    cy.intercept('GET', '**/admin/players-without-account', (req) => {
      req.reply({ statusCode: 200, body: playersWithout })
    }).as('getPlayersWithout')

    cy.intercept('POST', '**/admin/accounts/create', (req) => {
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

    cy.visit('/admin', { onBeforeLoad: seedAuth })
    cy.wait('@getPlayersWithout')

    cy.get('div.flex.border-b button').eq(1).click()
    cy.get('form').within(() => {
      cy.get('select').first().select('21')
      cy.get('select').eq(1).select('JOUEUR')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createAccount')
    cy.contains('l444444@padel.com').should('be.visible')
    cy.contains('TempPass123!').should('be.visible')
  })

  it('reinitialise un mot de passe depuis la liste', () => {
    const accounts = [
      {
        id: 11,
        email: 'reset@example.com',
        player_name: null,
        company: null,
        role: 'JOUEUR',
        is_active: true
      }
    ]

    cy.intercept('GET', '**/admin/accounts', { statusCode: 200, body: accounts }).as('getAccounts')
    cy.intercept('GET', '**/admin/players-without-account', { statusCode: 200, body: [] }).as('getPlayersWithout')
    cy.intercept('POST', '**/admin/accounts/11/reset-password', {
      statusCode: 200,
      body: { temporary_password: 'Reset123!' }
    }).as('resetPassword')

    cy.visit('/admin', { onBeforeLoad: seedAuth })
    cy.wait('@getAccounts')

    cy.contains('button', 'initialiser').click()
    cy.wait('@resetPassword')
    cy.contains('Reset123!').should('be.visible')
  })

  it('active ou desactive un compte', () => {
    let accounts = [
      {
        id: 12,
        email: 'toggle@example.com',
        player_name: null,
        company: null,
        role: 'JOUEUR',
        is_active: true
      }
    ]

    cy.intercept('GET', '**/admin/accounts', (req) => {
      req.reply({ statusCode: 200, body: accounts })
    }).as('getAccounts')
    cy.intercept('GET', '**/admin/players-without-account', { statusCode: 200, body: [] }).as('getPlayersWithout')
    cy.intercept('PUT', '**/admin/accounts/12/toggle-active', (req) => {
      accounts = [{ ...accounts[0], is_active: false }]
      req.reply({ statusCode: 200, body: { success: true } })
    }).as('toggleActive')

    cy.visit('/admin', { onBeforeLoad: seedAuth })
    cy.wait('@getAccounts')

    cy.contains('toggle@example.com')
      .parents('tr')
      .within(() => {
        cy.contains('button', 'activer').click()
      })

    cy.wait('@toggleActive')
    cy.wait('@getAccounts')
    cy.contains('Inactif').should('be.visible')
  })

  it('supprime un compte', () => {
    let accounts = [
      {
        id: 13,
        email: 'delete@example.com',
        player_name: null,
        company: null,
        role: 'JOUEUR',
        is_active: true
      }
    ]

    cy.intercept('GET', '**/admin/accounts', (req) => {
      req.reply({ statusCode: 200, body: accounts })
    }).as('getAccounts')
    cy.intercept('GET', '**/admin/players-without-account', { statusCode: 200, body: [] }).as('getPlayersWithout')
    cy.intercept('DELETE', '**/admin/accounts/13', (req) => {
      accounts = []
      req.reply({ statusCode: 204, body: {} })
    }).as('deleteAccount')

    cy.visit('/admin', { onBeforeLoad: seedAuth })
    cy.wait('@getAccounts')

    cy.contains('delete@example.com')
      .parents('tr')
      .within(() => {
        cy.contains('button', 'Supprimer').click()
      })

    cy.wait('@deleteAccount')
    cy.wait('@getAccounts')
    cy.contains('Aucun compte').should('be.visible')
  })
})
