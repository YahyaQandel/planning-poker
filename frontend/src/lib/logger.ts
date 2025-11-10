// Frontend Logging Utility
// Provides structured logging for all user interactions, API calls, and WebSocket events

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

export enum LogCategory {
  USER_ACTION = 'USER_ACTION',
  API_REQUEST = 'API_REQUEST',
  API_RESPONSE = 'API_RESPONSE',
  WEBSOCKET_SEND = 'WEBSOCKET_SEND',
  WEBSOCKET_RECEIVE = 'WEBSOCKET_RECEIVE',
  NAVIGATION = 'NAVIGATION',
  COMPONENT_LIFECYCLE = 'COMPONENT_LIFECYCLE',
  ERROR = 'ERROR',
  PERFORMANCE = 'PERFORMANCE'
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  category: LogCategory;
  message: string;
  context?: Record<string, any>;
  component?: string;
  userId?: string;
  sessionId?: string;
  roomCode?: string;
  stackTrace?: string;
}

class Logger {
  private sessionId: string;
  private userId?: string;
  private roomCode?: string;
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000; // Keep last 1000 logs in memory

  constructor() {
    this.sessionId = this.generateSessionId();
    this.initializeLogger();
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeLogger() {
    // Log the session start
    this.info(LogCategory.COMPONENT_LIFECYCLE, 'Frontend logger initialized', {
      sessionId: this.sessionId,
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    // Capture unhandled errors
    window.addEventListener('error', (event) => {
      this.error(LogCategory.ERROR, 'Unhandled JavaScript error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.toString()
      });
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.error(LogCategory.ERROR, 'Unhandled promise rejection', {
        reason: event.reason?.toString()
      });
    });
  }

  setUser(userId: string) {
    this.userId = userId;
    this.info(LogCategory.USER_ACTION, 'User set', { userId });
  }

  setRoom(roomCode: string) {
    this.roomCode = roomCode;
    this.info(LogCategory.NAVIGATION, 'Room set', { roomCode });
  }

  private createLogEntry(
    level: LogLevel,
    category: LogCategory,
    message: string,
    context?: Record<string, any>,
    component?: string
  ): LogEntry {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      category,
      message,
      context,
      component,
      userId: this.userId,
      sessionId: this.sessionId,
      roomCode: this.roomCode
    };

    if (level === LogLevel.ERROR) {
      entry.stackTrace = new Error().stack;
    }

    return entry;
  }

  private addLog(entry: LogEntry) {
    this.logs.push(entry);
    
    // Keep only the last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Console output with styling
    this.outputToConsole(entry);
  }

  private outputToConsole(entry: LogEntry) {
    const timestamp = entry.timestamp.split('T')[1].split('.')[0];
    const prefix = `[${timestamp}] [${entry.level}] [${entry.category}]`;
    
    let style = '';
    switch (entry.level) {
      case LogLevel.DEBUG:
        style = 'color: #888';
        break;
      case LogLevel.INFO:
        style = 'color: #0066cc';
        break;
      case LogLevel.WARN:
        style = 'color: #ff9900';
        break;
      case LogLevel.ERROR:
        style = 'color: #cc0000; font-weight: bold';
        break;
    }

    const contextInfo = entry.component ? ` [${entry.component}]` : '';
    const roomInfo = entry.roomCode ? ` [Room: ${entry.roomCode}]` : '';
    const userInfo = entry.userId ? ` [User: ${entry.userId}]` : '';

    console.groupCollapsed(`%c${prefix}${contextInfo}${roomInfo}${userInfo} ${entry.message}`, style);
    
    if (entry.context) {
      console.log('Context:', entry.context);
    }
    
    if (entry.stackTrace) {
      console.log('Stack trace:', entry.stackTrace);
    }
    
    console.groupEnd();
  }

  debug(category: LogCategory, message: string, context?: Record<string, any>, component?: string) {
    const entry = this.createLogEntry(LogLevel.DEBUG, category, message, context, component);
    this.addLog(entry);
  }

  info(category: LogCategory, message: string, context?: Record<string, any>, component?: string) {
    const entry = this.createLogEntry(LogLevel.INFO, category, message, context, component);
    this.addLog(entry);
  }

  warn(category: LogCategory, message: string, context?: Record<string, any>, component?: string) {
    const entry = this.createLogEntry(LogLevel.WARN, category, message, context, component);
    this.addLog(entry);
  }

  error(category: LogCategory, message: string, context?: Record<string, any>, component?: string) {
    const entry = this.createLogEntry(LogLevel.ERROR, category, message, context, component);
    this.addLog(entry);
  }

  // Convenience methods for specific types of logs
  userAction(action: string, context?: Record<string, any>, component?: string) {
    this.info(LogCategory.USER_ACTION, action, context, component);
  }

  apiRequest(method: string, url: string, data?: any, component?: string) {
    this.info(LogCategory.API_REQUEST, `${method} ${url}`, { data }, component);
  }

  apiResponse(method: string, url: string, status: number, data?: any, component?: string) {
    const level = status >= 400 ? LogLevel.ERROR : LogLevel.INFO;
    const entry = this.createLogEntry(level, LogCategory.API_RESPONSE, `${method} ${url} - ${status}`, { data }, component);
    this.addLog(entry);
  }

  websocketSend(type: string, data?: any, component?: string) {
    this.info(LogCategory.WEBSOCKET_SEND, `WS Send: ${type}`, { data }, component);
  }

  websocketReceive(type: string, data?: any, component?: string) {
    this.info(LogCategory.WEBSOCKET_RECEIVE, `WS Receive: ${type}`, { data }, component);
  }

  navigation(from: string, to: string, component?: string) {
    this.info(LogCategory.NAVIGATION, `Navigation: ${from} -> ${to}`, undefined, component);
  }

  componentMount(componentName: string, props?: Record<string, any>) {
    this.debug(LogCategory.COMPONENT_LIFECYCLE, `Component mounted: ${componentName}`, { props }, componentName);
  }

  componentUnmount(componentName: string) {
    this.debug(LogCategory.COMPONENT_LIFECYCLE, `Component unmounted: ${componentName}`, undefined, componentName);
  }

  performance(action: string, duration: number, component?: string) {
    this.info(LogCategory.PERFORMANCE, `${action} completed in ${duration}ms`, { duration }, component);
  }

  // Get logs for debugging or sending to backend
  getLogs(since?: Date): LogEntry[] {
    if (!since) return this.logs;
    const sinceTimestamp = since.toISOString();
    return this.logs.filter(log => log.timestamp >= sinceTimestamp);
  }

  // Export logs as JSON for debugging
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  // Clear logs (useful for testing)
  clearLogs() {
    this.logs = [];
    this.info(LogCategory.COMPONENT_LIFECYCLE, 'Logs cleared');
  }

  // Get session summary for debugging
  getSessionSummary(): Record<string, any> {
    const errorCount = this.logs.filter(log => log.level === LogLevel.ERROR).length;
    const warnCount = this.logs.filter(log => log.level === LogLevel.WARN).length;
    const userActions = this.logs.filter(log => log.category === LogCategory.USER_ACTION).length;
    const apiCalls = this.logs.filter(log => log.category === LogCategory.API_REQUEST).length;
    const wsMessages = this.logs.filter(log => 
      log.category === LogCategory.WEBSOCKET_SEND || log.category === LogCategory.WEBSOCKET_RECEIVE
    ).length;

    return {
      sessionId: this.sessionId,
      userId: this.userId,
      roomCode: this.roomCode,
      totalLogs: this.logs.length,
      errorCount,
      warnCount,
      userActions,
      apiCalls,
      wsMessages,
      sessionDuration: this.logs.length > 0 ? 
        new Date().getTime() - new Date(this.logs[0].timestamp).getTime() : 0
    };
  }
}

// Create singleton instance
export const logger = new Logger();

// Make logger available globally for debugging
declare global {
  interface Window {
    planningPokerLogger: Logger;
  }
}

window.planningPokerLogger = logger;