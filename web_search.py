from duckduckgo_search import DDGS


def get_web_context(query, max_results=3):
    """
    Rákeres a weben a megadott szövegre a DuckDuckGo segítségével,
    és egy formázott szöveget ad vissza az AI számára.
    """
    try:
        ddgs = DDGS()
        # Keresés indítása a weben
        results = ddgs.text(query, max_results=max_results)

        if not results:
            return "Nem találtam releváns információt a weben a megadott kérdéshez."

        # Az eredmények összefűzése egy kontextus szöveggé
        context = "--- ÉLŐ WEBES KERESÉS EREDMÉNYEI ---\n"
        context += "Kérlek, vedd figyelembe az alábbi friss információkat a webről a válaszadásnál:\n\n"

        for i, res in enumerate(results):
            context += f"[{i + 1}] Cím: {res['title']}\n"
            context += f"Kivonat: {res['body']}\n"
            context += f"Forrás link: {res['href']}\n\n"

        return context

    except Exception as e:
        return f"Hiba történt a webes keresés során: {e}"