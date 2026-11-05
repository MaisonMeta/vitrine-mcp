"""Minimal shopping agent loop on Vitrine. No dependencies.

    VITRINE_KEY=vtr_... python3 agent.py "relaxed linen trousers for a summer trip"

Without VITRINE_KEY it still works, with 5 basic results.
"""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("VITRINE_BASE", "https://vitrine.fashion")
KEY = os.environ.get("VITRINE_KEY")

# What your agent knows about its user's taste. Taste only, never identity.
TASTE = {
    "style_tags": ["minimal", "relaxed", "natural"],
    "preferred_colors": ["ecru", "white", "sage"],
    "avoided_colors": ["neon"],
    "price_comfort": {"min": 50, "max": 400},
}


def call(method: str, path: str, body: dict | None = None) -> dict:
    headers = {"content-type": "application/json", "user-agent": "vitrine-quickstart/0.1"}
    if KEY:
        headers["authorization"] = f"Bearer {KEY}"
    req = urllib.request.Request(BASE + path, method=method, headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)


def main() -> None:
    query = " ".join(sys.argv[1:]) or "relaxed linen trousers for a summer trip"
    data = call("POST", "/v1/search", {
        "query": query, "taste_profile": TASTE, "limit": 5,
        "agent": {"name": "vitrine-quickstart", "version": "0.1", "session_id": "demo-session"},
    })
    print(f'\n{data["count"]} picks for "{query}" ({data["meta"]["access"]} access)\n')
    for r in data["results"]:
        print(f'  {r["brand"]}: {r["title"]}, {r["currency"]} {r["price"]:,.0f}, {r["availability"].replace("_", " ")}')
        if "why" in r:
            print(f'    {r["why"]}')
        print(f'    {r["outbound_url"]}')
    if data["meta"]["access"] == "basic":
        print("\n" + data["meta"]["upgrade"])
    if data["results"]:
        top = data["results"][0]["id"]
        alts = call("POST", "/v1/similar", {"id": top, "limit": 5, "filters": {"availability": ["in_stock"]}})
        print(f"\nIn-stock alternatives to the top pick: " + ", ".join(f'{a["brand"]} {a["title"]}' for a in alts["results"][:3]))
    print("\nCheckout always happens at the retailer. Vitrine never sells or takes payment.")


if __name__ == "__main__":
    main()
