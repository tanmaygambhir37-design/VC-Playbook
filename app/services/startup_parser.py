from urllib.parse import urlparse


def _base_payload(url: str) -> dict:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    website = parsed.geturl()
    return {
        "name": "",
        "sector": "",
        "stage": "",
        "description": "",
        "business_model": "",
        "customers": "",
        "location": "",
        "website": website,
        "founding_year": "",
        "revenue_model": "",
        "team_size": "",
        "summary": "",
        "strengths": [],
        "risks": [],
    }


def parse_startup(url: str) -> dict:
    """Mock startup parser.

    This is intentionally isolated so a future OpenAI-backed parser can replace
    this implementation without changing Streamlit page code.
    """
    normalized = url.strip().lower()
    payload = _base_payload(url.strip())

    if "stripe" in normalized:
        payload.update(
            {
                "name": "Stripe",
                "sector": "Fintech",
                "stage": "Growth",
                "description": "Payments infrastructure platform for internet businesses, platforms, and marketplaces.",
                "business_model": "API-first financial infrastructure with payments, billing, treasury, tax, and embedded finance products.",
                "customers": "Startups, SaaS companies, marketplaces, enterprises, and global internet platforms.",
                "location": "San Francisco, CA and Dublin, Ireland",
                "founding_year": "2010",
                "revenue_model": "Transaction fees, subscription software, and usage-based financial infrastructure products.",
                "team_size": "7000",
                "summary": "Stripe is a scaled fintech infrastructure company enabling businesses to accept payments, automate revenue operations, and embed financial services globally.",
                "strengths": [
                    "Deep developer adoption",
                    "Large global payments market",
                    "Broad product expansion surface",
                    "Strong enterprise and startup customer mix",
                ],
                "risks": [
                    "Highly competitive payments category",
                    "Regulatory complexity across markets",
                    "Margin pressure from large enterprise customers",
                ],
            }
        )
        return payload

    if "openai" in normalized:
        payload.update(
            {
                "name": "OpenAI",
                "sector": "AI",
                "stage": "Growth",
                "description": "AI research and product company building frontier models, developer APIs, and AI applications.",
                "business_model": "Model access through API usage, enterprise subscriptions, consumer subscriptions, and platform partnerships.",
                "customers": "Developers, enterprises, consumers, startups, and software platforms building AI-native workflows.",
                "location": "San Francisco, CA",
                "founding_year": "2015",
                "revenue_model": "Usage-based API pricing, ChatGPT subscriptions, enterprise plans, and strategic partnerships.",
                "team_size": "3000",
                "summary": "OpenAI develops frontier AI systems and commercializes them through developer platforms, enterprise products, and consumer applications.",
                "strengths": [
                    "Category-defining AI products",
                    "Strong developer ecosystem",
                    "Massive enterprise demand",
                    "Rapid product velocity",
                ],
                "risks": [
                    "High compute and infrastructure costs",
                    "Regulatory scrutiny",
                    "Fast-moving competitive landscape",
                ],
            }
        )
        return payload

    domain = urlparse(url if "://" in url else f"https://{url}").netloc.replace("www.", "")
    name = domain.split(".")[0].replace("-", " ").title() if domain else "Demo Startup"
    payload.update(
        {
            "name": name,
            "sector": "SaaS",
            "stage": "Seed",
            "description": "AI-enabled software platform helping teams automate operational workflows and improve decision quality.",
            "business_model": "Subscription SaaS with tiered plans and usage-based expansion for larger teams.",
            "customers": "Mid-market operators, finance teams, founders, and strategy teams.",
            "location": "New York, NY",
            "founding_year": "2022",
            "revenue_model": "Monthly and annual software subscriptions with usage-based add-ons.",
            "team_size": "18",
            "summary": f"{name} appears to be an early-stage software company with a focused workflow automation product and a subscription-led go-to-market motion.",
            "strengths": [
                "Clear workflow pain point",
                "Recurring revenue potential",
                "Expandable customer base",
            ],
            "risks": [
                "Early market validation still required",
                "Potentially crowded SaaS category",
                "Sales efficiency needs proof at scale",
            ],
        }
    )
    return payload
