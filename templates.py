"""
Bluesky Tracker - Modern Dashboard UI
A clean, professional analytics dashboard with dark/light theme support.
"""

import html
import json
from urllib.parse import quote


def get_report_html(data):
    """Generate modern dashboard with professional aesthetics"""

    # Extract data
    stats = data.get("stats", {})
    unfollowers = data.get("unfollowers", [])
    non_mutual = data.get("non_mutual", [])
    followers_only = data.get("followers_only", [])
    mutual_follows = data.get("mutual_follows", [])
    hidden_analytics = data.get("hidden_analytics", {})
    hidden_categories = data.get("hidden_categories", {})
    top_posts = data.get("top_posts", [])
    top_interactors = data.get("top_interactors", [])
    last_updated = data.get("last_updated", "Never")
    bluesky_handle = data.get("bluesky_handle", "your-handle.bsky.social")
    auth_enabled = data.get("auth_enabled", True)

    def esc(value):
        return html.escape("" if value is None else str(value))

    def esc_attr(value):
        return html.escape("" if value is None else str(value), quote=True)

    def safe_url(url):
        if not url:
            return ""
        url = str(url).strip()
        if url.startswith("https://") or url.startswith("http://"):
            return url
        return ""

    bluesky_handle_js = json.dumps(str(bluesky_handle or ""))

    # Calculate metrics
    new_followers = stats.get("new_followers_30d", 0)
    lost_followers = stats.get("unfollowers_30d", 0)
    follower_change = new_followers - lost_followers

    # Hidden accounts data
    hidden_current = hidden_analytics.get("current", {})
    hidden_count = hidden_current.get("hidden_followers", 0)
    blocked_accounts = hidden_categories.get("blocked", {}).get("accounts", [])

    # SVG Icons (Lucide-style, clean)
    icons = {
        "users": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "user-plus": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>',
        "user-minus": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="22" y1="11" x2="16" y2="11"/></svg>',
        "handshake": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></svg>',
        "user-x": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" y1="8" x2="22" y2="13"/><line x1="22" y1="8" x2="17" y2="13"/></svg>',
        "star": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
        "trending-up": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
        "activity": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
        "bar-chart": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
        "heart": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
        "repeat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>',
        "message": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>',
        "bookmark": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>',
        "refresh": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>',
        "chevron-down": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
        "external": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
        "eye-off": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>',
        "scale": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>',
        "sun": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
        "moon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
        "search": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
        "zap": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        "ghost": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 10h.01"/><path d="M15 10h.01"/><path d="M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"/></svg>',
        "info": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    }

    def icon(name, size=20):
        return f'<span style="display:inline-flex;width:{size}px;height:{size}px;flex-shrink:0;">{icons.get(name, "")}</span>'

    # User card helper
    def user_card(user, meta_text="", show_bio=True, index=0):
        handle_raw = user.get("handle", "") or ""
        display_name_raw = user.get("display_name") or handle_raw
        avatar_url_raw = safe_url(user.get("avatar_url", ""))
        bio_raw = user.get("bio", "") or ""
        initial = (display_name_raw[0] if display_name_raw else "?").upper()

        onerror_handler = 'this.style.display="none";this.nextElementSibling.style.display="flex"'
        img_tag = f"<img src='{esc_attr(avatar_url_raw)}' alt='' loading='lazy' onerror='{onerror_handler}'>" if avatar_url_raw else ""
        avatar_html = f'''<div class="avatar">
            {img_tag}
            <span class="avatar-fallback">{esc(initial)}</span>
        </div>'''

        bio_html = ""
        if show_bio and bio_raw:
            bio_truncated = bio_raw[:100] + ("..." if len(bio_raw) > 100 else "")
            bio_html = f'<p class="user-bio">{esc(bio_truncated)}</p>'

        meta_html = f'<span class="tag tag-muted">{esc(meta_text)}</span>' if meta_text else ""
        hidden_class = " hidden" if index >= 50 else ""
        profile_url = f"https://bsky.app/profile/{quote(handle_raw, safe='')}"

        return f'''<a href="{esc_attr(profile_url)}" target="_blank" rel="noopener" class="user-card{hidden_class}" data-handle="{esc_attr(handle_raw.lower())}">
            {avatar_html}
            <div class="user-info">
                <div class="user-name">{esc(display_name_raw)}{meta_html}</div>
                <div class="user-handle">@{esc(handle_raw)}</div>
                {bio_html}
            </div>
            {icon("external", 14)}
        </a>'''

    # Generate user lists
    def generate_user_list(users, grid_id):
        if not users:
            return '<div class="empty">No accounts found</div>'
        cards = "".join([user_card(u, "", True, i) for i, u in enumerate(users)])
        show_more = f'<button class="btn btn-text" onclick="showMore(\'{grid_id}\')">Show all {len(users)}</button>' if len(users) > 50 else ""
        return f'<div class="user-grid" id="{grid_id}">{cards}</div>{show_more}'

    mutual_html = generate_user_list(mutual_follows, "mutual-grid")
    non_mutual_html = generate_user_list(non_mutual, "non-mutual-grid")
    followers_only_html = generate_user_list(followers_only, "followers-only-grid")

    # Hidden accounts section
    hidden_section = ""
    if hidden_count > 0 or blocked_accounts:
        blocked_html = ""
        if blocked_accounts:
            blocked_items = "".join([f'<a href="https://bsky.app/profile/{quote(str(u.get("handle", "")), safe="")}" target="_blank" class="blocked-item">@{esc(u.get("handle", ""))}</a>' for u in blocked_accounts[:10]])
            blocked_html = f'<div class="subsection"><h4>Blocked by you ({len(blocked_accounts)})</h4><div class="blocked-list">{blocked_items}</div></div>'

        suspected = hidden_current.get("suspected_blocks_or_suspensions", 0)
        suspected_html = f'<div class="subsection muted"><div class="info-row">{icon("info", 16)}<span>{suspected} accounts unavailable</span></div><p class="info-text">May have blocked you, deactivated, or been suspended.</p></div>' if suspected > 0 else ""

        hidden_section = f'''
        <section class="card" id="hidden-section">
            <div class="card-header" onclick="toggleSection('hidden-section')">
                <div class="card-title">{icon("eye-off", 18)}<span>Hidden Accounts</span></div>
                <div class="card-meta"><span class="badge">{hidden_count}</span>{icon("chevron-down", 18)}</div>
            </div>
            <div class="card-body">
                <div class="hidden-stats">
                    <div class="stat-mini"><span class="stat-mini-value">{hidden_current.get('profile_followers', 0)}</span><span class="stat-mini-label">Profile</span></div>
                    <span class="stat-divider">−</span>
                    <div class="stat-mini"><span class="stat-mini-value">{hidden_current.get('api_followers', 0)}</span><span class="stat-mini-label">API</span></div>
                    <span class="stat-divider">=</span>
                    <div class="stat-mini highlight"><span class="stat-mini-value">{hidden_count}</span><span class="stat-mini-label">Hidden</span></div>
                </div>
                {blocked_html}{suspected_html}
            </div>
        </section>'''

    page_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bluesky Analytics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --transition: 150ms ease;
        }}

        [data-theme="light"] {{
            --bg-0: #ffffff;
            --bg-1: #f9fafb;
            --bg-2: #f3f4f6;
            --bg-3: #e5e7eb;
            --border: #e5e7eb;
            --border-hover: #d1d5db;
            --text-0: #111827;
            --text-1: #374151;
            --text-2: #6b7280;
            --text-3: #9ca3af;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --accent-bg: #eff6ff;
            --success: #059669;
            --success-bg: #ecfdf5;
            --error: #dc2626;
            --error-bg: #fef2f2;
            --warning: #d97706;
            --warning-bg: #fffbeb;
        }}

        [data-theme="dark"] {{
            --bg-0: #0f0f0f;
            --bg-1: #171717;
            --bg-2: #1f1f1f;
            --bg-3: #2a2a2a;
            --border: #2a2a2a;
            --border-hover: #3a3a3a;
            --text-0: #fafafa;
            --text-1: #e5e5e5;
            --text-2: #a3a3a3;
            --text-3: #737373;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --accent-bg: rgba(59,130,246,0.1);
            --success: #10b981;
            --success-bg: rgba(16,185,129,0.1);
            --error: #ef4444;
            --error-bg: rgba(239,68,68,0.1);
            --warning: #f59e0b;
            --warning-bg: rgba(245,158,11,0.1);
        }}

        html {{ font-size: 14px; }}
        body {{
            font-family: var(--font);
            background: var(--bg-1);
            color: var(--text-0);
            line-height: 1.5;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}

        .app {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
        @media (max-width: 640px) {{ .app {{ padding: 16px; }} }}

        /* Header */
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 24px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
        }}
        .header-left {{ display: flex; align-items: center; gap: 12px; }}
        .header-avatar {{
            width: 40px; height: 40px;
            border-radius: 50%;
            background: var(--accent);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 600; font-size: 16px;
            overflow: hidden; flex-shrink: 0;
        }}
        .header-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
        .header-title {{ font-size: 18px; font-weight: 600; }}
        .header-handle {{ font-size: 13px; color: var(--text-2); }}
        .header-right {{ display: flex; align-items: center; gap: 8px; }}
        .header-meta {{ font-size: 12px; color: var(--text-3); margin-right: 8px; }}

        /* Buttons */
        .btn {{
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 14px;
            font-family: var(--font); font-size: 13px; font-weight: 500;
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            background: var(--bg-0);
            color: var(--text-1);
            cursor: pointer;
            transition: all var(--transition);
        }}
        .btn:hover {{ background: var(--bg-2); border-color: var(--border-hover); }}
        .btn-primary {{ background: var(--accent); border-color: var(--accent); color: white; }}
        .btn-primary:hover {{ background: var(--accent-hover); border-color: var(--accent-hover); }}
        .btn-icon {{ padding: 8px; }}
        .btn-text {{ background: transparent; border: none; color: var(--accent); padding: 8px 12px; }}
        .btn-text:hover {{ background: var(--accent-bg); }}
        .btn.loading svg {{ animation: spin 1s linear infinite; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

        /* Stats Grid */
        .stats {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }}
        @media (max-width: 900px) {{ .stats {{ grid-template-columns: repeat(3, 1fr); }} }}
        @media (max-width: 600px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}

        .stat {{
            background: var(--bg-0);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 16px;
        }}
        .stat-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
        .stat-label {{ font-size: 12px; font-weight: 500; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-icon {{ color: var(--text-3); }}
        .stat-value {{ font-size: 28px; font-weight: 700; display: flex; align-items: baseline; gap: 8px; }}
        .stat-change {{ font-size: 12px; font-weight: 600; padding: 2px 6px; border-radius: 4px; }}
        .stat-change.up {{ background: var(--success-bg); color: var(--success); }}
        .stat-change.down {{ background: var(--error-bg); color: var(--error); }}
        .stat-footer {{ font-size: 11px; color: var(--text-3); margin-top: 4px; }}

        /* Time Filter */
        .time-filter {{
            display: flex; align-items: center; justify-content: center; gap: 4px;
            padding: 12px; margin-bottom: 24px;
            background: var(--bg-0);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
        }}
        .time-filter-label {{ font-size: 12px; color: var(--text-2); margin-right: 8px; }}
        .time-btn {{
            padding: 6px 12px; font-size: 12px; font-weight: 500;
            background: transparent; border: none; border-radius: var(--radius-sm);
            color: var(--text-2); cursor: pointer; transition: all var(--transition);
        }}
        .time-btn:hover {{ color: var(--text-0); background: var(--bg-2); }}
        .time-btn.active {{ color: var(--accent); background: var(--accent-bg); }}

        /* Cards */
        .card {{
            background: var(--bg-0);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            margin-bottom: 16px;
            overflow: hidden;
        }}
        .card-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px; cursor: pointer;
            transition: background var(--transition);
        }}
        .card-header:hover {{ background: var(--bg-2); }}
        .card-title {{ display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 14px; }}
        .card-meta {{ display: flex; align-items: center; gap: 10px; color: var(--text-2); }}
        .card-meta svg {{ transition: transform var(--transition); }}
        .card.collapsed .card-meta svg {{ transform: rotate(-90deg); }}
        .card-body {{ padding: 0 16px 16px; }}
        .card.collapsed .card-body {{ display: none; }}

        /* Badge */
        .badge {{
            display: inline-flex; align-items: center; justify-content: center;
            min-width: 22px; height: 22px; padding: 0 8px;
            font-size: 12px; font-weight: 600;
            background: var(--bg-2); border-radius: 100px;
        }}
        .badge-accent {{ background: var(--accent-bg); color: var(--accent); }}
        .badge-success {{ background: var(--success-bg); color: var(--success); }}
        .badge-error {{ background: var(--error-bg); color: var(--error); }}

        /* Charts */
        .charts {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 16px; }}
        @media (max-width: 800px) {{ .charts {{ grid-template-columns: 1fr; }} }}
        .chart-card {{
            background: var(--bg-0);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 16px;
        }}
        .chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        .chart-title {{ font-size: 13px; font-weight: 600; }}
        .chart-container {{ height: 240px; }}

        /* Mini Stats */
        .mini-stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
        @media (max-width: 640px) {{ .mini-stats {{ grid-template-columns: repeat(2, 1fr); }} }}
        .mini-stat {{ background: var(--bg-2); border-radius: var(--radius-md); padding: 12px; text-align: center; }}
        .mini-stat-value {{ font-size: 20px; font-weight: 700; }}
        .mini-stat-label {{ font-size: 10px; color: var(--text-2); text-transform: uppercase; margin-top: 2px; }}

        /* User Grid */
        .user-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; }}
        .user-card {{
            display: flex; align-items: flex-start; gap: 10px;
            padding: 12px; border-radius: var(--radius-md);
            background: var(--bg-2);
            text-decoration: none; color: inherit;
            transition: all var(--transition);
        }}
        .user-card:hover {{ background: var(--bg-3); }}
        .user-card.hidden {{ display: none; }}
        .avatar {{
            width: 36px; height: 36px; border-radius: 50%;
            background: var(--accent); flex-shrink: 0;
            overflow: hidden; position: relative;
        }}
        .avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
        .avatar-fallback {{
            position: absolute; inset: 0;
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 600; font-size: 14px;
        }}
        .avatar img + .avatar-fallback {{ display: none; }}
        .user-info {{ flex: 1; min-width: 0; }}
        .user-name {{ font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }}
        .user-handle {{ font-size: 12px; color: var(--text-2); }}
        .user-bio {{ font-size: 11px; color: var(--text-3); margin-top: 4px; line-height: 1.4; }}
        .user-card > span:last-child {{ color: var(--text-3); opacity: 0; transition: opacity var(--transition); }}
        .user-card:hover > span:last-child {{ opacity: 1; }}

        /* Tags */
        .tag {{ font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }}
        .tag-muted {{ background: var(--error-bg); color: var(--error); }}

        /* Search */
        .search {{ position: relative; margin-bottom: 12px; }}
        .search input {{
            width: 100%; padding: 10px 12px 10px 36px;
            font-family: var(--font); font-size: 13px;
            background: var(--bg-2); border: 1px solid var(--border);
            border-radius: var(--radius-md); color: var(--text-0);
            outline: none; transition: border-color var(--transition);
        }}
        .search input:focus {{ border-color: var(--accent); }}
        .search input::placeholder {{ color: var(--text-3); }}
        .search > span {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-3); }}

        /* Hidden Stats */
        .hidden-stats {{
            display: flex; align-items: center; justify-content: center; gap: 16px;
            padding: 16px; background: var(--bg-2); border-radius: var(--radius-md);
        }}
        .stat-mini {{ text-align: center; }}
        .stat-mini-value {{ font-size: 24px; font-weight: 700; }}
        .stat-mini-label {{ font-size: 11px; color: var(--text-2); }}
        .stat-mini.highlight .stat-mini-value {{ color: var(--warning); }}
        .stat-divider {{ font-size: 20px; color: var(--text-3); }}

        .subsection {{ margin-top: 16px; }}
        .subsection h4 {{ font-size: 12px; font-weight: 600; color: var(--text-2); margin-bottom: 8px; }}
        .blocked-list {{ display: flex; flex-wrap: wrap; gap: 6px; }}
        .blocked-item {{
            padding: 4px 10px; font-size: 12px;
            background: var(--bg-2); border-radius: 100px;
            color: var(--text-1); text-decoration: none;
            transition: background var(--transition);
        }}
        .blocked-item:hover {{ background: var(--bg-3); }}
        .subsection.muted {{ padding: 12px; background: var(--warning-bg); border-radius: var(--radius-md); }}
        .info-row {{ display: flex; align-items: center; gap: 6px; font-weight: 600; color: var(--warning); }}
        .info-text {{ font-size: 12px; color: var(--text-2); margin-top: 4px; }}

        /* Balance */
        .balance {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 24px; align-items: center; }}
        @media (max-width: 640px) {{ .balance {{ grid-template-columns: 1fr; gap: 16px; }} }}
        .balance-col {{ background: var(--bg-2); border-radius: var(--radius-md); padding: 16px; }}
        .balance-col h4 {{ font-size: 12px; font-weight: 600; text-align: center; margin-bottom: 12px; }}
        .balance-col.given h4 {{ color: var(--success); }}
        .balance-col.received h4 {{ color: var(--accent); }}
        .balance-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; }}
        .balance-value {{ font-size: 20px; font-weight: 700; }}
        .balance-col.given .balance-value {{ color: var(--success); }}
        .balance-col.received .balance-value {{ color: var(--accent); }}
        .balance-label {{ font-size: 10px; color: var(--text-2); }}
        .balance-total {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); text-align: center; }}
        .balance-indicator {{ text-align: center; }}
        .ratio-circle {{
            width: 72px; height: 72px; margin: 0 auto;
            border-radius: 50%; background: var(--bg-2);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }}
        .ratio-value {{ font-size: 20px; font-weight: 700; color: var(--accent); }}
        .ratio-label {{ font-size: 10px; color: var(--text-2); }}
        .balance-type {{ font-size: 11px; color: var(--text-2); margin-top: 6px; }}

        /* Posts */
        .post {{
            padding: 12px; margin-bottom: 8px;
            background: var(--bg-2); border-radius: var(--radius-md);
            cursor: pointer; transition: background var(--transition);
        }}
        .post:hover {{ background: var(--bg-3); }}
        .post-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
        .post-avatar {{ width: 32px; height: 32px; border-radius: 50%; background: var(--accent); overflow: hidden; }}
        .post-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
        .post-author {{ font-size: 13px; font-weight: 600; flex: 1; }}
        .post-date {{ font-size: 11px; color: var(--text-3); }}
        .post-text {{ font-size: 13px; line-height: 1.5; margin-bottom: 10px; white-space: pre-wrap; word-break: break-word; }}
        .post-stats {{ display: flex; gap: 16px; padding-top: 10px; border-top: 1px solid var(--border); }}
        .post-stat {{ display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-2); }}
        .post-stat svg {{ width: 14px; height: 14px; }}
        .post-score {{ margin-left: auto; font-weight: 600; color: var(--accent); display: flex; align-items: center; gap: 4px; }}

        /* Empty */
        .empty {{ text-align: center; padding: 32px; color: var(--text-3); font-size: 13px; }}

        /* Toast */
        .toast-container {{ position: fixed; bottom: 24px; right: 24px; z-index: 1000; }}
        .toast {{
            display: flex; align-items: center; gap: 10px;
            padding: 12px 16px; margin-top: 8px;
            background: var(--bg-0); border: 1px solid var(--border);
            border-radius: var(--radius-md); box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            animation: toast-in 0.2s ease;
        }}
        @keyframes toast-in {{ from {{ opacity: 0; transform: translateY(8px); }} }}
        .toast-icon {{ flex-shrink: 0; }}
        .toast-icon.success {{ color: var(--success); }}
        .toast-icon.error {{ color: var(--error); }}
        .toast-title {{ font-size: 13px; font-weight: 600; }}
        .toast-close {{ cursor: pointer; color: var(--text-3); padding: 4px; }}

        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-3); }}
    </style>
</head>
<body>
    <div class="app">
        <header class="header">
            <div class="header-left">
                <div class="header-avatar" id="header-avatar">{esc((bluesky_handle[0] if bluesky_handle else "?").upper())}</div>
                <div>
                    <div class="header-title">Bluesky Analytics</div>
                    <div class="header-handle">@{esc(bluesky_handle)}</div>
                </div>
            </div>
            <div class="header-right">
                <span class="header-meta">Updated: <span id="last-updated">{esc(last_updated)}</span></span>
                <button class="btn" id="refresh-btn" onclick="refreshData()">{icon("refresh", 14)}<span>Refresh</span></button>
                <button class="btn btn-icon" onclick="toggleTheme()" title="Toggle theme"><span class="theme-icon">{icon("sun", 16)}</span></button>
            </div>
        </header>

        <div class="stats">
            <div class="stat">
                <div class="stat-header"><span class="stat-label">Followers</span><span class="stat-icon">{icon("users", 16)}</span></div>
                <div class="stat-value">{stats.get('follower_count', 0)}{f'<span class="stat-change up">+{follower_change}</span>' if follower_change > 0 else f'<span class="stat-change down">{follower_change}</span>' if follower_change < 0 else ''}</div>
                <div class="stat-footer">Total followers</div>
            </div>
            <div class="stat">
                <div class="stat-header"><span class="stat-label">Following</span><span class="stat-icon">{icon("user-plus", 16)}</span></div>
                <div class="stat-value">{stats.get('following_count', 0)}</div>
                <div class="stat-footer">Accounts you follow</div>
            </div>
            <div class="stat">
                <div class="stat-header"><span class="stat-label">Mutuals</span><span class="stat-icon">{icon("handshake", 16)}</span></div>
                <div class="stat-value">{len(mutual_follows)}</div>
                <div class="stat-footer">Follow each other</div>
            </div>
            <div class="stat">
                <div class="stat-header"><span class="stat-label">Non-Mutuals</span><span class="stat-icon">{icon("ghost", 16)}</span></div>
                <div class="stat-value">{stats.get('non_mutual_following', 0)}</div>
                <div class="stat-footer">Don't follow back</div>
            </div>
            <div class="stat">
                <div class="stat-header"><span class="stat-label">Fans</span><span class="stat-icon">{icon("star", 16)}</span></div>
                <div class="stat-value">{len(followers_only)}</div>
                <div class="stat-footer">You don't follow back</div>
            </div>
        </div>

        <div class="time-filter">
            <span class="time-filter-label">Period:</span>
            <button class="time-btn" data-days="1" onclick="changeTimeRange(1)">24h</button>
            <button class="time-btn" data-days="7" onclick="changeTimeRange(7)">7d</button>
            <button class="time-btn active" data-days="30" onclick="changeTimeRange(30)">30d</button>
            <button class="time-btn" data-days="90" onclick="changeTimeRange(90)">90d</button>
            <button class="time-btn" data-days="365" onclick="changeTimeRange(365)">1y</button>
            <button class="time-btn" data-days="999999" onclick="changeTimeRange(999999)">All</button>
        </div>

        <section class="card" id="balance-section">
            <div class="card-header" onclick="toggleSection('balance-section')">
                <div class="card-title">{icon("scale", 16)}<span>Engagement Balance</span></div>
                <div class="card-meta">{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body">
                <div class="balance">
                    <div class="balance-col given">
                        <h4>Given</h4>
                        <div class="balance-stats">
                            <div><div class="balance-value" id="given-likes">-</div><div class="balance-label">Likes</div></div>
                            <div><div class="balance-value" id="given-reposts">-</div><div class="balance-label">Reposts</div></div>
                            <div><div class="balance-value" id="given-replies">-</div><div class="balance-label">Replies</div></div>
                        </div>
                        <div class="balance-total"><span id="given-total" style="font-size:16px;font-weight:700;color:var(--success);">-</span></div>
                    </div>
                    <div class="balance-indicator">
                        <div class="ratio-circle"><span class="ratio-value" id="balance-ratio">-</span><span class="ratio-label">ratio</span></div>
                        <div class="balance-type" id="balance-type">Loading...</div>
                    </div>
                    <div class="balance-col received">
                        <h4>Received</h4>
                        <div class="balance-stats">
                            <div><div class="balance-value" id="received-likes">-</div><div class="balance-label">Likes</div></div>
                            <div><div class="balance-value" id="received-reposts">-</div><div class="balance-label">Reposts</div></div>
                            <div><div class="balance-value" id="received-replies">-</div><div class="balance-label">Replies</div></div>
                        </div>
                        <div class="balance-total"><span id="received-total" style="font-size:16px;font-weight:700;color:var(--accent);">-</span></div>
                    </div>
                </div>
            </div>
        </section>

        <section class="card" id="analytics-section">
            <div class="card-header" onclick="toggleSection('analytics-section')">
                <div class="card-title">{icon("activity", 16)}<span>Analytics</span></div>
                <div class="card-meta"><span class="badge" id="analytics-badge">30d</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body">
                <div class="mini-stats">
                    <div class="mini-stat"><div class="mini-stat-value" id="stat-days">-</div><div class="mini-stat-label">Days</div></div>
                    <div class="mini-stat"><div class="mini-stat-value" id="stat-change">-</div><div class="mini-stat-label">Net followers</div></div>
                    <div class="mini-stat"><div class="mini-stat-value" id="stat-posts">-</div><div class="mini-stat-label">Posts</div></div>
                    <div class="mini-stat"><div class="mini-stat-value" id="stat-engagement">-</div><div class="mini-stat-label">Avg engagement</div></div>
                </div>
                <div class="charts">
                    <div class="chart-card"><div class="chart-header"><span class="chart-title">Network Growth</span></div><div class="chart-container"><canvas id="growthChart"></canvas></div></div>
                    <div class="chart-card"><div class="chart-header"><span class="chart-title">Engagement</span><button class="btn btn-text" id="engToggle" onclick="toggleEngView()" style="padding:4px 8px;font-size:11px;">Daily</button></div><div class="chart-container"><canvas id="engChart"></canvas></div></div>
                    <div class="chart-card"><div class="chart-header"><span class="chart-title">Posts</span></div><div class="chart-container"><canvas id="postsChart"></canvas></div></div>
                    <div class="chart-card"><div class="chart-header"><span class="chart-title">Breakdown</span></div><div class="chart-container"><canvas id="breakdownChart"></canvas></div></div>
                </div>
            </div>
        </section>

        <section class="card" id="posts-section">
            <div class="card-header" onclick="toggleSection('posts-section')">
                <div class="card-title">{icon("zap", 16)}<span>Top Posts</span></div>
                <div class="card-meta"><span class="badge badge-accent" id="posts-count">-</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body" id="posts-container"><div class="empty">Loading...</div></div>
        </section>

        <section class="card collapsed" id="unfollowers-section">
            <div class="card-header" onclick="toggleSection('unfollowers-section')">
                <div class="card-title">{icon("user-minus", 16)}<span>Unfollowers</span></div>
                <div class="card-meta"><span class="badge badge-error" id="unfollowers-count">-</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body" id="unfollowers-container"><div class="empty">Loading...</div></div>
        </section>

        <section class="card collapsed" id="interactors-section">
            <div class="card-header" onclick="toggleSection('interactors-section')">
                <div class="card-title">{icon("heart", 16)}<span>Top Interactors</span></div>
                <div class="card-meta"><span class="badge badge-success" id="interactors-count">-</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body" id="interactors-container"><div class="empty">Loading...</div></div>
        </section>

        {hidden_section}

        <section class="card collapsed" id="mutuals-section">
            <div class="card-header" onclick="toggleSection('mutuals-section')">
                <div class="card-title">{icon("handshake", 16)}<span>Mutual Follows</span></div>
                <div class="card-meta"><span class="badge badge-success">{len(mutual_follows)}</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body">
                <div class="search"><span>{icon("search", 14)}</span><input type="text" placeholder="Search..." onkeyup="filterUsers('mutual-grid',this.value)"></div>
                {mutual_html}
            </div>
        </section>

        <section class="card collapsed" id="nonmutuals-section">
            <div class="card-header" onclick="toggleSection('nonmutuals-section')">
                <div class="card-title">{icon("ghost", 16)}<span>Non-Mutuals</span></div>
                <div class="card-meta"><span class="badge">{len(non_mutual)}</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body">
                <div class="search"><span>{icon("search", 14)}</span><input type="text" placeholder="Search..." onkeyup="filterUsers('non-mutual-grid',this.value)"></div>
                {non_mutual_html}
            </div>
        </section>

        <section class="card collapsed" id="fans-section">
            <div class="card-header" onclick="toggleSection('fans-section')">
                <div class="card-title">{icon("star", 16)}<span>Fans</span></div>
                <div class="card-meta"><span class="badge">{len(followers_only)}</span>{icon("chevron-down", 16)}</div>
            </div>
            <div class="card-body">
                <div class="search"><span>{icon("search", 14)}</span><input type="text" placeholder="Search..." onkeyup="filterUsers('followers-only-grid',this.value)"></div>
                {followers_only_html}
            </div>
        </section>
    </div>

    <div class="toast-container" id="toasts"></div>

    <script>
        const handle = {bluesky_handle_js};
        let timeRange = 30, charts = {{}}, engData = {{daily:null,cumulative:null,view:'cumulative'}}, avatarUrl = null;

        // Theme
        const getTheme = () => localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
        const setTheme = t => {{ document.documentElement.dataset.theme = t; localStorage.setItem('theme', t); updateThemeIcon(); updateCharts(); }};
        const toggleTheme = () => setTheme(getTheme() === 'dark' ? 'light' : 'dark');
        const updateThemeIcon = () => {{ document.querySelector('.theme-icon').innerHTML = getTheme() === 'dark' ? '{icon("sun", 16)}' : '{icon("moon", 16)}'; }};
        setTheme(getTheme());

        // Utils
        const esc = s => String(s??'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);
        const fmt = n => n >= 1e6 ? (n/1e6).toFixed(1)+'M' : n >= 1e3 ? (n/1e3).toFixed(1)+'K' : n;
        const timeLabel = d => d===1?'24h':d===7?'7d':d===30?'30d':d===90?'90d':d===365?'1y':'All';
        const fmtDate = s => {{ try {{ return new Date(s).toLocaleDateString('en-US',{{month:'short',day:'numeric'}}); }} catch {{ return s; }} }};

        // Toast
        const toast = (title, type='info') => {{
            const t = document.createElement('div');
            t.className = 'toast';
            t.innerHTML = `<span class="toast-icon ${{type}}" style="width:16px;height:16px;">${{type==='success'?'{icon("trending-up",16)}':'{icon("info",16)}'}}</span><span class="toast-title">${{esc(title)}}</span><span class="toast-close" onclick="this.parentElement.remove()" style="width:14px;height:14px;">{icon("user-x",14)}</span>`;
            document.getElementById('toasts').appendChild(t);
            setTimeout(() => t.remove(), 4000);
        }};

        // Sections
        const toggleSection = id => document.getElementById(id).classList.toggle('collapsed');
        const showMore = gid => {{ document.querySelectorAll(`#${{gid}} .hidden`).forEach(c => c.classList.remove('hidden')); }};
        const filterUsers = (gid, q) => {{
            const grid = document.getElementById(gid);
            if (!grid) return;
            q = q.toLowerCase();
            grid.querySelectorAll('.user-card').forEach(c => {{
                const h = c.dataset.handle || '';
                c.style.display = h.includes(q) ? '' : 'none';
            }});
        }};

        // Time range
        const changeTimeRange = d => {{
            timeRange = d;
            document.querySelectorAll('.time-btn').forEach(b => b.classList.toggle('active', +b.dataset.days === d));
            document.getElementById('analytics-badge').textContent = timeLabel(d);
            loadAll(d);
        }};

        // Chart colors
        const colors = () => {{
            const dark = getTheme() === 'dark';
            return {{
                grid: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
                text: dark ? '#a3a3a3' : '#6b7280',
                accent: '#2563eb',
                success: '#059669',
                warning: '#d97706',
                error: '#dc2626'
            }};
        }};

        const updateCharts = () => {{
            const c = colors();
            Object.values(charts).forEach(ch => {{
                if (!ch) return;
                ['x','y'].forEach(axis => {{
                    if (ch.options.scales?.[axis]) {{
                        ch.options.scales[axis].grid.color = c.grid;
                        ch.options.scales[axis].ticks.color = c.text;
                    }}
                }});
                if (ch.options.plugins?.legend?.labels) ch.options.plugins.legend.labels.color = c.text;
                ch.update('none');
            }});
        }};

        // Data loading
        const loadAll = async d => {{
            await Promise.all([loadStats(d), loadGrowth(d), loadEng(d), loadPosts(d), loadBreakdown(d), loadTopPosts(d), loadUnfollowers(d), loadInteractors(d), loadBalance(d)]);
        }};

        const loadStats = async d => {{
            try {{
                const r = await fetch(`/api/graphs/stats-summary?days=${{d}}`);
                const data = await r.json();
                document.getElementById('stat-days').textContent = data.daysTracked || '0';
                const ch = data.followerChange || 0;
                const el = document.getElementById('stat-change');
                el.textContent = ch >= 0 ? `+${{ch}}` : ch;
                el.style.color = ch >= 0 ? 'var(--success)' : 'var(--error)';
                document.getElementById('stat-posts').textContent = data.totalPosts || '0';
                document.getElementById('stat-engagement').textContent = (data.avgEngagementPerPost || 0).toFixed(1);
            }} catch(e) {{ console.error(e); }}
        }};

        const loadGrowth = async d => {{
            try {{
                const r = await fetch(`/api/graphs/follower-growth?days=${{d}}`);
                const data = await r.json();
                const ctx = document.getElementById('growthChart').getContext('2d');
                const c = colors();
                if (charts.growth) charts.growth.destroy();
                if (!data.dates?.length) return;
                charts.growth = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: data.dates,
                        datasets: [
                            {{ label: 'Followers', data: data.followers, borderColor: c.accent, backgroundColor: c.accent+'15', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 0 }},
                            {{ label: 'Following', data: data.following, borderColor: c.warning, backgroundColor: c.warning+'15', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 0 }}
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{ legend: {{ position: 'bottom', labels: {{ color: c.text, usePointStyle: true }} }} }},
                        scales: {{
                            x: {{ grid: {{ color: c.grid }}, ticks: {{ color: c.text }} }},
                            y: {{ grid: {{ color: c.grid }}, ticks: {{ color: c.text, precision: 0 }}, beginAtZero: false }}
                        }}
                    }}
                }});
            }} catch(e) {{ console.error(e); }}
        }};

        const loadEng = async d => {{
            try {{
                const r = await fetch(`/api/graphs/engagement-timeline?days=${{d}}`);
                const data = await r.json();
                engData.daily = data.daily;
                engData.cumulative = data.cumulative;
                renderEng();
            }} catch(e) {{ console.error(e); }}
        }};

        const toggleEngView = () => {{
            engData.view = engData.view === 'cumulative' ? 'daily' : 'cumulative';
            document.getElementById('engToggle').textContent = engData.view === 'cumulative' ? 'Daily' : 'Cumulative';
            renderEng();
        }};

        const renderEng = () => {{
            if (!engData.daily) return;
            const data = engData.view === 'cumulative' ? engData.cumulative : engData.daily;
            const ctx = document.getElementById('engChart').getContext('2d');
            const c = colors();
            const isCum = engData.view === 'cumulative';
            if (charts.eng) charts.eng.destroy();
            if (!data?.dates?.length) return;
            charts.eng = new Chart(ctx, {{
                type: isCum ? 'line' : 'bar',
                data: {{
                    labels: data.dates,
                    datasets: [
                        {{ label: 'Likes', data: data.likes, borderColor: '#ec4899', backgroundColor: isCum ? '#ec489915' : '#ec4899cc', borderWidth: 2, fill: isCum, tension: 0.4, pointRadius: 0 }},
                        {{ label: 'Reposts', data: data.reposts, borderColor: c.success, backgroundColor: isCum ? c.success+'15' : c.success+'cc', borderWidth: 2, fill: isCum, tension: 0.4, pointRadius: 0 }},
                        {{ label: 'Replies', data: data.replies, borderColor: c.accent, backgroundColor: isCum ? c.accent+'15' : c.accent+'cc', borderWidth: 2, fill: isCum, tension: 0.4, pointRadius: 0 }}
                    ]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ color: c.text, usePointStyle: true }} }} }},
                    scales: {{
                        x: {{ grid: {{ color: c.grid }}, ticks: {{ color: c.text }}, stacked: !isCum }},
                        y: {{ grid: {{ color: c.grid }}, ticks: {{ color: c.text, precision: 0 }}, beginAtZero: true, stacked: !isCum }}
                    }}
                }}
            }});
        }};

        const loadPosts = async d => {{
            try {{
                const r = await fetch(`/api/graphs/posting-frequency?days=${{d}}`);
                const data = await r.json();
                const ctx = document.getElementById('postsChart').getContext('2d');
                const c = colors();
                if (charts.posts) charts.posts.destroy();
                if (!data.dates?.length) return;
                charts.posts = new Chart(ctx, {{
                    type: 'bar',
                    data: {{ labels: data.dates, datasets: [{{ label: 'Posts', data: data.posts, backgroundColor: c.warning+'cc', borderRadius: 4 }}] }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ grid: {{ display: false }}, ticks: {{ color: c.text }} }},
                            y: {{ grid: {{ color: c.grid }}, ticks: {{ color: c.text, precision: 0 }}, beginAtZero: true }}
                        }}
                    }}
                }});
            }} catch(e) {{ console.error(e); }}
        }};

        const loadBreakdown = async d => {{
            try {{
                const r = await fetch(`/api/graphs/engagement-breakdown?days=${{d}}`);
                const data = await r.json();
                const ctx = document.getElementById('breakdownChart').getContext('2d');
                const c = colors();
                if (charts.breakdown) charts.breakdown.destroy();
                if (!data.values?.some(v => v > 0)) return;
                charts.breakdown = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{ labels: data.labels, datasets: [{{ data: data.values, backgroundColor: ['#ec4899', c.success, c.accent, '#a855f7', c.warning], borderWidth: 0 }}] }},
                    options: {{
                        responsive: true, maintainAspectRatio: false, cutout: '60%',
                        plugins: {{ legend: {{ position: 'bottom', labels: {{ color: c.text, usePointStyle: true }} }} }}
                    }}
                }});
            }} catch(e) {{ console.error(e); }}
        }};

        const loadTopPosts = async d => {{
            const container = document.getElementById('posts-container');
            const badge = document.getElementById('posts-count');
            try {{
                const r = await fetch(`/api/top-posts?days=${{d}}`);
                const data = await r.json();
                badge.textContent = data.count || 0;
                if (!data.posts?.length) {{ container.innerHTML = '<div class="empty">No posts</div>'; return; }}
                let html = '';
                for (const p of data.posts.slice(0, 10)) {{
                    const score = (p.likes||0) + (p.reposts||0)*2 + (p.replies||0)*3;
                    const id = p.uri?.split('/').pop() || '';
                    const url = id ? `https://bsky.app/profile/${{encodeURIComponent(handle)}}/post/${{encodeURIComponent(id)}}` : '#';
                    html += `<div class="post" onclick="window.open('${{url}}','_blank')">
                        <div class="post-header">
                            <div class="post-avatar">${{avatarUrl ? `<img src="${{esc(avatarUrl)}}" alt="">` : ''}}</div>
                            <div class="post-author">@${{esc(handle)}}</div>
                            <div class="post-date">${{fmtDate(p.created_at)}}</div>
                        </div>
                        <div class="post-text">${{esc((p.text||'').slice(0,280))}}</div>
                        <div class="post-stats">
                            <span class="post-stat">{icon("heart",14)}${{p.likes||0}}</span>
                            <span class="post-stat">{icon("repeat",14)}${{p.reposts||0}}</span>
                            <span class="post-stat">{icon("message",14)}${{p.replies||0}}</span>
                            <span class="post-score">{icon("trending-up",14)}${{score}}</span>
                        </div>
                    </div>`;
                }}
                container.innerHTML = html;
            }} catch(e) {{ container.innerHTML = '<div class="empty">Error loading</div>'; }}
        }};

        const loadUnfollowers = async d => {{
            const container = document.getElementById('unfollowers-container');
            const badge = document.getElementById('unfollowers-count');
            try {{
                const r = await fetch(`/api/unfollowers?days=${{d}}`);
                const data = await r.json();
                badge.textContent = data.unfollowers?.length || 0;
                if (!data.unfollowers?.length) {{ container.innerHTML = '<div class="empty">No unfollowers</div>'; return; }}
                let html = '<div class="user-grid">';
                for (const u of data.unfollowers) {{
                    const h = u.handle || '';
                    html += `<a href="https://bsky.app/profile/${{encodeURIComponent(h)}}" target="_blank" class="user-card">
                        <div class="avatar"><span class="avatar-fallback">${{(h[0]||'?').toUpperCase()}}</span></div>
                        <div class="user-info"><div class="user-name">@${{esc(h)}}<span class="tag tag-muted">${{fmtDate(u.date)}}</span></div></div>
                    </a>`;
                }}
                container.innerHTML = html + '</div>';
            }} catch(e) {{ container.innerHTML = '<div class="empty">Error</div>'; }}
        }};

        const loadInteractors = async d => {{
            const container = document.getElementById('interactors-container');
            const badge = document.getElementById('interactors-count');
            try {{
                const r = await fetch(`/api/top-interactors?days=${{d}}`);
                const data = await r.json();
                badge.textContent = data.interactors?.length || 0;
                if (!data.interactors?.length) {{ container.innerHTML = '<div class="empty">No data</div>'; return; }}
                let html = '<div class="user-grid">';
                for (const u of data.interactors.slice(0, 20)) {{
                    const h = u.handle || '';
                    const n = u.display_name || h;
                    const a = u.avatar || '';
                    html += `<a href="https://bsky.app/profile/${{encodeURIComponent(h)}}" target="_blank" class="user-card">
                        <div class="avatar">${{a ? `<img src="${{esc(a)}}" alt="" onerror="this.style.display='none'">` : ''}}<span class="avatar-fallback">${{(n[0]||'?').toUpperCase()}}</span></div>
                        <div class="user-info"><div class="user-name">${{esc(n)}}</div><div class="user-handle">@${{esc(h)}}</div></div>
                        <span class="badge badge-success">${{u.total_score||0}}</span>
                    </a>`;
                }}
                container.innerHTML = html + '</div>';
            }} catch(e) {{ container.innerHTML = '<div class="empty">Error</div>'; }}
        }};

        const loadBalance = async d => {{
            try {{
                const r = await fetch(`/api/engagement-balance?days=${{d}}`);
                const data = await r.json();
                document.getElementById('given-likes').textContent = fmt(data.given?.likes || 0);
                document.getElementById('given-reposts').textContent = fmt(data.given?.reposts || 0);
                document.getElementById('given-replies').textContent = fmt(data.given?.replies || 0);
                document.getElementById('given-total').textContent = fmt(data.given?.total || 0);
                document.getElementById('received-likes').textContent = fmt(data.received?.likes || 0);
                document.getElementById('received-reposts').textContent = fmt(data.received?.reposts || 0);
                document.getElementById('received-replies').textContent = fmt(data.received?.replies || 0);
                document.getElementById('received-total').textContent = fmt(data.received?.total || 0);
                const ratio = data.ratio || 0;
                document.getElementById('balance-ratio').textContent = ratio.toFixed(2);
                document.getElementById('balance-type').textContent = ratio > 1 ? 'Giver' : ratio < 1 ? 'Receiver' : 'Balanced';
            }} catch(e) {{ console.error(e); }}
        }};

        // Refresh
        const refreshData = async () => {{
            const btn = document.getElementById('refresh-btn');
            btn.classList.add('loading');
            btn.disabled = true;
            try {{
                const r = await fetch('/api/collect', {{ method: 'POST' }});
                const data = await r.json();
                if (data.success) {{
                    toast('Data refreshed', 'success');
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    toast('Refresh failed', 'error');
                }}
            }} catch(e) {{
                toast('Network error', 'error');
            }} finally {{
                btn.classList.remove('loading');
                btn.disabled = false;
            }}
        }};

        // Avatar
        const loadAvatar = async () => {{
            try {{
                const r = await fetch(`https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=${{encodeURIComponent(handle)}}`);
                const data = await r.json();
                avatarUrl = data.avatar || null;
                if (avatarUrl) {{
                    document.getElementById('header-avatar').innerHTML = `<img src="${{esc(avatarUrl)}}" alt="">`;
                }}
            }} catch(e) {{}}
        }};

        // Keyboard shortcuts
        document.addEventListener('keydown', e => {{
            if (e.target.tagName === 'INPUT') return;
            if (e.key === 'r' && !e.metaKey && !e.ctrlKey) {{ e.preventDefault(); refreshData(); }}
            if (e.key === 't') {{ e.preventDefault(); toggleTheme(); }}
            if (e.key >= '1' && e.key <= '5') {{ e.preventDefault(); changeTimeRange([1,7,30,90,365][e.key-1]); }}
        }});

        // Init
        const init = () => {{
            loadAvatar();
            if (typeof Chart !== 'undefined') loadAll(timeRange);
            else setTimeout(init, 100);
        }};
        document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
    </script>
</body>
</html>'''

    return page_html
