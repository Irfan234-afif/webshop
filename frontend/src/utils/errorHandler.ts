/**
 * Extract a user-friendly error message from various error formats
 * Handles Frappe API errors, ValidationErrors, and standard Error objects
 */
export function extractErrorMessage(error: any): string {
  // If it's a string, return it directly
  if (typeof error === 'string') {
    return error
  }

  if (Array.isArray(error.messages) && error.messages.length > 0 && typeof error.messages[0] === 'string') {
    return error.messages.join('\n')
  }

  // Get the actual error data - could be nested in Axios or frappe-ui wrapper
  const errorData = error?.response?.data || error?.data || error

  // Try _server_messages which Frappe often uses for user-facing validation errors
  if (errorData?._server_messages) {
    try {
      const messages = typeof errorData._server_messages === 'string' 
        ? JSON.parse(errorData._server_messages) 
        : errorData._server_messages

      if (Array.isArray(messages) && messages.length > 0) {
        const parsedMessages = messages.map((msg: any) => {
          try {
            // Each message might be a JSON string itself or already an object
            const parsed = typeof msg === 'string' ? JSON.parse(msg) : msg
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

  // Try the 'messages' field which frappe-ui often populates
  if (errorData?.messages && Array.isArray(errorData.messages) && errorData.messages.length > 0) {
    return errorData.messages.map((m: any) => typeof m === 'string' ? m : (m.message || JSON.stringify(m))).join('\n')
  }

  // Try to get the exception message from Frappe error structure (often contains traceback in dev)
  if (errorData?.exc) {
    try {
      const exc = typeof errorData.exc === 'string' ? JSON.parse(errorData.exc) : errorData.exc
      
      if (Array.isArray(exc) && exc.length > 0) {
        // Look for the last line if it's a traceback array
        const lastLine = exc[exc.length - 1]
        if (typeof lastLine === 'string' && lastLine.includes('ValidationError:')) {
           const match = lastLine.match(/ValidationError:\s*(.+?)(?:\n|$)/)
           if (match && match[1]) return match[1].trim()
        }
        return exc.join('\n')
      } else if (typeof exc === 'string') {
        const match = exc.match(/ValidationError:\s*(.+?)(?:\n|$)/)
        if (match && match[1]) return match[1].trim()
        return exc
      }
    } catch (e) {
      if (typeof errorData.exc === 'string') {
        const match = errorData.exc.match(/ValidationError:\s*(.+?)(?:\n|$)/)
        if (match && match[1]) {
          return match[1].trim()
        }
        return errorData.exc
      }
    }
  }

  // Try the exception field directly
  if (errorData?.exception) {
    const exceptionMsg = extractMessageFromException(errorData.exception)
    if (exceptionMsg) {
      return exceptionMsg
    }
  }

  // Try standard message field (Axios default or Frappe fallback)
  if (errorData?.message || error?.message) {
    const message = errorData?.message || error?.message
    
    // Remove the method path prefix if present (common in Frappe errors)
    const match = message.match(/webshop\.[^\s]+\s+(.+)/)
    if (match && match[1]) {
      return match[1]
    }
    
    return message
  }

  // Fallback to error details or generic message
  if (errorData?.httpStatus && errorData?.httpStatusText) {
    return `${errorData.httpStatusText} (${errorData.httpStatus})`
  }

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
