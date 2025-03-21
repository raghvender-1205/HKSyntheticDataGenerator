<script lang="ts">
  import { onMount } from 'svelte';
  import ProgressBar from '../components/ProgressBar.svelte';
  import DataSourceSelector from '../components/DataSourceSelector.svelte';
  import LLMSelector from '../components/LLMSelector.svelte';
  import DatasetGeneratorSelector from '../components/DatasetGeneratorSelector.svelte';
  import { workflowStep, activeDataSource, activeLlm, activeGenerator, documents, workflowProgress } from '../stores';
  
  // Step components
  const steps = [
    { id: 1, component: DataSourceSelector },
    { id: 2, component: LLMSelector },
    { id: 3, component: DatasetGeneratorSelector },
    // { id: 4, component: DatasetGenerator }, - to be implemented
    // { id: 5, component: DatasetPreview }, - to be implemented
  ];
  
  // Helper functions
  function goToStep(step: number) {
    if (canGoToStep(step)) {
      workflowStep.set(step);
    }
  }
  
  function canGoToStep(step: number): boolean {
    if (step === 1) return true;
    if (step === 2) return $activeDataSource !== null && $documents.length > 0;
    if (step === 3) return $activeLlm !== null;
    if (step === 4) return $activeGenerator !== null;
    if (step === 5) return false; // Depends on dataset being generated
    return false;
  }
  
  onMount(() => {
    // Reset workflow progress when the page loads
    workflowProgress.set({ step: 1, completed: false });
  });
  
  function nextStep() {
    workflowProgress.update(wp => {
      const nextStep = wp.step + 1;
      const completed = nextStep > 5;
      return { step: completed ? 5 : nextStep, completed };
    });
  }
  
  function previousStep() {
    workflowProgress.update(wp => {
      const prevStep = wp.step - 1;
      return { step: prevStep < 1 ? 1 : prevStep, completed: false };
    });
  }

  const sampleJson = `[
  {
    "instruction": "Explain the concept of gravitational waves in simple terms.",
    "response": "Gravitational waves are like ripples in space and time. Imagine space as a stretched rubber sheet. When heavy objects like black holes move on this sheet, they create waves that travel outward, similar to how dropping a stone in water creates ripples. These waves were predicted by Einstein's theory of relativity and were first directly detected in 2015."
  },
  {
    "instruction": "Provide a brief overview of quantum computing.",
    "response": "Quantum computing uses the principles of quantum mechanics to process information. While traditional computers use bits (0s and 1s), quantum computers use quantum bits or 'qubits' that can exist in multiple states simultaneously. This allows quantum computers to solve certain complex problems much faster than regular computers. They're especially promising for cryptography, optimization, and simulating quantum systems."
  }
]`;
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <section>
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Generate Synthetic Dataset</h1>
    <p class="text-xl text-gray-600 mb-6">Configure your workflow and generate data</p>
    
    <ProgressBar />
    
    <div class="bg-white shadow-md rounded-lg p-6 mb-8">
      {#if $workflowProgress.step === 1}
        <div>
          <h2 class="text-2xl font-semibold mb-4">Step 1: Select Data Source</h2>
          <p class="text-gray-600 mb-4">Choose a data source for generating synthetic data.</p>
          
          <div class="flex justify-center mt-8">
            <button 
              class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              on:click={nextStep}
            >
              Continue to LLM Selection
            </button>
          </div>
        </div>
      {:else if $workflowProgress.step === 2}
        <div>
          <h2 class="text-2xl font-semibold mb-4">Step 2: Select LLM Provider</h2>
          <p class="text-gray-600 mb-4">Choose an LLM provider to generate content.</p>
          
          <div class="flex justify-between mt-8">
            <button 
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              on:click={previousStep}
            >
              Back
            </button>
            <button 
              class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              on:click={nextStep}
            >
              Continue to Generator
            </button>
          </div>
        </div>
      {:else if $workflowProgress.step === 3}
        <div>
          <h2 class="text-2xl font-semibold mb-4">Step 3: Configure Generator</h2>
          <p class="text-gray-600 mb-4">Select and configure your dataset generator.</p>
          
          <div class="flex justify-between mt-8">
            <button 
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              on:click={previousStep}
            >
              Back
            </button>
            <button 
              class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              on:click={nextStep}
            >
              Generate Dataset
            </button>
          </div>
        </div>
      {:else if $workflowProgress.step === 4}
        <div>
          <h2 class="text-2xl font-semibold mb-4">Step 4: Generating Dataset</h2>
          <p class="text-gray-600 mb-4">Your dataset is being generated. This might take a few minutes.</p>
          
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-6">
            <div class="bg-blue-600 h-2.5 rounded-full w-3/4 animate-pulse"></div>
          </div>
          
          <div class="text-center text-gray-500 italic mt-4">
            Estimated time remaining: ~2 minutes
          </div>
          
          <div class="flex justify-between mt-8">
            <button 
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 opacity-50 cursor-not-allowed"
              disabled
            >
              Back
            </button>
            <button 
              class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              on:click={nextStep}
            >
              Preview Results
            </button>
          </div>
        </div>
      {:else if $workflowProgress.step === 5}
        <div>
          <h2 class="text-2xl font-semibold mb-4">Step 5: Preview & Download</h2>
          <p class="text-gray-600 mb-4">Your dataset has been generated successfully!</p>
          
          <div class="bg-gray-100 p-4 rounded-md mb-6 h-64 overflow-y-auto">
            <pre class="text-gray-700 text-sm">{sampleJson}</pre>
          </div>
          
          <div class="flex justify-between">
            <div class="text-gray-600">
              <p><span class="font-semibold">Total entries:</span> 250</p>
              <p><span class="font-semibold">Format:</span> JSONL</p>
              <p><span class="font-semibold">File size:</span> 1.2 MB</p>
            </div>
            
            <div class="flex flex-col gap-2">
              <button class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 inline-flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Dataset
              </button>
              <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 inline-flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Start New Generation
              </button>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </section>
</div> 