import { writable } from 'svelte/store';
import type { DataSource, LLMProvider, DatasetGenerator, Document, DataSourceConfig, LLMConfig, DatasetGeneratorConfig } from './types';

// UI state
export const isLoading = writable(false);
export const errorMessage = writable<string | null>(null);

// Data repositories
export const dataSources = writable<Record<string, DataSource>>({});
export const llmProviders = writable<Record<string, LLMProvider>>({});
export const datasetGenerators = writable<Record<string, DatasetGenerator>>({});

// Workflow state
export const workflowStep = writable(1);
export const activeDataSource = writable<string | null>(null);
export const activeLlm = writable<string | null>(null);
export const activeGenerator = writable<string | null>(null);
export const documents = writable<Document[]>([]);

// Configuration storage
export const dataSourceConfig = writable<DataSourceConfig | null>(null);
export const llmConfig = writable<LLMConfig | null>(null);
export const generatorConfig = writable<DatasetGeneratorConfig | null>(null);

// Progress tracking
export const workflowProgress = writable<{
  step: number;
  completed: boolean;
}>({
  step: 1,
  completed: false
}); 