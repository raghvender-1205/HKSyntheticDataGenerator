<script lang="ts">
  import { Link } from 'svelte-routing';
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <section class="text-center">
    <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">Synthetic Data Generator</h1>
    <p class="text-2xl text-gray-600 mb-8">Generate high-quality synthetic data for LLM training</p>
    
    <div class="max-w-3xl mx-auto text-lg text-gray-600 mb-12">
      <p class="mb-6">
        This application helps you create custom synthetic datasets for training and fine-tuning large language models.
        With a plugin-based architecture, you can easily use different data sources and LLM providers.
      </p>

      <div class="bg-white shadow rounded-lg p-8 mb-8">
        <h3 class="text-xl font-semibold mb-4">Features</h3>
        <ul class="space-y-4 text-left">
          <li class="flex items-start">
            <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Import data from various sources (files, APIs, databases)</span>
          </li>
          <li class="flex items-start">
            <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Generate synthetic QA pairs and instruction tuning datasets</span>
          </li>
          <li class="flex items-start">
            <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Support for multiple LLM providers (OpenAI, Ollama, Groq, Google Gemini)</span>
          </li>
          <li class="flex items-start">
            <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Customizable dataset formats</span>
          </li>
          <li class="flex items-start">
            <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Export to JSONL and other formats</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
      <div class="bg-white shadow rounded-lg p-6 flex flex-col items-center">
        <div class="bg-blue-100 p-3 rounded-full mb-4">
          <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold mb-2">1. Configure Data Source</h3>
        <p class="text-gray-600 mb-4 text-center">Select from various data sources including files, APIs and databases</p>
        <Link to="/datasources" class="mt-auto text-blue-600 hover:text-blue-800 font-medium">
          Browse Data Sources →
        </Link>
      </div>
      
      <div class="bg-white shadow rounded-lg p-6 flex flex-col items-center">
        <div class="bg-purple-100 p-3 rounded-full mb-4">
          <svg class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold mb-2">2. Select LLM Provider</h3>
        <p class="text-gray-600 mb-4 text-center">Choose from supported LLM providers like OpenAI, Ollama, Groq and more</p>
        <Link to="/llms" class="mt-auto text-purple-600 hover:text-purple-800 font-medium">
          View LLM Providers →
        </Link>
      </div>
      
      <div class="bg-white shadow rounded-lg p-6 flex flex-col items-center">
        <div class="bg-green-100 p-3 rounded-full mb-4">
          <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold mb-2">3. Configure Generator</h3>
        <p class="text-gray-600 mb-4 text-center">Select generator type and customize parameters for your dataset</p>
        <Link to="/generators" class="mt-auto text-green-600 hover:text-green-800 font-medium">
          Explore Generators →
        </Link>
      </div>
    </div>

    <div class="flex flex-col sm:flex-row justify-center gap-4">
      <Link to="/workflow" class="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 shadow-sm">
        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Start Generating Data
      </Link>
      
      <a href="https://github.com/your-org/synthetic-data-generator" target="_blank" rel="noopener" class="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 shadow-sm">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
        </svg>
        View on GitHub
      </a>
    </div>
  </section>
</div> 