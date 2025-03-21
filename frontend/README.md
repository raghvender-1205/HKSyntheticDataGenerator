# Synthetic Data Generator Frontend

A Svelte-based frontend for the Synthetic Data Generator application.

## Features

- Modern UI built with Svelte and TypeScript
- Responsive design using Bulma CSS framework
- Interactive workflow for generating synthetic datasets
- Support for multiple LLM providers
- Easy to use interface for configuring data sources and generators

## Development

### Prerequisites

- Node.js 14+ and npm

### Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser at http://localhost:5173

### Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

- `src/components/`: Reusable UI components
- `src/pages/`: Individual page components
- `src/services/`: API services for backend communication
- `src/stores/`: Svelte stores for state management
- `src/types/`: TypeScript type definitions

## Technologies Used

- Svelte
- TypeScript
- Bulma CSS
- Svelte Routing
- Axios for API calls
