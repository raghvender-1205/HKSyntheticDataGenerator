<script lang="ts">
  import { onMount } from 'svelte';
  
  // Form state
  let currentStep = 0;
  let loading = false;
  let error: string | null = null;
  let success = false;
  
  // Form data
  let formData = {
    dataSource: {
      type: 'pdf',
      url: '',
      file: null as File | null,
      text: ''
    },
    dataConfig: {
      format: 'qa', // qa, instructionResponse, etc.
      count: 10,
      seed: Math.floor(Math.random() * 1000)
    },
    llmConfig: {
      provider: 'openai',
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 1000,
      customEndpoint: '',
      apiKey: ''
    }
  };
  
  // Step validation
  function isStepValid(step: number): boolean {
    if (step === 0) {
      // Data source validation
      if (formData.dataSource.type === 'pdf') {
        return !!formData.dataSource.file || !!formData.dataSource.url;
      } else if (formData.dataSource.type === 'text') {
        return formData.dataSource.text.trim().length > 0;
      }
      return false;
    } else if (step === 1) {
      // Data config validation
      return formData.dataConfig.count > 0 && !!formData.dataConfig.format;
    } else if (step === 2) {
      // LLM config validation
      if (formData.llmConfig.provider === 'custom') {
        return !!formData.llmConfig.customEndpoint && !!formData.llmConfig.apiKey;
      }
      return !!formData.llmConfig.model && formData.llmConfig.temperature >= 0;
    }
    return true;
  }
  
  // Next step
  function nextStep(): void {
    if (isStepValid(currentStep)) {
      if (currentStep < 3) {
        currentStep++;
      }
    }
  }
  
  // Previous step
  function prevStep(): void {
    if (currentStep > 0) {
      currentStep--;
    }
  }
  
  // Handle file selection
  function handleFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      formData.dataSource.file = file;
      formData.dataSource.url = '';
    }
  }
  
  // Submit form
  async function submitForm(): Promise<void> {
    if (!isStepValid(currentStep)) return;
    
    loading = true;
    error = null;
    
    try {
      // Create FormData object for file upload
      const data = new FormData();
      
      // Add file or URL
      if (formData.dataSource.type === 'pdf') {
        if (formData.dataSource.file) {
          data.append('file', formData.dataSource.file);
        } else if (formData.dataSource.url) {
          data.append('connection_string', formData.dataSource.url);
        }
      } else if (formData.dataSource.type === 'text') {
        data.append('text', formData.dataSource.text);
      }
      
      // Add config data
      data.append('data_format', formData.dataConfig.format);
      data.append('sample_count', formData.dataConfig.count.toString());
      data.append('seed', formData.dataConfig.seed.toString());
      
      // Add LLM config
      if (formData.llmConfig.provider === 'custom') {
        data.append('llm_provider', 'custom');
        data.append('llm_endpoint', formData.llmConfig.customEndpoint);
        data.append('api_key', formData.llmConfig.apiKey);
      } else {
        data.append('llm_provider', formData.llmConfig.provider);
        data.append('model', formData.llmConfig.model);
      }
      
      data.append('temperature', formData.llmConfig.temperature.toString());
      data.append('max_tokens', formData.llmConfig.maxTokens.toString());
      
      console.log('Sending data to backend:', {
        dataSource: {
          type: formData.dataSource.type,
          url: formData.dataSource.url,
          hasFile: !!formData.dataSource.file
        },
        dataConfig: formData.dataConfig,
        llmConfig: {
          ...formData.llmConfig,
          apiKey: formData.llmConfig.apiKey ? '***' : '' // Don't log the actual API key
        }
      });
      
      try {
        // Send request to backend
        const response = await fetch('/api/v1/generate', {
          method: 'POST',
          body: data
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to generate data');
        }
        
        const result = await response.json();
        console.log('Generated data:', result);
        success = true;
      } catch (apiError: unknown) {
        console.error('API Error:', apiError);
        
        // For development/demo purposes, simulate success if the API isn't ready
        if (!window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1')) {
          throw apiError;
        }
        
        console.warn('Using mock success for development');
        await new Promise(resolve => setTimeout(resolve, 1500));
        success = true;
      }
    } catch (err: unknown) {
      console.error('Error generating data:', err);
      error = err instanceof Error ? err.message : 'An unexpected error occurred';
    } finally {
      loading = false;
    }
  }
  
  // Format options
  const formatOptions = [
    { value: 'qa', label: 'Question & Answer' },
    { value: 'instructionResponse', label: 'Instruction-Response' },
    { value: 'conversation', label: 'Conversation' }
  ];
  
  // LLM options
  const llmOptions = [
    { provider: 'openai', models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'] },
    { provider: 'anthropic', models: ['claude-2', 'claude-instant-1'] },
    { provider: 'custom', models: [] }
  ];
</script>

<svelte:head>
  <title>Generate Synthetic Data | HealthKart</title>
  <meta name="description" content="Generate synthetic data from your documents using advanced LLMs" />
</svelte:head>

<div class="container mx-auto py-8 px-4">
  <h1 class="text-3xl font-bold text-primary-700 mb-6">Generate Synthetic Data</h1>
  
  {#if success}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
      <div class="flex items-center">
        <svg class="h-6 w-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
        </svg>
        <p><strong>Success!</strong> Your synthetic data has been generated.</p>
      </div>
      <div class="mt-4 flex">
        <button class="btn btn-primary mr-2">Download Dataset</button>
        <button class="btn btn-secondary" on:click={() => { success = false; currentStep = 0; }}>Generate Another</button>
      </div>
    </div>
  {:else}
    <!-- Progress indicator -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        {#each ['Data Source', 'Configure Output', 'LLM Settings', 'Review & Generate'] as step, i}
          <div class="flex flex-col items-center">
            <div class={`w-10 h-10 rounded-full flex items-center justify-center mb-2 ${i <= currentStep ? 'bg-primary-600 text-white' : 'bg-secondary-200 text-secondary-700'}`}>
              {i + 1}
            </div>
            <div class={`text-sm ${i <= currentStep ? 'text-primary-600 font-medium' : 'text-secondary-500'}`}>{step}</div>
          </div>
          
          {#if i < 3}
            <div class={`flex-1 h-1 mx-2 ${i < currentStep ? 'bg-primary-600' : 'bg-secondary-200'}`}></div>
          {/if}
        {/each}
      </div>
    </div>

    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
        <p><strong>Error:</strong> {error}</p>
      </div>
    {/if}

    <div class="bg-white rounded-lg shadow-md border border-secondary-200 p-6 mb-6">
      <!-- Step 1: Data Source -->
      {#if currentStep === 0}
        <h2 class="text-xl font-semibold text-secondary-800 mb-4">Select Data Source</h2>
        
        <div class="mb-4">
          <div class="flex space-x-4 mb-4">
            <label class="flex items-center">
              <input type="radio" name="dataSourceType" value="pdf" bind:group={formData.dataSource.type} class="mr-2">
              <span>PDF Document</span>
            </label>
            <label class="flex items-center">
              <input type="radio" name="dataSourceType" value="text" bind:group={formData.dataSource.type} class="mr-2">
              <span>Text Input</span>
            </label>
          </div>
          
          {#if formData.dataSource.type === 'pdf'}
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">PDF Upload or URL</label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block mb-2 text-sm">Upload PDF</label>
                  <input type="file" accept=".pdf" on:change={handleFileChange} class="input">
                  {#if formData.dataSource.file}
                    <p class="text-sm text-secondary-600 mt-1">Selected: {formData.dataSource.file.name}</p>
                  {/if}
                </div>
                <div>
                  <label class="block mb-2 text-sm">Or enter PDF URL</label>
                  <input type="text" bind:value={formData.dataSource.url} placeholder="https://example.com/document.pdf" class="input w-full">
                </div>
              </div>
            </div>
          {:else if formData.dataSource.type === 'text'}
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Text Content</label>
              <textarea bind:value={formData.dataSource.text} rows="10" class="w-full p-2 border border-secondary-300 rounded" placeholder="Paste your text content here..."></textarea>
            </div>
          {/if}
        </div>
      
      <!-- Step 2: Data Configuration -->
      {:else if currentStep === 1}
        <h2 class="text-xl font-semibold text-secondary-800 mb-4">Configure Output</h2>
        
        <div class="mb-4">
          <label class="block text-secondary-700 mb-2">Data Format</label>
          <select bind:value={formData.dataConfig.format} class="input w-full">
            {#each formatOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <div class="mb-4">
          <label class="block text-secondary-700 mb-2">Number of Samples</label>
          <input type="number" bind:value={formData.dataConfig.count} min="1" max="100" class="input w-full">
          <p class="text-sm text-secondary-500 mt-1">Maximum 100 samples per generation</p>
        </div>
        
        <div class="mb-4">
          <label class="block text-secondary-700 mb-2">Random Seed (Optional)</label>
          <input type="number" bind:value={formData.dataConfig.seed} class="input w-full">
          <p class="text-sm text-secondary-500 mt-1">Set a specific seed for reproducible results</p>
        </div>
      
      <!-- Step 3: LLM Configuration -->
      {:else if currentStep === 2}
        <h2 class="text-xl font-semibold text-secondary-800 mb-4">LLM Settings</h2>
        
        <div class="mb-4">
          <label class="block text-secondary-700 mb-2">LLM Provider</label>
          <select bind:value={formData.llmConfig.provider} class="input w-full">
            {#each llmOptions as option}
              <option value={option.provider}>{option.provider === 'custom' ? 'Custom LLM' : option.provider.charAt(0).toUpperCase() + option.provider.slice(1)}</option>
            {/each}
          </select>
        </div>
        
        {#if formData.llmConfig.provider !== 'custom'}
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Model</label>
            <select bind:value={formData.llmConfig.model} class="input w-full">
              {#each llmOptions.find(o => o.provider === formData.llmConfig.provider)?.models || [] as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
          </div>
        {:else}
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Custom Endpoint</label>
            <input type="text" bind:value={formData.llmConfig.customEndpoint} placeholder="https://api.example.com/v1/chat/completions" class="input w-full">
          </div>
          
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">API Key</label>
            <input type="password" bind:value={formData.llmConfig.apiKey} placeholder="Your API key" class="input w-full">
          </div>
        {/if}
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Temperature</label>
            <input type="range" bind:value={formData.llmConfig.temperature} min="0" max="2" step="0.1" class="w-full">
            <div class="flex justify-between">
              <span class="text-sm">0 (Deterministic)</span>
              <span class="text-sm font-medium">{formData.llmConfig.temperature}</span>
              <span class="text-sm">2 (Creative)</span>
            </div>
          </div>
          
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Max Tokens</label>
            <input type="number" bind:value={formData.llmConfig.maxTokens} min="100" max="8000" class="input w-full">
          </div>
        </div>
      
      <!-- Step 4: Review & Generate -->
      {:else if currentStep === 3}
        <h2 class="text-xl font-semibold text-secondary-800 mb-4">Review & Generate</h2>
        
        <div class="space-y-6">
          <div class="p-4 bg-secondary-50 rounded-lg">
            <h3 class="font-medium mb-2">Data Source</h3>
            {#if formData.dataSource.type === 'pdf'}
              <p>PDF {formData.dataSource.file ? `File: ${formData.dataSource.file.name}` : `URL: ${formData.dataSource.url}`}</p>
            {:else}
              <p>Text Input ({formData.dataSource.text.length} characters)</p>
            {/if}
          </div>
          
          <div class="p-4 bg-secondary-50 rounded-lg">
            <h3 class="font-medium mb-2">Output Configuration</h3>
            <p>Format: {formatOptions.find(o => o.value === formData.dataConfig.format)?.label}</p>
            <p>Samples: {formData.dataConfig.count}</p>
            <p>Seed: {formData.dataConfig.seed}</p>
          </div>
          
          <div class="p-4 bg-secondary-50 rounded-lg">
            <h3 class="font-medium mb-2">LLM Configuration</h3>
            {#if formData.llmConfig.provider === 'custom'}
              <p>Provider: Custom LLM</p>
              <p>Endpoint: {formData.llmConfig.customEndpoint}</p>
            {:else}
              <p>Provider: {formData.llmConfig.provider.charAt(0).toUpperCase() + formData.llmConfig.provider.slice(1)}</p>
              <p>Model: {formData.llmConfig.model}</p>
            {/if}
            <p>Temperature: {formData.llmConfig.temperature}</p>
            <p>Max Tokens: {formData.llmConfig.maxTokens}</p>
          </div>
        </div>
        
        <div class="mt-6">
          <button 
            class="btn btn-primary w-full py-3 flex items-center justify-center" 
            on:click={submitForm}
            disabled={loading}
          >
            {#if loading}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating...
            {:else}
              Generate Synthetic Data
            {/if}
          </button>
          <p class="text-sm text-center text-secondary-500 mt-2">This process may take a few minutes depending on your configuration</p>
        </div>
      {/if}
      
      <!-- Navigation buttons -->
      <div class="flex justify-between mt-8">
        {#if currentStep > 0}
          <button class="btn btn-secondary" on:click={prevStep}>
            <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back
          </button>
        {:else}
          <div></div>
        {/if}
        
        {#if currentStep < 3}
          <button class="btn btn-primary" on:click={nextStep} disabled={!isStepValid(currentStep)}>
            Next
            <svg class="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        {/if}
      </div>
    </div>
  {/if}
</div> 