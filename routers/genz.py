"""
GenZ Content Bot — answer logic only (no direct endpoint).

Preserves:
- Internal sub-classifier (social_media / news / movies / quotes / general_knowledge / mixed / unrelated)
- External API integrations (NewsAPI, TMDB, Wikipedia)
- Language detection (langdetect)
- Platform-specific augmented prompt building
- Camera cues, trending hashtags, CTA generation
- Multiple fallback layers

Called internally by the auto-router in classifier.py.
"""

from typing import Dict, Any, List

import requests
from langdetect import detect

from config import NEWS_API_KEY, TMDB_API_KEY, WIKI_SUMMARY_URL, WIKI_HEADERS
from gemini_helpers import gemini_text, gemini_json


# ─── Internal Sub-Classifier ────────────────────────────────────

def classify_query_with_gemini(user_query: str) -> str:
    """
    Returns exactly one of:
    social_media, news, movies, quotes, general_knowledge, mixed, unrelated
    """
    prompt = f"""
Classify the user query into exactly ONE of the following categories:
- social_media
- news
- movies
- quotes
- general_knowledge
- mixed
- unrelated

Rules:
- If the user is asking for ideas, scripts, captions, posts, stories, threads, reels, or carousels specific to any social platform → "social_media".
- If explicitly about current events or headlines → "news".
- If about a film, known movie, cast, or plot → "movies".
- If asking for a quote, poem, or inspiration → "quotes".
- If asking for general facts, definitions, bios, history, or knowledge → "general_knowledge".
- If the query clearly spans multiple categories (e.g., "Instagram reel idea about a movie quote") → "mixed".
- If none of the above apply → "unrelated".

Return JSON only:
{{"category": "<one_of_the_above>"}}

User query: "{user_query}"
"""
    js = gemini_json(prompt)
    category = (js or {}).get("category", "unrelated").strip().lower()
    valid = {
        "social_media", "news", "movies", "quotes",
        "general_knowledge", "mixed", "unrelated",
    }
    return category if category in valid else "unrelated"


# ─── External API Handlers ──────────────────────────────────────

def newsapi_search(
    query: str, page_size: int = 5, language: str = "en"
) -> List[Dict[str, str]]:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
        "sortBy": "publishedAt",
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        data = r.json()
        return [
            {"title": a.get("title", "").strip(), "url": a.get("url", "").strip()}
            for a in data.get("articles", [])
            if a.get("title") and a.get("url")
        ]
    except Exception:
        return []


def tmdb_search_movie(
    title: str, language: str = "en-US", include_adult: bool = False
) -> List[Dict[str, Any]]:
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": language,
        "include_adult": str(include_adult).lower(),
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        data = r.json()
        results = data.get("results", []) or []
        results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        return results
    except Exception:
        return []


def tmdb_trending_fallback() -> List[Dict[str, Any]]:
    url = "https://api.themoviedb.org/3/trending/movie/day"
    params = {"api_key": TMDB_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=12)
        data = r.json()
        return data.get("results", []) or []
    except Exception:
        return []


def wikipedia_summary(topic: str) -> str:
    try:
        r = requests.get(
            WIKI_SUMMARY_URL + requests.utils.quote(topic),
            headers=WIKI_HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            extract = r.json().get("extract", "").strip()
            if extract:
                return extract
    except Exception:
        pass
    # Fallback to Gemini-generated content
    fallback_prompt = (
        f"Generate a GenZ style Instagram carousel caption about '{topic}', "
        "with minimal emojis and engaging tone."
    )
    return gemini_text(fallback_prompt)


# ─── Language Detection ──────────────────────────────────────────

def detect_language(text: str) -> str:
    try:
        if not text or text.strip().lower() == "auto":
            return "en"
        text = text.strip().lower()
        if len(text) <= 5 and text.isalpha():
            return text
        return detect(text)
    except Exception:
        return "en"


# ─── Augmented Prompt Builder ────────────────────────────────────

SOCIAL_PLATFORMS = {
    "instagram_reel": "Instagram reel (hook → beat → CTA, use 3-5 hashtags, sec-by-sec cues)",
    "linkedin_post": "LinkedIn post (professional yet modern, 120–180 words)",
    "x_thread": "X/Twitter thread of 4 short tweets",
    "youtube_short": "YouTube Shorts script (voiceover + quick cuts, title + tags)",
    "whatsapp_status": "WhatsApp status ideas — 1 line each (3 options)",
    "tiktok": "TikTok script (punchy hook + trend fit + CTA)",
}


def _build_augmented_prompt(
    user_prompt: str,
    platform: str,
    duration: int,
    content_type: str,
    area_spec: str,
    location: str,
    language: str,
    tone: str,
    include_trending: bool,
    deliver_camera_cues: bool,
    compare_with_reels: bool,
) -> str:
    platform_desc = SOCIAL_PLATFORMS.get(platform, SOCIAL_PLATFORMS["instagram_reel"])

    parts = [
        f"🎯 User idea: {user_prompt}",
        f"📱 Platform: {platform} → {platform_desc}",
        f"⏱ Target duration: {duration} seconds",
        f"🎬 Content type: {content_type}",
    ]
    if area_spec:
        parts.append(f"🍲 Specific focus: {area_spec}")
    if location:
        parts.append(f"📍 Location: {location}")
    parts.append(f"🌐 Language: {language}")
    parts.append(f"🌀 Tone: {tone} (always Gen-Z slang, memes, FOMO hooks)")
    parts.append(f"🔥 Include trending suggestions: {'yes' if include_trending else 'no'}")
    parts.append(f"🎥 Include camera cues & gestures: {'yes' if deliver_camera_cues else 'no'}")
    parts.append(f"📊 Compare with trending reels: {'yes' if compare_with_reels else 'no'}")

    inst = (
        "👉 You are a Gen-Z short-video content creator. Generate a scroll-stopping script "
        "with strong hook in first 3 seconds, energetic pacing, slang, emojis. "
        "If camera cues requested, give second-by-second instructions (close-up/mid/wide + gestures). "
        "If trending is enabled, suggest 2-3 trending sounds and hashtags. "
        "Keep it conversational, funny, and relatable. Always end with a clear CTA."
    )
    parts.append(inst)

    return "\n\n".join(parts)


# ─── Core GenZ Bot Logic ────────────────────────────────────────

def genz_bot_org(
    user_prompt: str,
    platform: str = "instagram_reel",
    duration: int = 30,
    content_type: str = "script_voiceover",
    area_spec: str = "",
    location: str = "",
    language: str = "auto",
    tone: str = "genz",
    include_trending: bool = True,
    deliver_camera_cues: bool = True,
    compare_with_reels: bool = True,
) -> tuple:
    """Returns (reply_text, language_detected)."""
    lang_detected = detect_language(language)

    augmented_prompt = _build_augmented_prompt(
        user_prompt=user_prompt,
        platform=platform,
        duration=duration,
        content_type=content_type,
        area_spec=area_spec,
        location=location,
        language=lang_detected,
        tone="genz",
        include_trending=include_trending,
        deliver_camera_cues=deliver_camera_cues,
        compare_with_reels=compare_with_reels,
    )

    # Primary attempt
    try:
        out = gemini_text(augmented_prompt)
        if out and isinstance(out, str) and out.strip():
            return (
                f"🌐 Language detected/selected: {lang_detected}\n\n{out.strip()}",
                lang_detected,
            )
    except Exception:
        pass

    # Fallback attempt
    try:
        fallback_prompt = "Return a compact GenZ style script:\n\n" + augmented_prompt
        out2 = gemini_text(fallback_prompt)
        if out2 and out2.strip():
            return (
                f"🌐 Language detected/selected: {lang_detected}\n\n{out2.strip()}",
                lang_detected,
            )
    except Exception:
        pass

    # Last resort template
    safe_template = (
        f"🌐 Language detected/selected: {lang_detected}\n\n"
        f"Title: {user_prompt}\nDuration: {duration}s\n\n"
        "Hook (0-3s): [Punchy hook here]\n"
        "Body: [Main script lines]\n"
        "CTA: [e.g., Tag your friend!]\n"
        "Hashtags: #trending #viral #shorts"
    )
    return safe_template, lang_detected


# ─── handle_query (preserves original routing for standalone use) ─

def handle_query(user_query: str) -> str:
    category = classify_query_with_gemini(user_query)

    if category == "social_media":
        platform_map = {
            "instagram": "instagram_reel",
            "reel": "instagram_reel",
            "linkedin": "linkedin_post",
            "thread": "x_thread",
            "twitter": "x_thread",
            "x ": "x_thread",
            "youtube": "youtube_short",
            "short": "youtube_short",
            "whatsapp": "whatsapp_status",
            "tiktok": "tiktok",
        }
        platform = "instagram_reel"
        for keyword, mapped_platform in platform_map.items():
            if keyword in user_query.lower():
                platform = mapped_platform
                break
        reply, _ = genz_bot_org(user_query, platform=platform, tone="genz")
        return reply

    elif category == "news":
        articles = newsapi_search(user_query)
        if articles:
            lines = [f"- [{a['title']}]({a['url']})" for a in articles[:5]]
            return "📰 Latest news:\n" + "\n".join(lines)
        return "No news articles found for that query."

    elif category == "movies":
        movies = tmdb_search_movie(user_query)
        if movies:
            lines = []
            for m in movies[:5]:
                title = m.get("title", "Unknown")
                year = (m.get("release_date") or "")[:4]
                rating = m.get("vote_average", "N/A")
                lines.append(f"- {title} ({year}) ⭐ {rating}")
            return "🎬 Movie results:\n" + "\n".join(lines)
        return "No movies found for that query."

    elif category == "general_knowledge":
        return wikipedia_summary(user_query)

    else:
        prompt = f"""
            You are a GenZ content creator AI. Respond in a casual, trendy, and GenZ style.
            User said: "{user_query}"
            Respond creatively, add humor or wit as appropriate, keep it short, avoid excessive emojis.
            Include hashtags and camera angles if fitting.
            """
        return gemini_text(prompt) or "Couldn't come up with something GenZ enough."
