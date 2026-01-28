describe('Planning des evenements', () => {
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
    { id: 1, company: 'Alpha' },
    { id: 2, company: 'Bravo' }
  ]

  beforeEach(() => {
    cy.intercept('GET', '**/profile/me', {
      statusCode: 200,
      body: { user: adminUser, player: { id: 1, first_name: 'Admin', last_name: 'User' } }
    }).as('getProfile')
  })

  it('affiche un evenement et ses details', () => {
    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    const event = {
      id: 100,
      event_date: dateStr,
      event_time: '09:00:00',
      matches: [
        {
          id: 200,
          court_number: 1,
          status: 'A_VENIR',
          team1: { id: 1, company: 'Alpha' },
          team2: { id: 2, company: 'Bravo' }
        }
      ]
    }

    cy.intercept('GET', '**/events*', { statusCode: 200, body: [event] }).as('getEvents')
    cy.intercept('GET', '**/teams', { statusCode: 200, body: teams }).as('getTeams')

    cy.visit('/planning', { onBeforeLoad: seedAuth })
    cy.wait('@getEvents')

    cy.contains('09:00').should('be.visible')
    cy.contains('09:00').click()
    cy.contains('Piste 1').should('be.visible')
    cy.contains('Alpha').should('be.visible')
    cy.contains('Bravo').should('be.visible')
  })

  it('cree un evenement avec un match', () => {
    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    let events = []

    cy.intercept('GET', '**/events*', (req) => {
      req.reply({ statusCode: 200, body: events })
    }).as('getEvents')
    cy.intercept('GET', '**/teams', { statusCode: 200, body: teams }).as('getTeams')
    cy.intercept('POST', '**/events', (req) => {
      const newEvent = {
        id: 101,
        event_date: req.body.event_date,
        event_time: req.body.event_time,
        matches: req.body.matches.map((match, index) => ({
          id: 300 + index,
          court_number: match.court_number,
          status: 'A_VENIR',
          team1: { id: match.team1_id, company: 'Alpha' },
          team2: { id: match.team2_id, company: 'Bravo' }
        }))
      }
      events = [newEvent]
      req.reply({ statusCode: 201, body: newEvent })
    }).as('createEvent')

    cy.visit('/planning', { onBeforeLoad: seedAuth })
    cy.wait('@getEvents')

    cy.contains('Nouvel').click()
    cy.get('form').within(() => {
      cy.get('input[type="date"]').type(dateStr)
      cy.get('input[type="time"]').clear().type('09:30')
      cy.get('select').eq(0).select('1')
      cy.get('select').eq(1).select('1')
      cy.get('select').eq(2).select('1')
      cy.get('select').eq(3).select('2')
      cy.get('button[type="submit"]').click()
    })

    cy.wait('@createEvent')
    cy.wait('@getEvents')
    cy.contains('09:30').should('be.visible')
  })
})
