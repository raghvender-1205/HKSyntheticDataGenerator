<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { writable } from 'svelte/store';
  import Spinner from '$lib/components/Spinner.svelte';
  import { ToastManager } from '$lib/components/ToastManager.js';
  
  // Form state
  let currentStep = 0;
  let loading = false;
  let error: string | null = null;
  let success = false;
  let generatedData: any = null;  // Store the generated data
  let progress = 0;
  let totalBatches = 0;
  let currentBatch = 0;
  let batchProgress = 0;
  let estimatedTimeRemaining = '';
  let startTime: number | null = null;
  
  // Settings
  let settings = {
    openai_api_key: '',
    gemini_api_key: '',
    groq_api_key: '',
    custom_api_key: '',
    custom_api_base_url: 'http://localhost:8000/v1',
    custom_model_name: 'custom-model',
    default_llm_provider: 'openai',
    default_model: 'gpt-4',
    default_temperature: 0.7,
    default_max_tokens: 1000,
    save_configurations: true
  };
  
  // Form data
  interface DataSource {
    type: string;
    url: string;
    file: File | null;
    text: string;
    jsonData: any;
    source_path: string;
    source: 'pdf' | 'json';
    name: string;
    preview: string;
  }

  interface FormData {
    dataSource: DataSource;
    dataConfig: {
      format: string;
      count: number;
      seed: number;
    };
    llmConfig: {
      provider: string;
      model: string;
      temperature: number;
      maxTokens: number;
      customEndpoint: string;
      apiKey: string;
      modelName: string;
      topP: number | undefined;
      topK: number | undefined;
      apiBase: string | undefined;
    };
    name: string;
    prompt: string;
    includeSource: boolean;
    count: number;
    downloadFormat: string;
  }

  let formData: FormData = {
    dataSource: {
      type: 'file',
      url: '',
      file: null,
      text: '',
      jsonData: '',
      source_path: '',
      source: 'pdf',
      name: '',
      preview: ''
    },
    dataConfig: {
      format: 'qa',
      count: 10,
      seed: Math.floor(Math.random() * 1000)
    },
    llmConfig: {
      provider: 'openai',
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 1000,
      customEndpoint: '',
      apiKey: '',
      modelName: 'custom-model',
      topP: undefined,
      topK: undefined,
      apiBase: undefined
    },
    name: '',
    prompt: '',
    includeSource: true,
    count: 10,
    downloadFormat: 'json'
  };
  
  // File upload state
  let selectedFile: File | null = null;
  let isFileUploading = false;
  let uploadProgress = 0;
  let pdfFileName = '';
  
  let progressInterval: number | null = null;
  
  onMount(async () => {
    // Load settings
    await loadSettings();
    
    // Apply settings to form data
    formData.llmConfig.provider = settings.default_llm_provider;
    formData.llmConfig.model = settings.default_model;
    formData.llmConfig.temperature = settings.default_temperature;
    formData.llmConfig.maxTokens = settings.default_max_tokens;
    
    // Set custom LLM fields if provider is custom
    if (settings.default_llm_provider === 'custom') {
      formData.llmConfig.customEndpoint = settings.custom_api_base_url;
      formData.llmConfig.apiKey = settings.custom_api_key;
      formData.llmConfig.modelName = settings.custom_model_name;
    }
  });
  
  // Load settings from backend or local storage
  async function loadSettings() {
    try {
      // Try to fetch from the backend API
      try {
        const response = await fetch('/api/v1/config/settings');
        
        if (response.ok) {
          const data = await response.json();
          settings = { ...settings, ...data };
          return;
        }
      } catch (apiError) {
        console.warn('API not available, falling back to local storage:', apiError);
      }
      
      // Fall back to local storage if API fails
      const savedSettings = localStorage.getItem('hk_settings');
      if (savedSettings) {
        settings = JSON.parse(savedSettings);
      }
    } catch (err) {
      console.error('Error loading settings:', err);
    }
  }
  
  // Save settings to backend or local storage
  async function saveSettings() {
    try {
      // Try to save to the backend API
      try {
        const response = await fetch('/api/v1/config/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            openai_api_key: settings.openai_api_key,
            gemini_api_key: settings.gemini_api_key,
            groq_api_key: settings.groq_api_key,
            custom_api_key: settings.custom_api_key,
            custom_api_base_url: settings.custom_api_base_url,
            custom_model_name: settings.custom_model_name,
            default_llm_provider: settings.default_llm_provider,
            default_model: settings.default_model,
            default_temperature: settings.default_temperature,
            default_max_tokens: settings.default_max_tokens,
            save_configurations: settings.save_configurations
          })
        });

        if (response.ok) {
          ToastManager.show('Settings saved successfully', 'success');
          return;
        }
      } catch (apiError) {
        console.warn('API not available, falling back to local storage:', apiError);
      }

      // Fall back to local storage if API fails
      localStorage.setItem('hk_settings', JSON.stringify(settings));
      ToastManager.show('Settings saved to local storage', 'success');
    } catch (err) {
      console.error('Error saving settings:', err);
      ToastManager.show('Failed to save settings', 'error');
    }
  }

  // Watch for settings changes and save them
  $: {
    if (settings.openai_api_key || settings.gemini_api_key || settings.groq_api_key || settings.custom_api_key) {
      saveSettings();
    }
  }
  
  // Step validation
  function isStepValid(step: number): boolean {
    if (step === 0) {
      // Data source validation
      if (formData.dataSource.type === 'pdf') {
        return !!formData.dataSource.file || !!formData.dataSource.url;
      } else if (formData.dataSource.type === 'json') {
        return !!formData.dataSource.file && !!formData.dataSource.jsonData;
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
        return !!formData.llmConfig.customEndpoint && !!formData.llmConfig.modelName;
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
  
  async function handleFileSelect(event: Event): Promise<void> {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    
    if (!file) return;

    formData.dataSource.file = file;
    formData.dataSource.source = file.type === 'application/json' ? 'json' : 'pdf';
    formData.dataSource.name = file.name;

    try {
        if (file.type === 'application/json') {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const jsonData = JSON.parse(e.target?.result as string);
                    formData.dataSource.jsonData = jsonData;
                    // Format the JSON data for preview
                    formData.dataSource.preview = JSON.stringify(jsonData, null, 2);
                } catch (error) {
                    console.error('Error parsing JSON:', error);
                    formData.dataSource.preview = 'Invalid JSON file';
                }
            };
            reader.readAsText(file);

            // Upload JSON file
            const formDataToSend = new FormData();
            formDataToSend.append('file', file);
            formDataToSend.append('datasource_name', file.name);

            const response = await fetch('http://localhost:8000/api/v1/upload/json', {
                method: 'POST',
                body: formDataToSend
            });

            if (!response.ok) {
                throw new Error('Failed to upload JSON file');
            }

            const result = await response.json();
            console.log('JSON upload result:', result);
        } else {
            // Upload PDF file
            const formDataToSend = new FormData();
            formDataToSend.append('file', file);
            formDataToSend.append('datasource_name', file.name);

            const response = await fetch('http://localhost:8000/api/v1/upload/pdf', {
                method: 'POST',
                body: formDataToSend
            });

            if (!response.ok) {
                throw new Error('Failed to upload PDF file');
            }

            const result = await response.json();
            console.log('PDF upload result:', result);
        }
    } catch (error) {
        console.error('Error handling file:', error);
        formData.dataSource.preview = `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
  
  async function generateWithUpload(): Promise<void> {
    if (!selectedFile) {
      ToastManager.show('Please select a file to upload', 'error');
      return;
    }
    
    if (!formData.name || !formData.prompt) {
      ToastManager.show('Please fill in all required fields', 'error');
      return;
    }
    
    loading = true;
    error = null;
    
    try {
      const formDataObj = new FormData();
      formDataObj.append('file', selectedFile);
      
      // Create the payload with all the necessary data
      const payload = {
        dataset_type: formData.dataConfig.format,
        sample_size: parseInt(formData.dataConfig.count.toString()),
        data_source_config: {
          type: formData.dataSource.type,
          source_path: "data/uploads",
          connection_string: "",
          parameters: {
            extract_metadata: "true",
            extract_layout: "true"
          },
          ...(formData.dataSource.type === 'json' && { json_data: formData.dataSource.jsonData })
        },
        llm_config: formData.llmConfig,
        save_result: true,
        save_name: formData.name || `Generation ${new Date().toISOString()}`
      };
      
      formDataObj.append('payload', JSON.stringify(payload));
      
      const response = await fetch('/api/v1/generate/upload', {
        method: 'POST',
        body: formDataObj
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }
      
      const result = await response.json();
      console.log('Generated data:', result);
      success = true;
      generatedData = result.data;  // Store the generated data
      
      if (result.data && result.data.length > 0) {
        ToastManager.show('Data generated successfully', 'success');
      } else {
        ToastManager.show('Generation completed but no data was returned', 'warning');
      }
      
    } catch (error) {
      console.error('Generation error:', error);
      ToastManager.show(`Failed to generate data: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      loading = false;
    }
  }
  
  // Function to submit the form
  async function submitForm(): Promise<void> {
    if (!isStepValid(currentStep)) return;
    
    loading = true;
    error = null;
    
    try {
      // Prepare data source config
      let dataSourceConfig: any = {
        type: formData.dataSource.type,
        source_path: "data/uploads",  // Always set this at the top level
        connection_string: "",         // Required field
        parameters: {
          extract_metadata: "true",
          extract_layout: "true"
        }
      };
      
      if (formData.dataSource.type === 'text') {
        dataSourceConfig.text = formData.dataSource.text;
      } else if (formData.dataSource.type === 'json') {
        dataSourceConfig.json_data = formData.dataSource.jsonData;
      }
      
      // Prepare LLM config
      const llmConfig: any = {
        type: formData.llmConfig.provider,
        model_name: formData.llmConfig.provider !== 'custom' ? formData.llmConfig.model : formData.llmConfig.modelName,
        api_key: '',  // Will be set below
        parameters: {
          temperature: formData.llmConfig.temperature,
          max_tokens: formData.llmConfig.maxTokens
        }
      };
      
      // Add provider-specific parameters
      if (formData.llmConfig.provider === 'gemini') {
        if (formData.llmConfig.topP !== undefined) {
          llmConfig.parameters.top_p = formData.llmConfig.topP;
        }
        if (formData.llmConfig.topK !== undefined) {
          llmConfig.parameters.top_k = formData.llmConfig.topK;
        }
      } else if (formData.llmConfig.provider === 'groq') {
        if (formData.llmConfig.topP !== undefined) {
          llmConfig.parameters.top_p = formData.llmConfig.topP;
        }
      }
      
      // Add API key based on provider
      if (formData.llmConfig.provider === 'openai') {
        llmConfig.api_key = settings.openai_api_key;
      } else if (formData.llmConfig.provider === 'gemini') {
        llmConfig.api_key = settings.gemini_api_key;
      } else if (formData.llmConfig.provider === 'groq') {
        llmConfig.api_key = settings.groq_api_key;
        llmConfig.api_base = formData.llmConfig.apiBase || 'https://api.groq.com/openai/v1';
      } else if (formData.llmConfig.provider === 'custom') {
        llmConfig.api_key = formData.llmConfig.apiKey || settings.custom_api_key;
        // Add custom endpoint to parameters
        llmConfig.parameters.api_base_url = formData.llmConfig.customEndpoint;
      }
      
      // Construct the full request payload
      const requestPayload = {
        dataset_type: formData.dataConfig.format,
        sample_size: parseInt(formData.dataConfig.count.toString()),
        data_source_config: dataSourceConfig,
        llm_config: llmConfig,
        save_result: true,
        save_name: `Generation ${new Date().toISOString()}`
      };
      
      console.log('Sending data to backend:', requestPayload);
      
      // Send request to backend
      const response = await fetch('/api/v1/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
      });
      
      // Handle response
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend error response:', errorData);
        throw new Error(errorData.detail || 'Failed to generate data');
      } 
      
      const result = await response.json();
      console.log('Generated data:', result);
      
      success = true;
      generatedData = result.data;  // Store the generated data
      ToastManager.show('Data generated successfully', 'success');
      
    } catch (error) {
      console.error('Error generating data:', error);
      ToastManager.show(`Generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      loading = false;
    }
  }
  
  // Format options
  const formatOptions = [
    { value: 'qa', label: 'Question & Answer' },
    { value: 'instruction', label: 'Instruction-Response' },
    { value: 'conversation', label: 'Conversation' },
    { value: 'classification', label: 'Classification' },
    { value: 'text', label: 'Text Generation' }
  ];
  
  // LLM options
  const llmOptions = [
    { provider: 'openai', models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'] },
    { provider: 'gemini', models: ['gemini-pro', 'gemini-1.5-pro', 'gemini-2.0-flash'], parameters: ['temperature', 'max_tokens', 'top_p', 'top_k'] },
    { 
      provider: 'groq', 
      models: [
        'llama3-8b-8192', 
        'llama3-70b-8192', 
        'mixtral-8x7b-32768',
        'gemma-7b-it',
      ], 
      parameters: ['temperature', 'max_tokens', 'top_p'] 
    },
    { provider: 'custom', models: [] }
  ];
  
  $: isPDFSource = formData.dataSource.type === 'pdf';

  async function downloadDataset() {
    if (!generatedData) {
      ToastManager.show('No data available to download', 'error');
      return;
    }

    try {
      // Parse all JSON content from the response
      const allQAPairs = generatedData.reduce((acc: any[], item: any) => {
        try {
          // Extract the JSON string from the content field
          const jsonStr = item.content.replace(/```json\n|\n```/g, '');
          const parsedData = JSON.parse(jsonStr);
          return [...acc, ...parsedData];
        } catch (error) {
          console.error('Error parsing JSON content:', error);
          return acc;
        }
      }, []);

      // Convert the data to a string based on the format
      let content = '';
      let filename = 'synthetic_data';
      let mimeType = 'text/plain';
      
      if (formData.downloadFormat === 'json') {
        content = JSON.stringify(allQAPairs, null, 2);
        filename += '.json';
        mimeType = 'application/json';
      } else if (formData.downloadFormat === 'txt') {
        if (formData.dataConfig.format === 'qa') {
          // Format as Q&A pairs
          content = allQAPairs.map((item: any) => 
            `Question: ${item.question}\nAnswer: ${item.answer}\n\n`
          ).join('');
          filename += '_qa.txt';
        } else if (formData.dataConfig.format === 'instructionResponse') {
          // Format as instruction-response pairs
          content = allQAPairs.map((item: any) => 
            `Instruction: ${item.instruction}\nResponse: ${item.response}\n\n`
          ).join('');
          filename += '_instruction_response.txt';
        } else {
          // Default to JSON format if format is not recognized
          content = JSON.stringify(allQAPairs, null, 2);
          filename += '.json';
          mimeType = 'application/json';
        }
      } else if (formData.downloadFormat === 'csv') {
        // Convert to CSV format
        const headers = Object.keys(allQAPairs[0] || {});
        const csvRows = [headers.join(',')];
        
        for (const item of allQAPairs) {
          const row = headers.map(header => {
            const value = item[header] || '';
            // Escape commas and quotes in the value
            return `"${String(value).replace(/"/g, '""')}"`;
          });
          csvRows.push(row.join(','));
        }
        
        content = csvRows.join('\n');
        filename += '.csv';
        mimeType = 'text/csv';
      }

      // Create a blob and download
      const blob = new Blob([content], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      ToastManager.show('Dataset downloaded successfully', 'success');
    } catch (error) {
      console.error('Error downloading dataset:', error);
      ToastManager.show('Failed to download dataset', 'error');
    }
  }

  async function generateData() {
    loading = true;
    progress = 0;
    currentBatch = 0;
    batchProgress = 0;
    startTime = Date.now();
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data_source_config: {
                    type: formData.dataSource.type,
                    source_path: "data/uploads",
                    parameters: {
                        extract_metadata: "true",
                        extract_layout: "true"
                    }
                },
                llm_config: {
                    type: formData.llmConfig.provider,
                    model: formData.llmConfig.model,
                    temperature: formData.llmConfig.temperature,
                    max_tokens: formData.llmConfig.maxTokens,
                    custom_endpoint: formData.llmConfig.customEndpoint,
                    model_name: formData.llmConfig.modelName,
                    top_p: formData.llmConfig.topP,
                    top_k: formData.llmConfig.topK,
                    api_base: formData.llmConfig.apiBase
                },
                dataset_type: formData.dataConfig.format,
                sample_size: formData.dataConfig.count,
                output_format: "json"
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate data');
        }

        const result = await response.json();
        generatedData = result.data;
        
        // Update progress information
        totalBatches = result.metadata.total_batches;
        currentBatch = totalBatches;
        progress = 100;
        batchProgress = 100;
        
        ToastManager.show('Data generated successfully!', 'success');
    
    } catch (error) {
        console.error('Error generating data:', error);
        ToastManager.show(`Error: ${error instanceof Error ? error.message : 'Failed to generate data'}`, 'error');
    } finally {
        loading = false;
        startTime = null;
    }
  }

  // Function to update estimated time remaining
  function updateEstimatedTime() {
    if (!startTime || progress === 0) return;
    
    const elapsedTime = (Date.now() - startTime) / 1000; // in seconds
    const timePerBatch = elapsedTime / currentBatch;
    const remainingBatches = totalBatches - currentBatch;
    const estimatedSeconds = Math.round(timePerBatch * remainingBatches);
    
    if (estimatedSeconds < 60) {
        estimatedTimeRemaining = `${estimatedSeconds} seconds`;
    } else {
        const minutes = Math.floor(estimatedSeconds / 60);
        const seconds = estimatedSeconds % 60;
        estimatedTimeRemaining = `${minutes} minute${minutes !== 1 ? 's' : ''} ${seconds} seconds`;
    }
  }

  // Start progress updates when loading begins
  $: if (loading && startTime) {
    progressInterval = window.setInterval(updateEstimatedTime, 1000);
  }

  // Cleanup interval on component destroy or when loading stops
  onDestroy(() => {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
  });

  $: if (!loading) {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
  }
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
      <div class="mt-4 flex flex-col space-y-4">
        <div class="flex items-center space-x-4">
          <select 
            bind:value={formData.downloadFormat} 
            class="input w-32"
          >
            <option value="json">JSON</option>
            <option value="txt">TXT</option>
            <option value="csv">CSV</option>
          </select>
          <button class="btn btn-primary" on:click={downloadDataset}>Download Dataset</button>
        </div>
        <button class="btn btn-secondary" on:click={() => { success = false; currentStep = 0; generatedData = null; }}>Generate Another</button>
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
              <input type="radio" name="dataSourceType" value="json" bind:group={formData.dataSource.type} class="mr-2">
              <span>JSON Data</span>
            </label>
            <label class="flex items-center">
              <input type="radio" name="dataSourceType" value="text" bind:group={formData.dataSource.type} class="mr-2">
              <span>Text Input</span>
            </label>
          </div>
          
          {#if formData.dataSource.type === 'pdf'}
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">PDF File Upload</label>
              <div class="flex flex-col space-y-3">
                <div class="flex items-center space-x-2">
                  <input 
                    type="file" 
                    accept=".pdf" 
                    on:change={handleFileSelect}
                    class="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 text-sm text-secondary-700"
                  >
                  {#if pdfFileName}
                    <span class="text-sm text-secondary-600">Selected: {pdfFileName}</span>
                  {/if}
                </div>
                
                <button 
                  on:click={generateWithUpload} 
                  class="btn btn-primary {selectedFile ? '' : 'opacity-50 cursor-not-allowed'}"
                  disabled={!selectedFile || loading}
                >
                  {#if loading}
                    <Spinner size="small" class_name="mr-2" /> Uploading...
                  {:else}
                    Upload PDF
                  {/if}
                </button>
                
                {#if isFileUploading}
                  <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-primary-600 h-2.5 rounded-full" style="width: {uploadProgress}%"></div>
                  </div>
                {/if}
                
                <div class="flex justify-between items-center mt-2">
                  <p class="text-sm text-secondary-600 bg-blue-50 p-2 rounded">
                    Upload a PDF file or use files already on the server in the data/uploads directory
                  </p>
                  
                  <button 
                    on:click={generateWithUpload} 
                    class="btn btn-success ml-4 {selectedFile ? '' : 'opacity-50 cursor-not-allowed'}"
                    disabled={!selectedFile || loading}
                    title={selectedFile ? 'Upload and generate in one step' : 'Please select a file first'}
                  >
                    {#if loading}
                      <Spinner size="small" class_name="mr-2" /> Generating...
                    {:else}
                      Upload & Generate
                    {/if}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">PDF Source Directory</label>
              <input 
                type="text" 
                value="data/uploads" 
                class="input w-full" 
                disabled
                title="Currently using the data/uploads directory on the server"
              >
              <p class="text-sm text-secondary-600 mt-1 bg-yellow-50 p-2 rounded">
                Note: The system will use PDF files already stored in the data/uploads directory on the server or files you've uploaded above.
              </p>
            </div>
          {:else if formData.dataSource.type === 'json'}
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">JSON File Upload</label>
              <div class="flex flex-col space-y-3">
                <div class="flex items-center space-x-2">
                  <input 
                    type="file" 
                    accept=".json" 
                    on:change={handleFileSelect}
                    class="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 text-sm text-secondary-700"
                  >
                  {#if formData.dataSource.name}
                    <span class="text-sm text-secondary-600">Selected: {formData.dataSource.name}</span>
                  {/if}
                </div>
                
                {#if formData.dataSource.preview}
                  <div class="mt-4">
                    <label class="block text-secondary-700 mb-2">JSON Preview</label>
                    <pre class="json-preview">{formData.dataSource.preview}</pre>
                  </div>
                {/if}
                
                <button 
                  on:click={generateWithUpload} 
                  class="btn btn-primary {formData.dataSource.file ? '' : 'opacity-50 cursor-not-allowed'}"
                  disabled={!formData.dataSource.file}
                >
                  {#if formData.dataSource.file}
                    Upload JSON
                  {:else}
                    Select JSON File
                  {/if}
                </button>
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
        
        {#if formData.llmConfig.provider === 'gemini'}
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Model</label>
            <select bind:value={formData.llmConfig.model} class="input w-full">
              {#each llmOptions.find(o => o.provider === formData.llmConfig.provider)?.models || [] as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
          </div>
          
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">API Key</label>
            <input 
              type="password" 
              bind:value={settings.gemini_api_key} 
              placeholder="Enter your Gemini API key" 
              class="input w-full"
            >
            <p class="text-sm text-secondary-500 mt-1">Your API key will be securely stored in your settings</p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Temperature</label>
              <input type="range" bind:value={formData.llmConfig.temperature} min="0" max="1" step="0.1" class="w-full">
              <div class="flex justify-between">
                <span class="text-sm">0 (Deterministic)</span>
                <span class="text-sm font-medium">{formData.llmConfig.temperature}</span>
                <span class="text-sm">1 (Creative)</span>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Max Tokens</label>
              <input type="number" bind:value={formData.llmConfig.maxTokens} min="100" max="8000" class="input w-full">
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Top P (Optional)</label>
              <input type="range" bind:value={formData.llmConfig.topP} min="0" max="1" step="0.1" class="w-full">
              <div class="flex justify-between">
                <span class="text-sm">0</span>
                <span class="text-sm font-medium">{formData.llmConfig.topP || 'Not set'}</span>
                <span class="text-sm">1</span>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Top K (Optional)</label>
              <input type="number" bind:value={formData.llmConfig.topK} min="1" max="100" class="input w-full" placeholder="Optional">
            </div>
          </div>
        {:else if formData.llmConfig.provider === 'groq'}
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Model</label>
            <select bind:value={formData.llmConfig.model} class="input w-full">
              {#each llmOptions.find(o => o.provider === formData.llmConfig.provider)?.models || [] as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
            <p class="text-sm text-secondary-500 mt-1">
              Choose from Llama 3, Mixtral or Claude models offered by Groq.
            </p>
          </div>
          
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">API Key</label>
            <input 
              type="password" 
              bind:value={settings.groq_api_key} 
              placeholder="Enter your Groq API key" 
              class="input w-full"
            >
            <p class="text-sm text-secondary-500 mt-1">Your Groq API key will be securely stored in your settings</p>
          </div>
          
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">API Base URL</label>
            <input 
              type="text" 
              bind:value={formData.llmConfig.apiBase} 
              placeholder="https://api.groq.com/openai/v1" 
              class="input w-full"
            >
            <p class="text-sm text-secondary-500 mt-1">Default: https://api.groq.com/openai/v1</p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Temperature</label>
              <input type="range" bind:value={formData.llmConfig.temperature} min="0" max="1" step="0.1" class="w-full">
              <div class="flex justify-between">
                <span class="text-sm">0 (Deterministic)</span>
                <span class="text-sm font-medium">{formData.llmConfig.temperature}</span>
                <span class="text-sm">1 (Creative)</span>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Max Tokens</label>
              <input type="number" bind:value={formData.llmConfig.maxTokens} min="100" max="32000" class="input w-full">
            </div>
            
            <div class="mb-4">
              <label class="block text-secondary-700 mb-2">Top P (Optional)</label>
              <input type="range" bind:value={formData.llmConfig.topP} min="0" max="1" step="0.1" class="w-full">
              <div class="flex justify-between">
                <span class="text-sm">0</span>
                <span class="text-sm font-medium">{formData.llmConfig.topP || 'Not set'}</span>
                <span class="text-sm">1</span>
              </div>
            </div>
          </div>
        {:else if formData.llmConfig.provider !== 'custom'}
          <div class="mb-4">
            <label class="block text-secondary-700 mb-2">Model</label>
            <select bind:value={formData.llmConfig.model} class="input w-full">
              {#each llmOptions.find(o => o.provider === formData.llmConfig.provider)?.models || [] as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
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
            {:else if formData.dataSource.type === 'json'}
              <p>JSON File: {pdfFileName}</p>
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
              <p>Model Name: {formData.llmConfig.modelName}</p>
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

    {#if loading}
      <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-8 rounded-lg shadow-xl max-w-md w-full mx-4">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-semibold text-secondary-800">Generating Synthetic Data</h3>
            <div class="animate-spin h-6 w-6 text-primary-600">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          </div>

          <div class="space-y-6">
            <!-- Overall Progress -->
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-sm font-medium text-secondary-700">Overall Progress</span>
                <span class="text-sm font-medium text-primary-600">{progress}%</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3">
                <div 
                  class="bg-primary-600 h-3 rounded-full transition-all duration-500 ease-out" 
                  style="width: {progress}%"
                ></div>
              </div>
            </div>

            <!-- Batch Progress -->
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-sm font-medium text-secondary-700">Current Batch</span>
                <span class="text-sm font-medium text-primary-600">{currentBatch} of {totalBatches}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div 
                  class="bg-primary-500 h-2 rounded-full transition-all duration-500 ease-out" 
                  style="width: {batchProgress}%"
                ></div>
              </div>
            </div>

            <!-- Status Information -->
            <div class="bg-secondary-50 rounded-lg p-4 space-y-3">
              <div class="flex items-center space-x-2">
                <svg class="h-5 w-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span class="text-sm font-medium text-secondary-700">Processing Status</span>
              </div>
              <p class="text-sm text-secondary-600">
                {#if currentBatch === 0}
                  Initializing generation process...
                {:else if currentBatch < totalBatches}
                  Processing batch {currentBatch} of {totalBatches}
                {:else}
                  Finalizing results...
                {/if}
              </p>
              {#if estimatedTimeRemaining}
                <div class="flex items-center space-x-2">
                  <svg class="h-5 w-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="text-sm text-secondary-600">Estimated time remaining: {estimatedTimeRemaining}</span>
                </div>
              {/if}
            </div>

            <!-- Tips -->
            <div class="bg-blue-50 rounded-lg p-4">
              <div class="flex items-center space-x-2 mb-2">
                <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="text-sm font-medium text-blue-700">Tips</span>
              </div>
              <ul class="text-sm text-blue-600 space-y-1">
                <li>• Generation time varies based on your configuration</li>
                <li>• Larger sample sizes will take longer to process</li>
                <li>• You can safely close this window - generation will continue</li>
                <li>• Results will be available for download once complete</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .json-preview {
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 4px;
    max-height: 300px;
    overflow-y: auto;
    font-family: monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
</style> 