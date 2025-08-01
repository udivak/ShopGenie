/**
 * Simple logger utility
 */
class Logger {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
  }

  /**
   * Log info message
   */
  info(message, ...args) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [INFO] ${message}`, ...args);
  }

  /**
   * Log warning message
   */
  warn(message, ...args) {
    const timestamp = new Date().toISOString();
    console.warn(`[${timestamp}] [WARN] ${message}`, ...args);
  }

  /**
   * Log error message
   */
  error(message, ...args) {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] [ERROR] ${message}`, ...args);
  }

  /**
   * Log debug message (only in development)
   */
  debug(message, ...args) {
    if (this.isDevelopment) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] [DEBUG] ${message}`, ...args);
    }
  }
}

// Export singleton instance
const logger = new Logger();

module.exports = {
  logger
}; 