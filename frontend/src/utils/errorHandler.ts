/**
 * Extract a user-friendly error message from various error formats
 * Handles Frappe API errors, ValidationErrors, and standard Error objects
 */
export function extractErrorMessage(error: any): string {
  // If it's a string, return it directly
  if (typeof error === 'string') {
    return error
  }

  // Try to get the exception message from Frappe error structure
  if (error?.exc) {
    try {
      // Frappe errors often come in this format with exc containing stringified JSON
      const exc = typeof error.exc === 'string' ? JSON.parse(error.exc) : error.exc
      
      // Extract the actual error message
      if (Array.isArray(exc) && exc.length > 0) {
        // Sometimes it's an array of error strings
        return exc.join('\n')
      } else if (typeof exc === 'string') {
        return exc
      }
    } catch (e) {
      // If JSON parsing fails, try to extract message from the string
      if (typeof error.exc === 'string') {
        // Look for ValidationError pattern and extract the actual message
        const match = error.exc.match(/ValidationError:\s*(.+?)(?:\n|$)/)
        if (match && match[1]) {
          return match[1].trim()
        }
        return error.exc
      }
    }
  }

  // Try _server_messages which Frappe sometimes uses
  if (error?._server_messages) {
    try {
      const messages = JSON.parse(error._server_messages)
      if (Array.isArray(messages) && messages.length > 0) {
        // Each message might be a JSON string itself
        const parsedMessages = messages.map((msg: any) => {
          try {
            const parsed = JSON.parse(msg)
            return parsed.message || msg
          } catch {
            return msg
          }
        })
        return parsedMessages.join('\n')
      }
    } catch (e) {
      // Ignore parsing errors
    }
  }

  // Try the exception field
  if (error?.exception) {
    // Sometimes the exception contains the detailed message
    const exceptionMsg = extractMessageFromException(error.exception)
    if (exceptionMsg) {
      return exceptionMsg
    }
  }

  // Try standard message field
  if (error?.message) {
    // Clean up the message if it contains the full path
    const message = error.message
    
    // Remove the method path prefix if present
    const match = message.match(/webshop\.[^\s]+\s+(.+)/)
    if (match && match[1]) {
      return match[1]
    }
    
    return message
  }

  // Fallback to error details or generic message
  if (error?.httpStatus && error?.httpStatusText) {
    return `${error.httpStatusText} (${error.httpStatus})`
  }

  // Last resort
  return 'Terjadi kesalahan. Silakan coba lagi.'
}

/**
 * Extract message from exception string
 */
function extractMessageFromException(exception: string): string | null {
  // Try to extract from ValidationError pattern
  const validationMatch = exception.match(/ValidationError:\s*(.+?)(?:\n|$)/)
  if (validationMatch && validationMatch[1]) {
    return validationMatch[1].trim()
  }

  // Try to extract from generic error pattern
  const errorMatch = exception.match(/Error:\s*(.+?)(?:\n|$)/)
  if (errorMatch && errorMatch[1]) {
    return errorMatch[1].trim()
  }

  return null
}

/**
 * Format error for display in UI
 */
export function formatErrorForDisplay(error: any): { message: string; details?: string } {
  const message = extractErrorMessage(error)
  
  // Optionally include technical details in development
  const details = import.meta.env.DEV ? JSON.stringify(error, null, 2) : undefined
  
  return { message, details }
}
