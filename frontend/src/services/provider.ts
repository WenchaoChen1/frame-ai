import api from './api';

export interface Provider {
  name: string;
  models: string[];
}

export interface ProvidersResponse {
  providers: Provider[];
}

export const providerService = {
  async getProviders(): Promise<Provider[]> {
    const response = await api.get<ProvidersResponse>('/providers');
    return response.data.providers;
  },
};

