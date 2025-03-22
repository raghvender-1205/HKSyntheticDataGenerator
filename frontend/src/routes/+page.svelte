<script lang="ts">
  import { goto } from '$app/navigation';
</script>

<svelte:head>
  <title>HealthKart Synthetic Data Generator</title>
  <meta name="description" content="Generate high-quality synthetic data for various use cases" />
</svelte:head>

<section class="mb-12">
  <div class="max-w-4xl mx-auto py-12">
    <h1 class="text-4xl font-bold tracking-tight text-secondary-900 mb-4 text-center">
      HealthKart Synthetic Data Generator
    </h1>
    <p class="text-xl text-secondary-600 text-center mb-8">
      Generate high-quality synthetic data from your existing content using advanced LLMs
    </p>
    <div class="flex justify-center">
      <button 
        class="btn btn-primary mr-4"
        on:click={() => goto('/generate')}
      >
        Get Started
      </button>
      <a href="/docs" class="btn btn-secondary">
        Learn More
      </a>
    </div>
  </div>
</section>

<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
  <div class="card">
    <div class="h-12 w-12 bg-primary-100 rounded-lg mb-4 flex items-center justify-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>
    <h3 class="text-lg font-medium text-secondary-900 mb-2">PDF Extraction</h3>
    <p class="text-secondary-600">
      Extract structured data from your PDF documents to use as a foundation for synthetic data generation.
    </p>
  </div>

  <div class="card">
    <div class="h-12 w-12 bg-primary-100 rounded-lg mb-4 flex items-center justify-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    </div>
    <h3 class="text-lg font-medium text-secondary-900 mb-2">Custom LLM Integration</h3>
    <p class="text-secondary-600">
      Use your preferred LLM to generate synthetic data, with support for OpenAI, Gemini, and custom LLM endpoints.
    </p>
  </div>

  <div class="card">
    <div class="h-12 w-12 bg-primary-100 rounded-lg mb-4 flex items-center justify-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
      </svg>
    </div>
    <h3 class="text-lg font-medium text-secondary-900 mb-2">Multiple Dataset Types</h3>
    <p class="text-secondary-600">
      Generate various types of datasets including Q&A pairs, instruction-response, classification, and more.
    </p>
  </div>
</div>

<section class="card mb-12">
  <h2 class="text-2xl font-bold text-secondary-900 mb-4">How It Works</h2>
  <div class="flex flex-col md:flex-row items-center justify-between">
    <div class="md:w-1/2 mb-6 md:mb-0 md:pr-6">
      <ol class="list-decimal list-inside space-y-4 text-secondary-700">
        <li>Upload your PDF document or connect to an existing data source</li>
        <li>Choose the type of synthetic data you want to generate (Q&A, instruction-response, etc.)</li>
        <li>Configure your preferred LLM and generation parameters</li>
        <li>Generate your synthetic dataset and download or save the configuration for later</li>
      </ol>
    </div>
    <div class="md:w-1/2 flex justify-center">
      <div class="bg-white p-4 rounded-lg shadow-md border border-secondary-200">
        <div class="flex justify-around items-center">
          <div class="text-center">
            <div class="h-16 w-16 bg-primary-100 rounded-full mb-2 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p class="text-sm font-medium text-secondary-700">Data Source</p>
          </div>
          
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
          
          <div class="text-center">
            <div class="h-16 w-16 bg-primary-100 rounded-full mb-2 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p class="text-sm font-medium text-secondary-700">LLM Processing</p>
          </div>
          
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
          
          <div class="text-center">
            <div class="h-16 w-16 bg-primary-100 rounded-full mb-2 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
              </svg>
            </div>
            <p class="text-sm font-medium text-secondary-700">Synthetic Data</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="mb-12">
  <div class="card">
    <h2 class="text-2xl font-bold text-secondary-900 mb-4">Get Started</h2>
    <p class="text-secondary-700 mb-6">
      Ready to generate your first synthetic dataset? Click the button below to start configuring your generation parameters.
    </p>
    <button 
      class="btn btn-primary"
      on:click={() => goto('/generate')}
    >
      Generate Synthetic Data
    </button>
  </div>
</section>
