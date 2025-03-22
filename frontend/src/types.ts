// Data source and configuration
export interface SchemaProperty {
  type: string;
  title?: string;
  description?: string;
  enum?: string[];
  default?: any;
  hidden?: boolean;
  minimum?: number;
  maximum?: number;
}

export interface ConfigSchema {
  title: string;
  type: string;
  properties: Record<string, SchemaProperty>;
  required: string[];
}

export interface DataSource {
  id: string;
  name: string;
  description?: string;
  config_schema: ConfigSchema;
}

export interface DataSourceConfig {
  source_id: string;
  [key: string]: any;
}

// LLM Providers
export interface LLMProvider {
  id: string;
  name: string;
  description?: string;
  supported_models?: string[];
  config_schema: ConfigSchema;
}

export interface LLMConfig {
  model_id: string;
  [key: string]: any;
}

// Dataset Generators
export interface DatasetGenerator {
  id: string;
  name: string;
  description?: string;
  output_formats?: string[];
  config_schema: ConfigSchema;
}

export interface DatasetGeneratorConfig {
  generator_id: string;
  data_source_id: string;
  llm_id: string;
  [key: string]: any;
}

// Dataset and generation request
export interface Dataset {
  id: string;
  name: string;
  format: string;
  size: number;
  data: any[];
  metadata?: Record<string, any>;
}

export interface GenerateDatasetRequest {
  count: number;
  format: string;
  options?: Record<string, any>;
}

// Document type for imported data
export interface Document {
  id: string;
  content: string;
  metadata?: Record<string, any>;
}

// API Service responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
} 