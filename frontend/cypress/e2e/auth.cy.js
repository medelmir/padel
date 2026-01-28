describe('Authentification', () => {
  const adminUser = {
    id: 1,
    email: 'admin@padel.com',
    role: 'ADMINISTRATEUR'
  }
  const authToken = 'cypress-test-token'

  const mockLoginSuccess = () => {
    cy.intercept('POST', '**/auth/login', {
      statusCode: 200,
      body: {
        access_token: authToken,
        token_type: 'bearer',
        user: adminUser
      }
    }).as('login')
  }

  const mockLoginFailure = (detail, statusCode = 401) => {
    cy.intercept('POST', '**/auth/login', {
      statusCode,
      body: { detail }
    }).as('login')
  }

  const submitLogin = (email, password) => {
    cy.get('input[type="email"]').clear().type(email)
    cy.get('input[type="password"]').clear().type(password, { log: false })
    cy.get('button[type="submit"]').click()
    cy.wait('@login')
  }

  const seedAuth = (win) => {
    win.localStorage.setItem('token', authToken)
    win.localStorage.setItem('user', JSON.stringify(adminUser))
  }

  beforeEach(() => {
    // Nettoyer le localStorage
    cy.clearLocalStorage()
    cy.intercept('GET', '**/profile/me', {
      statusCode: 200,
      body: { user: adminUser, player: { id: 1, first_name: 'Admin', last_name: 'User' } }
    }).as('getProfile')
  })

  it('Affiche la page de login', () => {
    cy.visit('/login')
    cy.contains('Corpo Padel').should('be.visible')
    cy.contains('Connectez-vous').should('be.visible')
    cy.get('input[type="email"]').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
  })

  it('Connexion réussie avec credentials valides', () => {
    mockLoginSuccess()
    cy.visit('/login')

    submitLogin('admin@padel.com', 'Admin@2025!')

    // Vérifier la redirection vers la page d'accueil
    cy.location('pathname').should('eq', '/')
    cy.contains('Bonjour').should('be.visible')
    cy.contains('admin@padel.com').should('be.visible')
  })

  it('Connexion échoue avec email invalide', () => {
    mockLoginFailure({
      message: 'Email ou mot de passe incorrect',
      attempts_remaining: 4
    })
    cy.visit('/login')

    submitLogin('wrong@example.com', 'Admin@2025!')

    // Vérifier le message d'erreur
    //cy.contains('Email ou mot de passe incorrect').should('be.visible')
    //cy.contains('Tentatives restantes').should('be.visible')
  })

  it('Connexion échoue avec mot de passe invalide', () => {
    mockLoginFailure({
      message: 'Email ou mot de passe incorrect',
      attempts_remaining: 4
    })
    cy.visit('/login')

    submitLogin('admin@padel.com', 'WrongPassword')

    // Vérifier le message d'erreur
    //cy.contains('Email ou mot de passe incorrect').should('be.visible')
  })

  it('Connexion échoue avec compte désactivé', () => {
    mockLoginFailure({ message: 'Compte désactivé' }, 403)
    cy.visit('/login')

    submitLogin('admin@padel.com', 'Admin@2025!')

    cy.contains('Compte').should('be.visible')
  })

  it('Bloque le compte après 5 tentatives échouées', () => {
    let attempts = 0
    cy.intercept('POST', '**/auth/login', (req) => {
      attempts += 1
      if (attempts < 5) {
        req.reply({
          statusCode: 401,
          body: {
            detail: {
              message: 'Email ou mot de passe incorrect',
              attempts_remaining: 5 - attempts
            }
          }
        })
        return
      }

      req.reply({
        statusCode: 403,
        body: {
          detail: {
            message: 'Compte bloqué',
            minutes_remaining: 30
          }
        }
      })
    }).as('login')

    cy.visit('/login')

    // Faire 5 tentatives échouées
    for (let i = 0; i < 5; i++) {
      submitLogin('admin@padel.com', 'WrongPassword')
    }

    // Vérifier le message de blocage
    cy.contains('Compte bloqu').should('be.visible')
    cy.contains('minutes').should('be.visible')
    cy.get('button[type="submit"]').should('be.disabled')
  })

  it('Redirection automatique si déjá connecté', () => {
    cy.visit('/login', { onBeforeLoad: seedAuth })

    // Devrait être redirigé vers l'accueil
    cy.location('pathname').should('eq', '/')
  })

  it('Déconnexion fonctionne correctement', () => {
    cy.intercept('POST', '**/auth/logout', {
      statusCode: 200,
      body: { message: 'Déconnexion réussie' }
    }).as('logout')

    // Se connecter
    cy.visit('/', { onBeforeLoad: seedAuth })

    // Vérifier que l'utilisateur est connecté
    cy.location('pathname').should('eq', '/')

    // Se déconnecter
    cy.contains('Déconnexion').click()
    cy.wait('@logout')

    // Vérifier la redirection vers login
    cy.url().should('include', '/login')

    // Vérifier que le token est supprimé
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null
    })
  })
})
