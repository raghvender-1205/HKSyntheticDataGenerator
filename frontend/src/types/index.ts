// Basic types
export interface ApiResponse<T> {
  data: T;
  status: string;
  message?: string;
}

// Data Source Types
export interface DataSourceConfig {
  source_id: string;
  name: string;
  description?: string;
  source_type?: string;
  [key: string]: any;
}

export interface DataSource {
  id: string;
  name: string;
  description?: string;
  config_schema: any;
}

export interface Document {
  content: string;
  metadata: Record<string, any>;
}

// LLM Types
export interface LLMConfig {
  model_id: string;
  name: string;
  description?: string;
  provider?: string;
  temperature?: number;
  max_tokens?: number;
  [key: string]: any;
}

export interface LLMProvider {
  id: string;
  name: string;
  description?: string;
  provider: string;
  config_schema: any;
}

export interface LLMResponse {
  text: string;
  metadata: Record<string, any>;
}

// Dataset Generator Types
export interface DatasetGeneratorConfig {
  generator_id: string;
  name: string;
  description?: string;
  generator_type?: string;
  [key: string]: any;
}

export interface DatasetGenerator {
  id: string;
  name: string;
  description?: string;
  config_schema: any;
}

export interface DatasetItem {
  data: Record<string, any>;
  metadata: Record<string, any>;
}

export interface Dataset {
  name: string;
  description?: string;
  items: DatasetItem[];
  metadata: Record<string, any>;
}

export interface GenerateDatasetRequest {
  datasource_id: string;
  llm_id: string;
  options?: Record<string, any>;
} 