# Frontend - Corpo Padel

Frontend VueJS 3 avec Vue Router, Pinia et TailwindCSS.

## Installation

```bash
npm install
```

## Configuration

```bash
cp .env.example .env
```

## Lancement

```bash
npm run dev
```

Application : http://localhost:5173

## Build production

```bash
npm run build
npm run preview
```

## Tests E2E

```bash
# Mode interactif
npx cypress open

# Mode headless
npx cypress run
```

## Structure

- `src/components/` : Composants réutilisables
- `src/views/` : Pages de l'application
- `src/router/` : Configuration du routing
- `src/stores/` : Stores Pinia
- `src/services/` : Services API
