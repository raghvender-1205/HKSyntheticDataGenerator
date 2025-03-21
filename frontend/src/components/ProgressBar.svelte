<script lang="ts">
  import { workflowProgress } from '../stores';
  
  // Define the steps in the workflow
  const steps = [
    { id: 1, label: 'Data Source' },
    { id: 2, label: 'LLM Provider' },
    { id: 3, label: 'Dataset Generator' },
    { id: 4, label: 'Generate' },
    { id: 5, label: 'Preview & Download' }
  ];
</script>

<div class="my-6">
  <div class="relative">
    <!-- Progress bar background -->
    <div class="absolute inset-0 flex items-center" aria-hidden="true">
      <div class="h-0.5 w-full bg-gray-200"></div>
    </div>
    
    <ol class="relative z-10 flex justify-between">
      {#each steps as step}
        <li class="flex items-center">
          <div 
            class="{$workflowProgress.step === step.id ? 'bg-blue-600 border-blue-600 text-white' : ''} 
                  {$workflowProgress.step > step.id ? 'bg-green-500 border-green-500 text-white' : 'bg-white border-gray-300 text-gray-500'} 
                  relative flex h-8 w-8 items-center justify-center rounded-full border shadow-sm"
          >
            {#if $workflowProgress.step > step.id}
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            {:else}
              {step.id}
            {/if}
          </div>
          <span class="ml-2 text-sm font-medium {$workflowProgress.step >= step.id ? 'text-blue-600' : 'text-gray-500'}">
            {step.label}
          </span>
        </li>
      {/each}
    </ol>
  </div>
</div> 