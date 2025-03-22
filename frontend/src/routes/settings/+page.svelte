<script lang="ts">
  import { onMount } from 'svelte';
  
  // Form data
  let settings = {
    openai_api_key: '',
    gemini_api_key: '',
    custom_api_key: '',
    custom_api_base_url: 'http://localhost:8000/v1',
    custom_model_name: 'custom-model',
    default_llm_provider: 'openai',
    default_model: 'gpt-4',
    default_temperature: 0.7,
    default_max_tokens: 1000,
    save_configurations: true
  };
  
  // Form state
  let loading = false;
  let error: string | null = null;
  let success = false;
  let activeTab = 'api_keys';
  
  // LLM options
  const llmOptions = [
    { provider: 'openai', models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'] },
    { provider: 'gemini', models: ['gemini-pro', 'gemini-1.5-pro'] },
    { provider: 'custom', models: ['custom-model'] }
  ];
  
  onMount(async () => {
    await fetchSettings();
  });
  
  // Fetch settings
  async function fetchSettings(): Promise<void> {
    loading = true;
    error = null;
    
    try {
      // Try to fetch from the backend API
      try {
        const response = await fetch('/api/v1/config/settings');
        
        if (response.ok) {
          const data = await response.json();
          settings = { ...settings, ...data };
          return;
        }
      } catch (apiError: unknown) {
        console.warn('API not available, falling back to local storage:', apiError);
      }
      
      // Fall back to local storage if API fails
      const savedSettings = localStorage.getItem('hk_settings');
      if (savedSettings) {
        settings = JSON.parse(savedSettings);
      }
    } catch (err: unknown) {
      console.error('Error fetching settings:', err);
      error = err instanceof Error ? err.message : 'An unexpected error occurred';
    } finally {
      loading = false;
    }
  }
  
  // Save settings
  async function saveSettings(): Promise<void> {
    loading = true;
    error = null;
    success = false;
    
    try {
      // First try to save to the backend
      let apiSuccess = false;
      
      try {
        const response = await fetch('/api/v1/config/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        });
        
        if (response.ok) {
          apiSuccess = true;
        }
      } catch (apiError: unknown) {
        console.warn('API not available, falling back to local storage:', apiError);
      }
      
      // If API failed, save to local storage as fallback
      if (!apiSuccess) {
        localStorage.setItem('hk_settings', JSON.stringify(settings));
      }
      
      success = true;
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        success = false;
      }, 3000);
    } catch (err: unknown) {
      console.error('Error saving settings:', err);
      error = err instanceof Error ? err.message : 'An unexpected error occurred';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Settings | HealthKart</title>
  <meta name="description" content="Configure your synthetic data generation settings" />
</svelte:head>

<div class="container mx-auto py-8 px-4">
  <h1 class="text-3xl font-bold text-primary-700 mb-6">Settings</h1>
  
  {#if success}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex items-center">
      <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
      </svg>
      <p>Settings saved successfully</p>
    </div>
  {/if}
  
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
      <p><strong>Error:</strong> {error}</p>
    </div>
  {/if}
  
  <div class="bg-white rounded-lg shadow-md border border-secondary-200 overflow-hidden">
    <!-- Settings tabs -->
    <div class="border-b border-secondary-200">
      <nav class="flex -mb-px">
        <button 
          class={`py-4 px-6 font-medium text-sm border-b-2 ${activeTab === 'api_keys' ? 'border-primary-500 text-primary-600' : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'}`}
          on:click={() => activeTab = 'api_keys'}
        >
          API Keys
        </button>
        <button 
          class={`py-4 px-6 font-medium text-sm border-b-2 ${activeTab === 'defaults' ? 'border-primary-500 text-primary-600' : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'}`}
          on:click={() => activeTab = 'defaults'}
        >
          Default Settings
        </button>
      </nav>
    </div>
    
    <div class="p-6">
      <!-- API Keys tab -->
      {#if activeTab === 'api_keys'}
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-secondary-800 mb-4">API Keys</h2>
          <p class="text-secondary-600 mb-6">
            Configure your API keys for different LLM providers. These keys will be used to make requests to the respective services.
          </p>
          
          <div class="space-y-6">
            <div>
              <label for="openai_api_key" class="block text-secondary-700 mb-2">OpenAI API Key</label>
              <input 
                type="password" 
                id="openai_api_key" 
                bind:value={settings.openai_api_key} 
                placeholder="sk-..." 
                class="input w-full"
              />
              <p class="text-sm text-secondary-500 mt-1">
                Used for GPT-3.5 and GPT-4 models. Get your API key from the <a href="https://platform.openai.com/account/api-keys" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">OpenAI dashboard</a>.
              </p>
            </div>
            
            <div>
              <label for="gemini_api_key" class="block text-secondary-700 mb-2">Google Gemini API Key</label>
              <input 
                type="password" 
                id="gemini_api_key" 
                bind:value={settings.gemini_api_key} 
                placeholder="AIza..." 
                class="input w-full"
              />
              <p class="text-sm text-secondary-500 mt-1">
                Used for Gemini models. Get your API key from the <a href="https://ai.google.dev/" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">Google AI Studio</a>.
              </p>
            </div>
            
            <!-- Custom LLM Configuration -->
            <div class="mt-8 border-t pt-6">
              <h3 class="text-lg font-semibold text-secondary-800 mb-4">Custom LLM Configuration</h3>
              <p class="text-secondary-600 mb-4">
                Configure your custom LLM endpoint settings. These will be used when selecting the "Custom" provider.
              </p>
              
              <div class="space-y-4">
                <div>
                  <label for="custom_api_base_url" class="block text-secondary-700 mb-2">API Base URL</label>
                  <input 
                    type="text" 
                    id="custom_api_base_url" 
                    bind:value={settings.custom_api_base_url} 
                    placeholder="http://localhost:8000/v1" 
                    class="input w-full"
                  />
                  <p class="text-sm text-secondary-500 mt-1">
                    The base URL for your custom LLM API (e.g., vLLM, llama.cpp, local server).
                  </p>
                </div>
                
                <div>
                  <label for="custom_api_key" class="block text-secondary-700 mb-2">Custom API Key (Optional)</label>
                  <input 
                    type="password" 
                    id="custom_api_key" 
                    bind:value={settings.custom_api_key} 
                    placeholder="Your API key" 
                    class="input w-full"
                  />
                  <p class="text-sm text-secondary-500 mt-1">
                    Optional API key for your custom LLM service, if required.
                  </p>
                </div>
                
                <div>
                  <label for="custom_model_name" class="block text-secondary-700 mb-2">Model Name</label>
                  <input 
                    type="text" 
                    id="custom_model_name" 
                    bind:value={settings.custom_model_name} 
                    placeholder="custom-model" 
                    class="input w-full"
                  />
                  <p class="text-sm text-secondary-500 mt-1">
                    The name of the model to use with your custom LLM provider.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      
      <!-- Default Settings tab -->
      {:else if activeTab === 'defaults'}
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-secondary-800 mb-4">Default Settings</h2>
          <p class="text-secondary-600 mb-6">
            Configure default settings for data generation. These will be pre-filled when creating new configurations.
          </p>
          
          <div class="space-y-6">
            <div>
              <label for="default_llm_provider" class="block text-secondary-700 mb-2">Default LLM Provider</label>
              <select 
                id="default_llm_provider" 
                bind:value={settings.default_llm_provider} 
                class="input w-full"
                on:change={() => {
                  if (settings.default_llm_provider) {
                    const provider = llmOptions.find(p => p.provider === settings.default_llm_provider);
                    if (provider && provider.models.length > 0) {
                      settings.default_model = provider.models[0];
                    }
                  }
                }}
              >
                {#each llmOptions as option}
                  <option value={option.provider}>{option.provider.charAt(0).toUpperCase() + option.provider.slice(1)}</option>
                {/each}
              </select>
            </div>
            
            <div>
              <label for="default_model" class="block text-secondary-700 mb-2">Default Model</label>
              <select 
                id="default_model" 
                bind:value={settings.default_model} 
                class="input w-full"
              >
                {#each llmOptions.find(o => o.provider === settings.default_llm_provider)?.models || [] as model}
                  <option value={model}>{model}</option>
                {/each}
              </select>
            </div>
            
            <!-- Custom LLM Configuration fields (shown only when custom provider is selected) -->
            {#if settings.default_llm_provider === 'custom'}
              <div class="mt-6 pt-6 border-t border-secondary-200">
                <h3 class="text-lg font-semibold text-secondary-800 mb-4">Custom LLM Configuration</h3>
                
                <div class="space-y-4">
                  <div>
                    <label for="default_custom_api_base_url" class="block text-secondary-700 mb-2">API Base URL</label>
                    <input 
                      type="text" 
                      id="default_custom_api_base_url" 
                      bind:value={settings.custom_api_base_url} 
                      placeholder="http://localhost:8000/v1" 
                      class="input w-full"
                    />
                  </div>
                  
                  <div>
                    <label for="default_custom_model_name" class="block text-secondary-700 mb-2">Model Name</label>
                    <input 
                      type="text" 
                      id="default_custom_model_name" 
                      bind:value={settings.custom_model_name} 
                      placeholder="custom-model" 
                      class="input w-full"
                    />
                  </div>
                  
                  <div>
                    <label for="default_custom_api_key" class="block text-secondary-700 mb-2">API Key (Optional)</label>
                    <input 
                      type="password" 
                      id="default_custom_api_key" 
                      bind:value={settings.custom_api_key} 
                      placeholder="Your API key" 
                      class="input w-full"
                    />
                  </div>
                </div>
              </div>
            {/if}
            
            <div>
              <label for="default_temperature" class="block text-secondary-700 mb-2">Default Temperature</label>
              <input 
                type="range" 
                id="default_temperature" 
                bind:value={settings.default_temperature} 
                min="0" 
                max="2" 
                step="0.1" 
                class="w-full"
              />
              <div class="flex justify-between">
                <span class="text-sm">0 (Deterministic)</span>
                <span class="text-sm font-medium">{settings.default_temperature}</span>
                <span class="text-sm">2 (Creative)</span>
              </div>
            </div>
            
            <div>
              <label for="default_max_tokens" class="block text-secondary-700 mb-2">Default Max Tokens</label>
              <input 
                type="number" 
                id="default_max_tokens" 
                bind:value={settings.default_max_tokens} 
                min="100" 
                max="8000" 
                class="input w-full"
              />
              <p class="text-sm text-secondary-500 mt-1">
                Maximum number of tokens to generate in the response.
              </p>
            </div>
            
            <div>
              <label class="flex items-center">
                <input 
                  type="checkbox" 
                  bind:checked={settings.save_configurations} 
                  class="mr-2"
                />
                <span>Automatically save configurations after generation</span>
              </label>
              <p class="text-sm text-secondary-500 mt-1 ml-6">
                When enabled, all successful generation configurations will be saved for future use.
              </p>
            </div>
          </div>
        </div>
      {/if}
      
      <div class="mt-8 flex justify-end">
        <button 
          class="btn btn-primary px-6" 
          on:click={saveSettings}
          disabled={loading}
        >
          {#if loading}
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Saving...
          {:else}
            Save Settings
          {/if}
        </button>
      </div>
    </div>
  </div>
</div> 