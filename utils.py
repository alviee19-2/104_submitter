def parse_cookie_header(header_string: str) -> dict:
    """
    將 Cookie 字串解析為字典格式。

    Args:
        header_string (str): 包含多個 Cookie 的字串。

    Returns:
        dict: 包含 Cookie 名稱和值的字典。
    """
    cookies = {}
    for part in header_string.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k] = v
    return cookies

        