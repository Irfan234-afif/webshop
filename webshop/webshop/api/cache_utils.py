import frappe


def clear_product_cache(doc=None, method=None):
    """
    Clear all product-related cache entries.
    
    This function is triggered on updates to Item, Website Item, and Item Price doctypes.
    It clears all cache keys matching the pattern 'webshop:items_home:*' to ensure
    fresh data is loaded after any product-related changes.
    
    Note: Uses Redis SCAN command directly because cache keys are dynamically generated
    based on school unit and grade combinations, making enumeration of individual keys
    impractical. This approach is consistent with similar operations in the codebase.
    
    Args:
        doc: The document being saved/updated (optional)
        method: The hook method being called (optional)
    """
    try:
        # Get Frappe cache instance
        cache = frappe.cache()
        
        # Verify redis_connection is available
        if not hasattr(cache, 'redis_connection') or not cache.redis_connection:
            frappe.logger().warning(
                "Redis connection not available, skipping cache clear"
            )
            return
        
        # Clear all product cache keys matching pattern 'webshop:items_home:*'
        # This includes:
        # - webshop:items_home:general
        # - webshop:items_home:{school_unit}:all_grades
        # - webshop:items_home:{school_unit}:{grade}
        
        redis_client = cache.redis_connection
        pattern = "webshop:items_home:*"
        
        # Use Redis SCAN to find all keys matching the pattern
        # SCAN is preferred over KEYS as it doesn't block the Redis server
        keys_to_delete = []
        cursor = 0
        
        while True:
            cursor, keys = redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                keys_to_delete.extend(keys)
            if cursor == 0:
                break
        
        # Delete all found keys in a single operation
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
            
            # Log cache clearing activity only in development mode
            if frappe.conf.get("developer_mode"):
                doctype_name = doc.doctype if doc else "Unknown"
                frappe.logger().info(
                    f"Product cache cleared: {len(keys_to_delete)} key(s) deleted "
                    f"due to {doctype_name} update"
                )
                
    except AttributeError as e:
        # Handle missing redis_connection attribute gracefully
        frappe.logger().warning(
            f"Unable to access Redis connection: {str(e)}"
        )
    except Exception as e:
        # Log error but don't break the save operation
        # This ensures document saves aren't blocked by cache issues
        frappe.log_error(
            title="Product Cache Clear Error",
            message=f"Failed to clear product cache: {str(e)}\n"
                    f"Doctype: {doc.doctype if doc else 'Unknown'}\n"
                    f"Document: {doc.name if doc else 'N/A'}"
        )
