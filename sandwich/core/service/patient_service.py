def maybe_patient_name(q: str) -> list[str] | None:
    """
    try to turn unstructured text into a patient name

    >>> maybe_patient_name("")
    None
    >>> maybe_patient_name("SMITT, CARL")
    ["Carl", "Smitt"]
    >>> maybe_patient_name("SMITT, CARL JOSEPH")
    ["Carl Joseph", "Smitt"]
    >>> maybe_patient_name("sarah wu")
    ["Sarah", "Wu"]
    >>> maybe_patient_name("bowser")
    ["Bowser", ""]
    """
    q = q.strip()
    if len(q) < 3:  # noqa: PLR2004
        return None
    parts = q.split(",", maxsplit=1)[::-1] if "," in q else q.split(" ", 1)
    result = [p.strip().capitalize() for p in parts]
    if len(result) == 1:
        result.append("")
    return result
