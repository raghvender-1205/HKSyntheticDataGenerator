import { writable, derived } from 'svelte/store';
import type {
  DataSource,
  DataSourceConfig,
  Document,
  LLMProvider,
  LLMConfig,
  DatasetGenerator,
  DatasetGeneratorConfig,
  Dataset
} from '../types';

// DataSources store
export const dataSources = writable<Record<string, DataSource>>({});
export const activeDataSource = writable<string | null>(null);
export const dataSourceConfig = writable<DataSourceConfig | null>(null);
export const documents = writable<Document[]>([]);

// LLM Providers store
export const llmProviders = writable<Record<string, LLMProvider>>({});
export const activeLlm = writable<string | null>(null);
export const llmConfig = writable<LLMConfig | null>(null);

// Dataset Generators store
export const datasetGenerators = writable<Record<string, DatasetGenerator>>({});
export const activeGenerator = writable<string | null>(null);
export const generatorConfig = writable<DatasetGeneratorConfig | null>(null);
export const generatedDataset = writable<Dataset | null>(null);

// Workflow state
export const workflowStep = writable<number>(1);
export const isLoading = writable<boolean>(false);
export const errorMessage = writable<string | null>(null);

// Derived stores
export const selectedDataSource = derived(
  [dataSources, activeDataSource],
  ([$dataSources, $activeDataSource]) => {
    if (!$activeDataSource) return null;
    return $dataSources[$activeDataSource] || null;
  }
);

export const selectedLlm = derived(
  [llmProviders, activeLlm],
  ([$llmProviders, $activeLlm]) => {
    if (!$activeLlm) return null;
    return $llmProviders[$activeLlm] || null;
  }
);

export const selectedGenerator = derived(
  [datasetGenerators, activeGenerator],
  ([$datasetGenerators, $activeGenerator]) => {
    if (!$activeGenerator) return null;
    return $datasetGenerators[$activeGenerator] || null;
  }
);

// Progress indicator
export const workflowProgress = derived(
  [workflowStep, activeDataSource, activeLlm, activeGenerator, documents, generatedDataset],
  ([$workflowStep, $activeDataSource, $activeLlm, $activeGenerator, $documents, $generatedDataset]) => {
    return {
      step: $workflowStep,
      dataSourceSelected: $activeDataSource !== null,
      llmSelected: $activeLlm !== null,
      generatorSelected: $activeGenerator !== null,
      documentsLoaded: $documents.length > 0,
      datasetGenerated: $generatedDataset !== null
    };
  }
); 