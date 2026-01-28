describe('Profil', () => {
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

  it('charge et met a jour le profil', () => {
    let profile = {
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

    cy.intercept('GET', '**/api/v1/profile/me', (req) => {
      req.reply({ statusCode: 200, body: profile })
    }).as('getProfile')
    cy.intercept('PUT', '**/api/v1/profile/me', (req) => {
      profile = {
        ...profile,
        user: { ...profile.user, email: req.body.email },
        player: { ...profile.player, first_name: req.body.first_name, last_name: req.body.last_name }
      }
      req.reply({ statusCode: 200, body: profile })
    }).as('updateProfile')

    cy.visit('/profile', { onBeforeLoad: seedAuth })
    cy.wait('@getProfile')

    cy.get('input[type="text"]').first().clear().type('Pierre')
    cy.get('input[type="text"]').eq(1).clear().type('Martin')
    cy.get('input[type="email"]').clear().type('updated@example.com')
    cy.contains('Enregistrer les modifications').click()

    cy.wait('@updateProfile')
    cy.wait('@getProfile')
    cy.contains('Profil mis').should('be.visible')
  })

  it('affiche un message d erreur sur changement de mot de passe invalide', () => {
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

    cy.intercept('GET', '**/api/v1/profile/me', { statusCode: 200, body: profile }).as('getProfile')
    cy.intercept('POST', '**/api/v1/profile/me/change-password', {
      statusCode: 422,
      body: { detail: [{ loc: ['body', 'new_password'], msg: 'invalid' }] }
    }).as('changePassword')

    cy.visit('/profile', { onBeforeLoad: seedAuth })
    cy.wait('@getProfile')

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
