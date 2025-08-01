/**
 * Simple rate limiter for user requests
 */
class RateLimiter {
  constructor() {
    this.requests = new Map();
    this.maxRequests = parseInt(process.env.MAX_REQUESTS_PER_MINUTE) || 10;
    this.windowMs = 60 * 1000; // 1 minute
  }

  /**
   * Check if user can make a request
   */
  checkLimit(userId) {
    const now = Date.now();
    const userRequests = this.requests.get(userId) || [];
    
    // Remove old requests outside the time window
    const validRequests = userRequests.filter(timestamp => 
      now - timestamp < this.windowMs
    );
    
    // Check if user has exceeded the limit
    if (validRequests.length >= this.maxRequests) {
      return false;
    }
    
    // Add current request
    validRequests.push(now);
    this.requests.set(userId, validRequests);
    
    return true;
  }

  /**
   * Get remaining requests for a user
   */
  getRemainingRequests(userId) {
    const now = Date.now();
    const userRequests = this.requests.get(userId) || [];
    
    const validRequests = userRequests.filter(timestamp => 
      now - timestamp < this.windowMs
    );
    
    return Math.max(0, this.maxRequests - validRequests.length);
  }

  /**
   * Get time until next reset for a user
   */
  getTimeUntilReset(userId) {
    const now = Date.now();
    const userRequests = this.requests.get(userId) || [];
    
    if (userRequests.length === 0) {
      return 0;
    }
    
    const oldestRequest = Math.min(...userRequests);
    const resetTime = oldestRequest + this.windowMs;
    
    return Math.max(0, resetTime - now);
  }

  /**
   * Clean up old entries to prevent memory leaks
   */
  cleanup() {
    const now = Date.now();
    
    for (const [userId, requests] of this.requests.entries()) {
      const validRequests = requests.filter(timestamp => 
        now - timestamp < this.windowMs
      );
      
      if (validRequests.length === 0) {
        this.requests.delete(userId);
      } else {
        this.requests.set(userId, validRequests);
      }
    }
  }
}

// Export singleton instance
const rateLimiter = new RateLimiter();

// Clean up old entries every 5 minutes
setInterval(() => {
  rateLimiter.cleanup();
}, 5 * 60 * 1000);

module.exports = {
  rateLimiter
}; 