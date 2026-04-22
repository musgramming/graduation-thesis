def naming_with_sbd(id_name : str) -> dict:
    """
    Trả về định danh có kèm index "with-sbd"

    Args:
        id_name (str): Tên của id đó

    Returns: 
        dict: Tên định danh chính của id đó
    """
    return {"type": id_name, "index" : "with-sbd"}



def naming_without_sbd(id_name : str) -> dict:
    """
    Trả về định danh có kèm index "without-sbd"

    Args:
        id_name (str): Tên của id đó

    Returns: 
        dict: Tên định danh chính của id đó
    """
    return {"type": id_name, "index" : "without-sbd"}
