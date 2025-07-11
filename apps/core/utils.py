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