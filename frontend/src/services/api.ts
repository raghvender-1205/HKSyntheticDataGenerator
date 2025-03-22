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
const API_PREFIX = '/api/v1';

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
      const response = await apiClient.get<Record<string, DataSource>>(`${API_PREFIX}/datasources/plugins`);
      return response.data || {};
    } catch (error) {
      console.error('Error fetching data sources:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<DataSource> {
    try {
      const response = await apiClient.get<DataSource>(`${API_PREFIX}/datasources/plugins/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data source config for ${id}:`, error);
      throw error;
    }
  },

  // Create a datasource instance
  async create(config: DataSourceConfig): Promise<{ status: string, datasource_id: string }> {
    const response = await apiClient.post(`${API_PREFIX}/datasources/create`, config);
    return response.data;
  },

  // Get datasource info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`${API_PREFIX}/datasources/${id}/info`);
    return response.data;
  },

  // Load documents from a datasource
  async loadDocuments(id: string): Promise<Document[]> {
    const response = await apiClient.get(`${API_PREFIX}/datasources/${id}/load`);
    return response.data;
  },

  // Get available file paths from the system
  async getAvailableFiles(directory: string = ''): Promise<string[]> {
    try {
      const response = await apiClient.get(`${API_PREFIX}/utils/files`, {
        params: { directory }
      });
      return response.data.files || [];
    } catch (error) {
      console.error('Error fetching available files:', error);
      return [];
    }
  },

  // Upload a file to the server
  async uploadFile(file: File, directory: string = ''): Promise<{ filename: string, path: string, message: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('directory', directory);
      
      const response = await apiClient.post(`${API_PREFIX}/utils/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  },

  // Get supported file types
  async getFileTypes(): Promise<string[]> {
    try {
      const response = await apiClient.get(`${API_PREFIX}/utils/file-types`);
      return response.data.types || [];
    } catch (error) {
      console.error('Error fetching file types:', error);
      return ["txt", "json", "csv"]; // Fallback defaults
    }
  },

  // Get supported encodings
  async getEncodings(): Promise<string[]> {
    try {
      const response = await apiClient.get(`${API_PREFIX}/utils/encodings`);
      return response.data.encodings || [];
    } catch (error) {
      console.error('Error fetching encodings:', error);
      return ["utf-8", "utf-16", "ascii", "latin-1"]; // Fallback defaults
    }
  },

  // Get active datasource instances
  async getActiveInstances(): Promise<string[]> {
    try {
      // This endpoint would need to be implemented on the backend
      // For now, we'll work with local state
      return [];
    } catch (error) {
      console.error('Error fetching active datasource instances:', error);
      return [];
    }
  },

  // Delete a datasource instance
  async deleteInstance(id: string): Promise<boolean> {
    try {
      // This endpoint would need to be implemented on the backend
      // For now, we'll simulate success
      console.log(`Would delete datasource instance ${id}`);
      return true;
    } catch (error) {
      console.error(`Error deleting datasource instance ${id}:`, error);
      return false;
    }
  }
};

// LLM providers API
export const llmService = {
  async getAll(): Promise<Record<string, LLMProvider>> {
    try {
      const response = await apiClient.get<Record<string, LLMProvider>>(`${API_PREFIX}/llms/plugins`);
      return response.data || {};
    } catch (error) {
      console.error('Error fetching LLM providers:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<LLMProvider> {
    try {
      const response = await apiClient.get<LLMProvider>(`${API_PREFIX}/llms/plugins/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching LLM provider config for ${id}:`, error);
      throw error;
    }
  },

  // Create an LLM instance
  async create(config: LLMConfig): Promise<{ status: string, llm_id: string }> {
    const response = await apiClient.post(`${API_PREFIX}/llms/create`, config);
    return response.data;
  },

  // Get LLM info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`${API_PREFIX}/llms/${id}/info`);
    return response.data;
  },

  // Generate text using an LLM
  async generate(id: string, prompt: string, options?: { temperature?: number, max_tokens?: number }): Promise<any> {
    const response = await apiClient.post(`${API_PREFIX}/llms/${id}/generate`, {
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
      const response = await apiClient.get<Record<string, DatasetGenerator>>(`${API_PREFIX}/datasets/generators`);
      return response.data || {};
    } catch (error) {
      console.error('Error fetching dataset generators:', error);
      throw error;
    }
  },
  
  async getConfig(id: string): Promise<DatasetGenerator> {
    try {
      const response = await apiClient.get<DatasetGenerator>(`${API_PREFIX}/datasets/generators/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching generator config for ${id}:`, error);
      throw error;
    }
  },

  // Create a dataset generator instance
  async create(config: DatasetGeneratorConfig): Promise<{ status: string, generator_id: string }> {
    const response = await apiClient.post(`${API_PREFIX}/datasets/generators/create`, config);
    return response.data;
  },

  // Get dataset generator info
  async getInfo(id: string): Promise<any> {
    const response = await apiClient.get(`${API_PREFIX}/datasets/generators/${id}/info`);
    return response.data;
  },

  // Generate a dataset
  async generate(generatorId: string, request: GenerateDatasetRequest): Promise<Dataset> {
    const response = await apiClient.post(`${API_PREFIX}/datasets/generators/${generatorId}/generate`, request);
    return response.data;
  },

  async generateDataset(config: any): Promise<string> {
    try {
      const response = await apiClient.post<ApiResponse<string>>(`${API_PREFIX}/generate`, config);
      return response.data.data || '';
    } catch (error) {
      console.error('Error generating dataset:', error);
      throw error;
    }
  }
}; 