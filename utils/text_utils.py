def turkish_lower(text):
    """
    Türkçe karakterlere uyumlu küçük harfe çevirme.
    I -> ı, İ -> i, Ş -> ş vs.
    """
    if not text:
        return ""
    
    # Özel dönüşümler
    replacements = {
        "I": "ı",
        "İ": "i",
        "Ş": "ş",
        "Ğ": "ğ",
        "Ü": "ü",
        "Ö": "ö",
        "Ç": "ç"
    }
    
    result = []
    for char in text:
        if char in replacements:
            result.append(replacements[char])
        else:
            result.append(char.lower())
    
    return "".join(result)
