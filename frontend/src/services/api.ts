import axios from 'axios';
import type {
  DataSource,
  DataSourceConfig,
  Document,
  LLMProvider,
  LLMConfig,
  DatasetGenerator,
  DatasetGeneratorConfig,
  Dataset,
  GenerateDatasetRequest,
  ApiResponse
} from '../types';

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with common config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Data sources API
export const datasourceService = {
  async getAll(): Promise<Record<string, DataSource>> {
    try {
      const response = await apiClient.get<Record<string, DataSource>>('/datasources/plugins');
      return response.data || {};
    } catch (error) {
      console.error('Error fetching data sources:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<DataSource> {
    try {
      const response = await apiClient.get<DataSource>(`/datasources/plugins/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data source config for ${id}:`, error);
      throw error;
    }
  },

  // Create a datasource instance
  async create(config: DataSourceConfig): Promise<{ status: string, datasource_id: string }> {
    const response = await apiClient.post('/datasources/create', config);
    return response.data;
  },

  // Get datasource info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`/datasources/${id}/info`);
    return response.data;
  },

  // Load documents from a datasource
  async loadDocuments(id: string): Promise<Document[]> {
    const response = await apiClient.get(`/datasources/${id}/load`);
    return response.data;
  }
};

// LLM providers API
export const llmService = {
  async getAll(): Promise<Record<string, LLMProvider>> {
    try {
      const response = await apiClient.get<Record<string, LLMProvider>>('/llms/plugins');
      return response.data || {};
    } catch (error) {
      console.error('Error fetching LLM providers:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<LLMProvider> {
    try {
      const response = await apiClient.get<LLMProvider>(`/llms/plugins/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching LLM provider config for ${id}:`, error);
      throw error;
    }
  },

  // Create an LLM instance
  async create(config: LLMConfig): Promise<{ status: string, llm_id: string }> {
    const response = await apiClient.post('/llms/create', config);
    return response.data;
  },

  // Get LLM info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`/llms/${id}/info`);
    return response.data;
  },

  // Generate text using an LLM
  async generate(id: string, prompt: string, options?: { temperature?: number, max_tokens?: number }): Promise<any> {
    const response = await apiClient.post(`/llms/${id}/generate`, {
      prompt,
      ...options
    });
    return response.data;
  }
};

// Dataset generators API
export const datasetService = {
  async getAll(): Promise<Record<string, DatasetGenerator>> {
    try {
      const response = await apiClient.get<Record<string, DatasetGenerator>>('/datasets/generators');
      return response.data || {};
    } catch (error) {
      console.error('Error fetching dataset generators:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<DatasetGenerator> {
    try {
      const response = await apiClient.get<DatasetGenerator>(`/datasets/generators/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching generator config for ${id}:`, error);
      throw error;
    }
  },

  // Create a dataset generator instance
  async create(config: DatasetGeneratorConfig): Promise<{ status: string, generator_id: string }> {
    const response = await apiClient.post('/datasets/generators/create', config);
    return response.data;
  },

  // Get dataset generator info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`/datasets/generators/${id}/info`);
    return response.data;
  },

  // Generate a dataset
  async generate(generatorId: string, request: GenerateDatasetRequest): Promise<Dataset> {
    const response = await apiClient.post(`/datasets/generators/${generatorId}/generate`, request);
    return response.data;
  },

  async generateDataset(config: any): Promise<string> {
    try {
      const response = await apiClient.post<ApiResponse<string>>('/generate', config);
      return response.data.data || '';
    } catch (error) {
      console.error('Error generating dataset:', error);
      throw error;
    }
  }
}; 