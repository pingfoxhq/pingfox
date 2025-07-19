def get_or_null(model, **kwargs):
    """
    Retrieve an object from the database or return None if it does not exist.
    
    Args:
        model (Model): The Django model to query.
        **kwargs: The lookup parameters to filter the query.
    
    Returns:
        Model instance or None if not found.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
    


def cors_enabled(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    return wrapper


def is_htmx(request):
    """
    Check if the request is an HTMX request.
    
    Args:
        request (HttpRequest): The Django request object.
    
    Returns:
        bool: True if the request is an HTMX request, False otherwise.
    """
    return "HX-Request" in request.headers or "hx-request" in request.headers