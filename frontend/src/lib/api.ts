// API Client with comprehensive logging
import { logger, LogCategory } from './logger';

export interface Room {
  code: string;
  session_name: string;
  created_at: string;
  current_story: Story | null;
  participants: Participant[];
  stories: Story[];
}

export interface Participant {
  id: string;
  username: string;
  connected: boolean;
  session_id: string;
  joined_at: string;
  votes: Vote[];
}

export interface Story {
  id: string;
  story_id: string;
  title: string;
  final_points: string | null;
  estimated_at: string | null;
  order: number;
  votes: Vote[];
}

export interface Vote {
  id: string;
  value: string;
  revealed: boolean;
  created_at: string;
  participant: Participant;
}

export interface CreateRoomData {
  story_id?: string;
  title?: string;
}

export interface JoinRoomData {
  username: string;
  session_id: string;
}

export interface AddStoryData {
  story_id?: string;
  title?: string;
}

export interface ConfirmPointsData {
  points: string;
}

class ApiClient {
  private baseUrl: string;
  private component = 'ApiClient';

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    logger.info(LogCategory.COMPONENT_LIFECYCLE, `API client initialized with base URL: ${this.baseUrl}`, undefined, this.component);
  }

  private async makeRequest<T>(
    method: string,
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const requestId = `${method}-${endpoint}-${Date.now()}`;
    
    logger.apiRequest(method, url, data, this.component);
    
    const startTime = performance.now();
    
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        ...options,
      });

      const duration = performance.now() - startTime;
      
      let responseData: T;
      
      if (response.headers.get('content-type')?.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text() as unknown as T;
      }

      logger.apiResponse(method, url, response.status, responseData, this.component);
      logger.performance(`${method} ${endpoint}`, duration, this.component);

      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        logger.error(LogCategory.API_RESPONSE, `API request failed: ${method} ${url}`, {
          status: response.status,
          statusText: response.statusText,
          responseData,
          requestId
        }, this.component);
        throw error;
      }

      logger.info(LogCategory.API_RESPONSE, `API request successful: ${method} ${url}`, {
        status: response.status,
        duration,
        requestId
      }, this.component);

      return responseData;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      logger.error(LogCategory.API_REQUEST, `API request error: ${method} ${url}`, {
        error: error instanceof Error ? error.message : String(error),
        duration,
        requestId,
        data
      }, this.component);
      
      throw error;
    }
  }

  // Room operations
  async createRoom(data: CreateRoomData): Promise<Room> {
    logger.userAction('Create room initiated', data, this.component);
    return this.makeRequest<Room>('POST', '/rooms/', data);
  }

  async getRoom(code: string): Promise<Room> {
    logger.userAction('Get room data', { roomCode: code }, this.component);
    return this.makeRequest<Room>('GET', `/rooms/${code}/`);
  }

  async joinRoom(code: string, data: JoinRoomData): Promise<{ participant: Participant; room: Room }> {
    logger.userAction('Join room', { roomCode: code, ...data }, this.component);
    return this.makeRequest<{ participant: Participant; room: Room }>('POST', `/rooms/${code}/join/`, data);
  }

  async addStory(code: string, data: AddStoryData): Promise<Story> {
    logger.userAction('Add story', { roomCode: code, ...data }, this.component);
    return this.makeRequest<Story>('POST', `/rooms/${code}/add_story/`, data);
  }

  async resetRoom(code: string): Promise<{ message: string }> {
    logger.userAction('Reset room', { roomCode: code }, this.component);
    return this.makeRequest<{ message: string }>('POST', `/rooms/${code}/reset/`);
  }

  async revealVotes(code: string): Promise<Room> {
    logger.userAction('Reveal votes', { roomCode: code }, this.component);
    return this.makeRequest<Room>('POST', `/rooms/${code}/reveal/`);
  }

  async confirmPoints(code: string, data: ConfirmPointsData): Promise<Room> {
    logger.userAction('Confirm points', { roomCode: code, ...data }, this.component);
    return this.makeRequest<Room>('POST', `/rooms/${code}/confirm_points/`, data);
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Log API client creation
logger.info(LogCategory.COMPONENT_LIFECYCLE, 'API client instance created', undefined, 'ApiClient');