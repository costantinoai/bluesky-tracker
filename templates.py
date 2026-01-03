"""
Modern Material Design 3 HTML templates for Bluesky Tracker with Expandable Lists
"""


def get_report_html(data):
    """Generate modern Material Design 3 report page with expandable user lists"""

    # Extract data
    stats = data.get("stats", {})
    unfollowers = data.get("unfollowers", [])
    non_mutual = data.get("non_mutual", [])
    followers_only = data.get("followers_only", [])
    mutual_follows = data.get("mutual_follows", [])
    hidden_analytics = data.get("hidden_analytics", {})
    hidden_categories = data.get("hidden_categories", {})
    change_history = data.get("change_history", [])
    top_posts = data.get("top_posts", [])
    advanced_metrics = data.get("advanced_metrics", {})
    top_interactors = data.get("top_interactors", [])
    last_updated = data.get("last_updated", "Never")
    bluesky_handle = data.get("bluesky_handle", "your-handle.bsky.social")
    auth_enabled = data.get("auth_enabled", True)  # For showing auth status

    # Helper function for user cards with hiding capability
    def user_card(user, meta_text="", show_bio=True, index=0):
        handle = user.get("handle", "")
        display_name = user.get("display_name", handle)
        avatar_url = user.get("avatar_url", "")
        bio = user.get("bio", "")

        avatar_html = ""
        if avatar_url and avatar_url.strip():
            avatar_html = f'<div class="user-avatar"><img src="{avatar_url}" alt="{display_name}" onerror="this.style.display=\'none\'"></div>'

        bio_html = ""
        if show_bio and bio:
            bio_truncated = bio[:120] + ("..." if len(bio) > 120 else "")
            bio_html = f'<p class="user-bio">{bio_truncated}</p>'

        meta_html = f'<span class="user-meta">{meta_text}</span>' if meta_text else ""
        hidden_class = " hidden-card" if index >= 50 else ""

        profile_url = f"https://bsky.app/profile/{handle}"

        return f"""<div class="user-card{hidden_class}" onclick="window.open('{profile_url}', '_blank')">
            {avatar_html}
            <div class="user-content">
                <div class="user-header">
                    <h4 class="user-name">{display_name}</h4>
                    {meta_html}
                </div>
                <p class="user-handle">@{handle}</p>
                {bio_html}
            </div>
            <div class="user-action">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                </svg>
            </div>
        </div>"""

    # HTML with embedded CSS
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bluesky Analytics - Modern Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        :root {{
            --md-primary: #1976D2; --md-primary-container: #BBDEFB; --md-on-primary: #FFFFFF;
            --md-secondary: #0288D1; --md-secondary-container: #B3E5FC;
            --md-tertiary: #0097A7; --md-success: #00897B; --md-success-container: #B2DFDB;
            --md-error: #D32F2F; --md-error-container: #FFCDD2;
            --md-surface: #FEF7FF; --md-surface-variant: #E7E0EC;
            --md-on-surface: #1C1B1F; --md-on-surface-variant: #49454F;
            --md-outline: #79747E; --md-outline-variant: #CAC4D0;
            --md-elevation-1: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
            --md-elevation-2: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
            --md-elevation-3: 0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3);
        }}

        .material-icons {{ font-family: 'Material Icons'; font-weight: normal; font-style: normal;
                          font-size: 24px; display: inline-block; line-height: 1; text-transform: none;
                          letter-spacing: normal; word-wrap: normal; white-space: nowrap; direction: ltr; }}
        .section-icon .material-icons {{ font-size: 28px; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #E3F2FD;
               color: var(--md-on-surface); line-height: 1.6; min-height: 100vh; padding: 24px; }}
        .container {{ max-width: 1200px; margin: 0 auto; animation: fadeIn 0.6s ease-out; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .header {{ background: white; border-radius: 28px; padding: 32px; margin-bottom: 24px;
                   box-shadow: var(--md-elevation-2); position: relative; overflow: hidden; }}
        .header::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 6px;
                          background: #1e88e5; }}
        .header-content {{ display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }}
        .header-left {{ display: flex; align-items: center; gap: 16px; }}
        .avatar-large {{ width: 64px; height: 64px; border-radius: 50%;
                         background: transparent;
                         display: flex; align-items: center; justify-content: center; color: white;
                         font-size: 28px; font-weight: 600; box-shadow: var(--md-elevation-2); }}
        .header-text h1 {{ font-size: 28px; font-weight: 700; color: var(--md-on-surface); margin-bottom: 4px; }}
        .header-text p {{ color: var(--md-on-surface-variant); font-size: 14px; }}
        .auth-badge {{ display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px;
                       border-radius: 28px; font-size: 13px; font-weight: 500;
                       background: var(--md-success-container); color: var(--md-success); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 24px; }}
        @media (max-width: 1200px) {{ .stats-grid {{ grid-template-columns: repeat(5, 1fr); }} }}
        @media (max-width: 900px) {{ .stats-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
        @media (max-width: 600px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        .stat-card {{ background: white; border-radius: 16px; padding: 24px; box-shadow: var(--md-elevation-1);
                      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; cursor: pointer; }}
        .stat-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
                             background: var(--card-color, var(--md-primary));
                             transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .stat-card:hover {{ transform: translateY(-4px); box-shadow: var(--md-elevation-3); }}
        .stat-card:hover::before {{ height: 6px; }}
        .stat-card.primary {{ --card-color: var(--md-primary); }}
        .stat-card.secondary {{ --card-color: var(--md-secondary); }}
        .stat-card.tertiary {{ --card-color: var(--md-tertiary); }}
        .stat-card.success {{ --card-color: var(--md-success); }}
        .stat-card.error {{ --card-color: var(--md-error); }}
        .stat-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
        .stat-label {{ font-size: 13px; font-weight: 500; color: var(--md-on-surface-variant);
                       text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-icon {{ font-size: 24px; }}
        .stat-value {{ font-size: 36px; font-weight: 700; color: var(--md-on-surface); line-height: 1; }}
        .stat-change {{ font-size: 13px; color: var(--md-on-surface-variant); margin-top: 4px; }}
        .section-card {{ background: white; border-radius: 16px; margin-bottom: 16px;
                         box-shadow: var(--md-elevation-1); overflow: hidden; transition: box-shadow 0.3s ease; }}
        .section-card:hover {{ box-shadow: var(--md-elevation-2); }}
        .section-header {{ padding: 24px; cursor: pointer; user-select: none; display: flex;
                          align-items: center; justify-content: space-between; transition: background 0.2s ease; }}
        .section-header:hover {{ background: var(--md-surface-variant); }}
        .section-title {{ display: flex; align-items: center; gap: 16px; flex: 1; }}
        .section-icon {{ font-size: 32px; width: 48px; height: 48px; display: flex; align-items: center;
                        justify-content: center; color: #1976D2; }}
        .section-text h3 {{ font-size: 20px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 4px; }}
        .section-text p {{ font-size: 14px; color: var(--md-on-surface-variant); }}
        .section-badge {{ display: inline-flex; align-items: center; justify-content: center; min-width: 32px;
                         height: 32px; padding: 0 12px; background: var(--md-primary); color: var(--md-on-primary);
                         border-radius: 28px; font-size: 14px; font-weight: 600; margin-right: 16px; }}
        .section-chevron {{ width: 24px; height: 24px; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .section-chevron.expanded {{ transform: rotate(180deg); }}
        .section-content {{ max-height: 0; overflow: hidden; transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}
        .section-content.expanded {{ max-height: 50000px; }}
        .section-body {{ padding: 0 24px 24px; }}
        .user-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
        .user-card {{ background: var(--md-surface); border: 1px solid var(--md-outline-variant);
                      border-radius: 12px; padding: 16px; display: flex; gap: 16px;
                      transition: all 0.2s ease; cursor: pointer; }}
        .user-card.hidden-card {{ display: none; }}
        .user-card:hover {{ border-color: var(--md-primary); background: var(--md-primary-container);
                           transform: translateX(4px); }}
        .user-avatar img {{ width: 56px; height: 56px; border-radius: 50%; object-fit: cover;
                           border: 2px solid var(--md-outline-variant); }}
        .user-content {{ flex: 1; min-width: 0; }}
        .user-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
        .user-name {{ font-size: 16px; font-weight: 600; color: var(--md-on-surface);
                     white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .user-meta {{ font-size: 11px; padding: 2px 8px; background: var(--md-error-container);
                     color: var(--md-error); border-radius: 4px; font-weight: 500; }}
        .user-handle {{ font-size: 14px; color: var(--md-on-surface-variant); margin-bottom: 4px; }}
        .user-bio {{ font-size: 13px; color: var(--md-on-surface-variant); line-height: 1.4; }}
        .user-action {{ flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; display: flex;
                       align-items: center; justify-content: center; color: var(--md-on-surface-variant);
                       transition: all 0.2s ease; }}
        .user-card:hover .user-action {{ background: var(--md-primary); color: var(--md-on-primary); }}
        .show-more-btn {{ display: inline-flex; align-items: center; gap: 8px; margin-top: 16px;
                         padding: 12px 24px; background: var(--md-primary); color: var(--md-on-primary);
                         border: none; border-radius: 28px; font-size: 14px; font-weight: 500; cursor: pointer;
                         transition: all 0.2s ease; box-shadow: var(--md-elevation-1); }}
        .show-more-btn:hover {{ background: var(--md-secondary); box-shadow: var(--md-elevation-2);
                                transform: translateY(-2px); }}
        .show-more-btn:active {{ transform: translateY(0); }}
        .show-more-container {{ text-align: center; margin-top: 16px; }}
        .empty-state {{ text-align: center; padding: 48px 24px; color: var(--md-on-surface-variant); }}
        .empty-state-icon {{ font-size: 64px; margin-bottom: 16px; opacity: 0.5; }}
        .empty-state h4 {{ font-size: 18px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 8px; }}
        @media (max-width: 768px) {{
            body {{ padding: 16px; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .user-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
        <!-- Chart.js for Historical Analytics -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <script>
            console.log("TEST: JavaScript is running!");
            console.log("TEST: Chart available:", typeof Chart !== "undefined");
        </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <div class="avatar-large" style="font-size: 32px;">📈</div>
                    <div class="header-text">
                        <h1>Bluesky Analytics</h1>
                        <p>@{bluesky_handle}</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 13px; color: #49454F;">
                        Last updated: <span id="last-updated">{last_updated}</span>
                    </div>
                    <button id="refresh-btn" onclick="refreshData()" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: #1976D2; color: white; border: none; border-radius: 24px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <span class="material-icons" style="font-size: 18px;">sync</span>
                        Refresh Data
                    </button>
                    <div class="auth-badge" style="background: {'var(--md-success-container)' if auth_enabled else '#FFF3E0'}; color: {'var(--md-success)' if auth_enabled else '#F57C00'};">
                        <span>{'Authenticated ✓' if auth_enabled else 'Public API Only'}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="stat-header"><span class="stat-label">Followers</span><span class="stat-icon">👥</span></div>
                <div class="stat-value">{stats.get('follower_count', 0)}</div>
                <div class="stat-change">Current count</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-header"><span class="stat-label">Following</span><span class="stat-icon">➕</span></div>
                <div class="stat-value">{stats.get('following_count', 0)}</div>
                <div class="stat-change">People you follow</div>
            </div>
            <div class="stat-card success">
                <div class="stat-header"><span class="stat-label">Mutual</span><span class="stat-icon">🤝</span></div>
                <div class="stat-value">{len(mutual_follows)}</div>
                <div class="stat-change">Follow each other</div>
            </div>
            <div class="stat-card tertiary">
                <div class="stat-header"><span class="stat-label">Not Following Back</span><span class="stat-icon">🚫</span></div>
                <div class="stat-value">{stats.get('non_mutual_following', 0)}</div>
                <div class="stat-change">You follow, they don't</div>
            </div>
            <div class="stat-card error">
                <div class="stat-header"><span class="stat-label">Unfollowers (30d)</span><span class="stat-icon">💔</span></div>
                <div class="stat-value">{stats.get('unfollowers_30d', 0)}</div>
                <div class="stat-change">Last 30 days</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-header"><span class="stat-label">They Follow, You Don't</span><span class="stat-icon">👤</span></div>
                <div class="stat-value">{len(followers_only)}</div>
                <div class="stat-change">Follow you only</div>
            </div>
        </div>

        <!-- Global Time Filter -->
        <div class="global-time-filter" style="display: flex; justify-content: center; align-items: center; gap: 12px; margin: 24px 0; flex-wrap: wrap; padding: 16px; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <span style="font-size: 14px; color: #666; font-weight: 500;">Time Range:</span>
            <button class="time-range-btn" data-days="1" onclick="changeGlobalTimeRange(1)">1D</button>
            <button class="time-range-btn" data-days="7" onclick="changeGlobalTimeRange(7)">7D</button>
            <button class="time-range-btn active" data-days="30" onclick="changeGlobalTimeRange(30)">30D</button>
            <button class="time-range-btn" data-days="90" onclick="changeGlobalTimeRange(90)">90D</button>
            <button class="time-range-btn" data-days="365" onclick="changeGlobalTimeRange(365)">1Y</button>
            <button class="time-range-btn" data-days="999999" onclick="changeGlobalTimeRange(999999)">All</button>
        </div>

        <!-- ENGAGEMENT BALANCE SECTION (Given vs Received) -->
        <div class="section-card" style="margin-bottom: 16px;">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">⚖️</div>
                    <div class="section-text">
                        <h3>Engagement Balance</h3>
                        <p id="engagement-balance-subtitle">Comparing what you give vs what you receive</p>
                    </div>
                </div>
                <svg class="section-chevron expanded" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content expanded">
                <div class="section-body" id="engagement-balance-container">
                    <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 24px; align-items: center;">
                        <!-- Given Column -->
                        <div style="background: #E8F5E9; border-radius: 12px; padding: 20px;">
                            <h4 style="font-size: 16px; font-weight: 600; color: #388E3C; margin-bottom: 16px; text-align: center;">Given (Outgoing)</h4>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center;">
                                <div>
                                    <div id="given-likes" style="font-size: 28px; font-weight: 700; color: #388E3C;">-</div>
                                    <div style="font-size: 12px; color: #666;">Likes</div>
                                </div>
                                <div>
                                    <div id="given-reposts" style="font-size: 28px; font-weight: 700; color: #388E3C;">-</div>
                                    <div style="font-size: 12px; color: #666;">Reposts</div>
                                </div>
                                <div>
                                    <div id="given-replies" style="font-size: 28px; font-weight: 700; color: #388E3C;">-</div>
                                    <div style="font-size: 12px; color: #666;">Replies</div>
                                </div>
                            </div>
                            <div style="margin-top: 16px; text-align: center; border-top: 1px solid #A5D6A7; padding-top: 12px;">
                                <span style="font-size: 14px; color: #666;">Total:</span>
                                <span id="given-total" style="font-size: 20px; font-weight: 700; color: #2E7D32; margin-left: 8px;">-</span>
                            </div>
                        </div>

                        <!-- Balance Indicator -->
                        <div style="text-align: center;">
                            <div id="balance-indicator" style="width: 80px; height: 80px; border-radius: 50%; background: #E3F2FD; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0 auto;">
                                <div id="balance-ratio" style="font-size: 24px; font-weight: 700; color: #1976D2;">-</div>
                                <div style="font-size: 11px; color: #666;">ratio</div>
                            </div>
                            <div id="balance-type" style="font-size: 13px; font-weight: 500; color: #666; margin-top: 8px;">Loading...</div>
                        </div>

                        <!-- Received Column -->
                        <div style="background: #E3F2FD; border-radius: 12px; padding: 20px;">
                            <h4 style="font-size: 16px; font-weight: 600; color: #1976D2; margin-bottom: 16px; text-align: center;">Received (Incoming)</h4>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center;">
                                <div>
                                    <div id="received-likes" style="font-size: 28px; font-weight: 700; color: #1976D2;">-</div>
                                    <div style="font-size: 12px; color: #666;">Likes</div>
                                </div>
                                <div>
                                    <div id="received-reposts" style="font-size: 28px; font-weight: 700; color: #1976D2;">-</div>
                                    <div style="font-size: 12px; color: #666;">Reposts</div>
                                </div>
                                <div>
                                    <div id="received-replies" style="font-size: 28px; font-weight: 700; color: #1976D2;">-</div>
                                    <div style="font-size: 12px; color: #666;">Replies</div>
                                </div>
                            </div>
                            <div style="margin-top: 16px; text-align: center; border-top: 1px solid #90CAF9; padding-top: 12px;">
                                <span style="font-size: 14px; color: #666;">Total:</span>
                                <span id="received-total" style="font-size: 20px; font-weight: 700; color: #1565C0; margin-left: 8px;">-</span>
                            </div>
                        </div>
                    </div>
                    <p style="font-size: 13px; color: #666; text-align: center; margin-top: 16px;">
                        <strong>Ratio &lt; 1</strong> = you receive more than you give (receiver) |
                        <strong>Ratio &gt; 1</strong> = you give more than you receive (giver)
                    </p>
                </div>
            </div>
        </div>
"""

    html += """
<!-- HISTORICAL ANALYTICS SECTION -->
<!-- ================================================================ -->

<div class="section-card" style="margin-top: 16px;">
    <div class="section-header" onclick="toggleSection(this)">
        <div class="section-title">
            <div class="section-icon">📈</div>
            <div class="section-text">
                <h3>Historical Analytics</h3>
                <p id="analytics-subtitle">Tracking trends over time</p>
            </div>
        </div>
        <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
        </svg>
    </div>

    <div class="section-content expanded">
        <div class="section-body">
            <!-- Stats Summary Cards -->
            <div style="display: grid; grid-template-columns: repeat(8, 1fr); gap: 12px; margin-bottom: 24px;">
                <div style="background: #E3F2FD; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Days Tracked</div>
                    <div id="stat-days-tracked" style="font-size: 28px; font-weight: 700; color: #1976D2;">-</div>
                </div>
                <div style="background: #E8F5E9; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Follower Change</div>
                    <div id="stat-follower-change" style="font-size: 28px; font-weight: 700; color: #388E3C;">-</div>
                </div>
                <div style="background: #FFF3E0; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Total Posts</div>
                    <div id="stat-total-posts" style="font-size: 28px; font-weight: 700; color: #F57C00;">-</div>
                </div>
                <div style="background: #F3E5F5; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Avg Engagement</div>
                    <div id="stat-avg-engagement" style="font-size: 28px; font-weight: 700; color: #7B1FA2;">-</div>
                </div>
                <div style="background: #FFEBEE; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Likes</div>
                    <div id="stat-likes-change" style="font-size: 28px; font-weight: 700; color: #D32F2F;">-</div>
                </div>
                <div style="background: #E0F7FA; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Reposts/Quotes</div>
                    <div id="stat-reposts-quotes-change" style="font-size: 28px; font-weight: 700; color: #00838F;">-</div>
                </div>
                <div style="background: #FFF8E1; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Replies</div>
                    <div id="stat-replies-change" style="font-size: 28px; font-weight: 700; color: #FF8F00;">-</div>
                </div>
                <div style="background: #E8EAF6; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Saves</div>
                    <div id="stat-saves-change" style="font-size: 28px; font-weight: 700; color: #3949AB;">-</div>
                </div>
            </div>

            <!-- Graphs Grid -->
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">

                <!-- Row 1: Network Growth (left), Engagement Timeline (right) -->
                <!-- Follower Growth Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Network Growth</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="followerGrowthChart"></canvas>
                    </div>
                </div>

                <!-- Engagement Timeline Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h4 style="margin: 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Engagement Timeline</h4>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span style="font-size: 12px; color: #666;">View:</span>
                            <button id="engagementViewToggle" onclick="toggleEngagementView()" style="
                                padding: 6px 12px;
                                background: #1976D2;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 12px;
                                font-weight: 500;
                                transition: background 0.2s;
                            ">Daily</button>
                        </div>
                    </div>
                    <div style="position: relative; height: 280px; width: 100%;">
                        <canvas id="engagementTimelineChart"></canvas>
                    </div>
                </div>

                <!-- Row 2: Engagement Distribution (left), Posting Activity (right) -->
                <!-- Engagement Breakdown Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Engagement Distribution</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="engagementBreakdownChart"></canvas>
                    </div>
                </div>

                <!-- Posting Frequency Chart (same x-axis as Engagement Timeline) -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Posting Activity</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="postingFrequencyChart"></canvas>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
    .time-range-btn {
        padding: 8px 16px;
        border: 1px solid #CAC4D0;
        border-radius: 20px;
        background: white;
        color: #1C1B1F;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .time-range-btn:hover {
        background: #F5F5F5;
    }

    .time-range-btn.active {
        background: #1976D2;
        color: white;
        border-color: #1976D2;
    }
</style>


    """

    # Top Posts Section (AJAX-loaded)
    html += f"""
        <div class="section-card" id="top-posts-section">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">📊</div>
                    <div class="section-text">
                        <h3>Top Posts by Engagement</h3>
                        <p id="top-posts-subtitle">Your most popular posts (original content only)</p>
                    </div>
                </div>
                <span class="section-badge" id="top-posts-count">-</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body" id="top-posts-container">
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span>
                        <p>Loading top posts...</p>
                    </div>
                </div>
            </div>
        </div>
"""

    # Unfollowers Section (AJAX-loaded)
    html += f"""
        <div class="section-card" id="unfollowers-section">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">💔</div>
                    <div class="section-text">
                        <h3>Recent Unfollowers</h3>
                        <p id="unfollowers-subtitle">People who unfollowed you</p>
                    </div>
                </div>
                <span class="section-badge" id="unfollowers-count">-</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body" id="unfollowers-container">
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span>
                        <p>Loading unfollowers...</p>
                    </div>
                </div>
            </div>
        </div>
"""

    # Hidden Accounts / Blocked You / Deactivated Section
    hidden_current = hidden_analytics.get("current", {})
    if (
        hidden_current.get("suspected_blocks_or_suspensions", 0) > 0
        or hidden_current.get("blocked_count", 0) > 0
        or hidden_current.get("muted_count", 0) > 0
    ):
        html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">🚫</div>
                    <div class="section-text">
                        <h3>Hidden Accounts Analysis</h3>
                        <p>Accounts that blocked you, were deactivated, or you blocked/muted</p>
                    </div>
                </div>
                <span class="section-badge">{hidden_current.get('hidden_followers', 0)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">
                    <div style="background: var(--md-surface-variant); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 8px;"><span style="font-size: 18px; vertical-align: middle;">📊</span> Account Breakdown</h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
                            <div style="background: white; padding: 12px; border-radius: 8px;">
                                <div style="font-size: 24px; font-weight: 700; color: var(--md-primary);">{hidden_current.get('profile_followers', 0)}</div>
                                <div style="font-size: 13px; color: var(--md-on-surface-variant);">Profile Count</div>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px;">
                                <div style="font-size: 24px; font-weight: 700; color: var(--md-success);">{hidden_current.get('api_followers', 0)}</div>
                                <div style="font-size: 13px; color: var(--md-on-surface-variant);">API Returns</div>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px;">
                                <div style="font-size: 24px; font-weight: 700; color: var(--md-error);">{hidden_current.get('hidden_followers', 0)}</div>
                                <div style="font-size: 13px; color: var(--md-on-surface-variant);">Hidden</div>
                            </div>
                        </div>
                    </div>
"""
        # Show accounts you blocked
        blocked_accounts = hidden_categories.get("blocked", {}).get("accounts", [])
        if blocked_accounts:
            html += f"""
                    <div style="background: var(--md-error-container); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: var(--md-error);">🚫 You Blocked ({len(blocked_accounts)})</h4>
"""
            for user in blocked_accounts[:10]:
                display_name = user.get("display_name", user.get("handle"))
                handle = user.get("handle", "")
                bio = user.get("bio", "")[:100]
                html += f"""
                        <div class="card" style="margin-bottom: 8px; cursor: pointer;" onclick="window.open('https://bsky.app/profile/{handle}', '_blank')">
                            <strong>{display_name}</strong> <span style="color: var(--md-on-surface-variant);">@{handle}</span>
                            {f'<p style="font-size: 13px; color: var(--md-on-surface-variant); margin-top: 4px;">{bio}</p>' if bio else ''}
                        </div>
"""
            html += """
                    </div>
"""

        # Show suspected blocks/deactivations
        suspected = hidden_current.get("suspected_blocks_or_suspensions", 0)
        html += f"""
                    <div style="background: var(--md-secondary-container); padding: 20px; border-radius: 12px;">
                        <h4 style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">❓ Blocked You or Deactivated: {suspected} accounts</h4>
                        <p style="margin-bottom: 12px; line-height: 1.6;">
                            These {suspected} accounts are hidden from the API and could be:
                        </p>
                        <ul style="padding-left: 20px; margin-bottom: 12px;">
                            <li><strong>Blocked you</strong> - They don't want you to see their profile</li>
                            <li><strong>Deactivated</strong> - Deleted their account</li>
                            <li><strong>Suspended</strong> - Violated Bluesky's terms</li>
                        </ul>
                        <div style="background: rgba(255,255,255,0.3); padding: 12px; border-radius: 8px; margin-top: 12px;">
                            <p style="font-size: 13px; font-weight: 500;">
                                🔒 <strong>Cannot identify WHO:</strong> Bluesky filters these accounts for privacy. 
                                However, starting tomorrow with historical tracking, we'll be able to identify them when they disappear from our follower list!
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

    # Top Interactors Section (AJAX-loaded)
    html += f"""
        <div class="section-card" id="top-interactors-section">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">👥</div>
                    <div class="section-text">
                        <h3>Top Interactors</h3>
                        <p id="top-interactors-subtitle">People who engage most with your content</p>
                    </div>
                </div>
                <span class="section-badge" id="top-interactors-count">-</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body" id="top-interactors-container">
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span>
                        <p>Loading top interactors...</p>
                    </div>
                </div>
            </div>
        </div>
"""

    # Mutual Follows Section
    mutual_body = ""
    if mutual_follows:
        cards = "".join(
            [user_card(u, "", True, i) for i, u in enumerate(mutual_follows)]
        )
        mutual_body = f'<div class="user-grid" id="mutual-grid">{cards}</div>'
        if len(mutual_follows) > 50:
            mutual_body += f'<div class="show-more-container"><button class="show-more-btn" onclick="showMoreCards(\'mutual-grid\')">Show All {len(mutual_follows)} Mutual Follows</button></div>'
    else:
        mutual_body = '<div class="empty-state"><div class="empty-state-icon">🤝</div><h4>No mutual follows yet</h4></div>'

    html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">🤝</div>
                    <div class="section-text">
                        <h3>Mutual Follows</h3>
                        <p>Accounts where you follow each other</p>
                    </div>
                </div>
                <span class="section-badge">{len(mutual_follows)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">{mutual_body}</div>
            </div>
        </div>
"""

    # Non-Mutual Section
    non_mutual_body = ""
    if non_mutual:
        cards = "".join([user_card(u, "", True, i) for i, u in enumerate(non_mutual)])
        non_mutual_body = f'<div class="user-grid" id="non-mutual-grid">{cards}</div>'
        if len(non_mutual) > 50:
            non_mutual_body += f'<div class="show-more-container"><button class="show-more-btn" onclick="showMoreCards(\'non-mutual-grid\')">Show All {len(non_mutual)} Accounts</button></div>'
    else:
        non_mutual_body = '<div class="empty-state"><div class="empty-state-icon">✨</div><h4>Everyone follows back</h4></div>'

    html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">👻</div>
                    <div class="section-text">
                        <h3>Not Following Back</h3>
                        <p>People you follow who don't follow you back</p>
                    </div>
                </div>
                <span class="section-badge">{len(non_mutual)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">{non_mutual_body}</div>
            </div>
        </div>
"""

    # Followers Only Section
    followers_only_body = ""
    if followers_only:
        cards = "".join(
            [user_card(u, "", True, i) for i, u in enumerate(followers_only)]
        )
        followers_only_body = (
            f'<div class="user-grid" id="followers-only-grid">{cards}</div>'
        )
        if len(followers_only) > 50:
            followers_only_body += f'<div class="show-more-container"><button class="show-more-btn" onclick="showMoreCards(\'followers-only-grid\')">Show All {len(followers_only)} Followers</button></div>'
    else:
        followers_only_body = '<div class="empty-state"><div class="empty-state-icon">🤷</div><h4>No followers only</h4></div>'

    html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">🌟</div>
                    <div class="section-text">
                        <h3>Followers Only</h3>
                        <p>People who follow you but you don't follow back</p>
                    </div>
                </div>
                <span class="section-badge">{len(followers_only)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">{followers_only_body}</div>
            </div>
        </div>
"""

    # Footer with JavaScript
    html += """
    </div>
    <script>
        function showMoreCards(gridId) {
            const grid = document.getElementById(gridId);
            const hiddenCards = grid.querySelectorAll('.user-card.hidden-card');
            const btn = grid.nextElementSibling.querySelector('.show-more-btn');

            hiddenCards.forEach((card, index) => {
                setTimeout(() => {
                    card.classList.remove('hidden-card');
                    card.style.animation = 'fadeIn 0.3s ease-out';
                }, index * 20);
            });

            btn.style.display = 'none';
        }
    </script>

    <script>
        function toggleSection(element) {
            const content = element.nextElementSibling;
            const chevron = element.querySelector('.section-chevron');
            content.classList.toggle('expanded');
            chevron.classList.toggle('expanded');
        }
        
        async function refreshData() {
            const btn = document.getElementById('refresh-btn');
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="material-icons" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Refreshing...';
            btn.style.opacity = '0.6';
            
            try {
                const response = await fetch('/api/collect', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    btn.innerHTML = '<span class="material-icons" style="font-size: 18px; color: #00897B;">check_circle</span> Success!';
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    btn.innerHTML = '<span class="material-icons" style="font-size: 18px; color: #D32F2F;">error</span> Failed';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }, 2000);
                }
            } catch (error) {
                btn.innerHTML = '<span class="material-icons" style="font-size: 18px; color: #D32F2F;">error</span> Error';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    btn.style.opacity = '1';
                }, 2000);
            }
        }
    </script>
    <style>
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</body>
</html>"""

    html += """
    <script>
    // ========================================================================
// CHART.JS HISTORICAL ANALYTICS
// ========================================================================

let currentTimeRange = 30;  // Default to 30 days
let chartInstances = {};
// Store both daily and cumulative engagement data
let engagementDataStore = {
    daily: null,
    cumulative: null,
    currentView: "cumulative"
};

function toggleEngagementView() {
    const button = document.getElementById("engagementViewToggle");

    if (engagementDataStore.currentView === "cumulative") {
        engagementDataStore.currentView = "daily";
        button.textContent = "Cumulative";
        button.style.background = "#4CAF50";
    } else {
        engagementDataStore.currentView = "cumulative";
        button.textContent = "Daily";
        button.style.background = "#1976D2";
    }

    updateEngagementChart();
}

function updateEngagementChart() {
    if (!engagementDataStore.daily) {
        return;
    }

    // Destroy existing chart and recreate with new type
    if (chartInstances.engagementTimeline) {
        chartInstances.engagementTimeline.destroy();
    }

    const dataToShow = engagementDataStore.currentView === "cumulative"
        ? engagementDataStore.cumulative
        : engagementDataStore.daily;

    const ctx = document.getElementById('engagementTimelineChart').getContext('2d');

    chartInstances.engagementTimeline = new Chart(ctx, {
        type: engagementDataStore.currentView === 'cumulative' ? 'line' : 'bar',
        data: {
            labels: dataToShow.dates,
            datasets: [
                {
                    label: 'Likes',
                    data: dataToShow.likes,
                    backgroundColor: engagementDataStore.currentView === 'cumulative' ? 'rgba(233, 30, 99, 0.1)' : 'rgba(233, 30, 99, 0.8)',
                    borderColor: '#E91E63',
                    borderWidth: 2,
                    fill: engagementDataStore.currentView === 'cumulative',
                    tension: 0.4
                },
                {
                    label: 'Reposts',
                    data: dataToShow.reposts,
                    backgroundColor: engagementDataStore.currentView === 'cumulative' ? 'rgba(76, 175, 80, 0.1)' : 'rgba(76, 175, 80, 0.8)',
                    borderColor: '#4CAF50',
                    borderWidth: 2,
                    fill: engagementDataStore.currentView === 'cumulative',
                    tension: 0.4
                },
                {
                    label: 'Replies',
                    data: dataToShow.replies,
                    backgroundColor: engagementDataStore.currentView === 'cumulative' ? 'rgba(33, 150, 243, 0.1)' : 'rgba(33, 150, 243, 0.8)',
                    borderColor: '#2196F3',
                    borderWidth: 2,
                    fill: engagementDataStore.currentView === 'cumulative',
                    tension: 0.4
                },
                {
                    label: 'Quotes',
                    data: dataToShow.quotes,
                    backgroundColor: engagementDataStore.currentView === 'cumulative' ? 'rgba(156, 39, 176, 0.1)' : 'rgba(156, 39, 176, 0.8)',
                    borderColor: '#9C27B0',
                    borderWidth: 2,
                    fill: engagementDataStore.currentView === 'cumulative',
                    tension: 0.4
                },
                {
                    label: 'Bookmarks',
                    data: dataToShow.bookmarks,
                    backgroundColor: engagementDataStore.currentView === 'cumulative' ? 'rgba(255, 152, 0, 0.1)' : 'rgba(255, 152, 0, 0.8)',
                    borderColor: '#FF9800',
                    borderWidth: 2,
                    fill: engagementDataStore.currentView === 'cumulative',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: false,
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    stacked: false
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Initialize charts on page load - wait for both DOM and Chart.js
function initCharts() {
    console.log('Initializing charts...');
    console.log('Chart.js available:', typeof Chart !== 'undefined');
    console.log('Current time range:', currentTimeRange);

    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded! Retrying in 500ms...');
        setTimeout(initCharts, 500);
        return;
    }

    // Check if canvas elements exist
    const canvases = [
        'followerGrowthChart',
        'netGrowthChart',
        'engagementTimelineChart',
        'postingFrequencyChart',
        'engagementBreakdownChart'
    ];

    let allFound = true;
    canvases.forEach(id => {
        const el = document.getElementById(id);
        console.log(`Canvas ${id}:`, el ? 'found' : 'NOT FOUND');
        if (!el) allFound = false;
    });

    if (!allFound) {
        console.error('Not all canvas elements found! Retrying in 500ms...');
        setTimeout(initCharts, 500);
        return;
    }

    console.log('All prerequisites met, loading graphs...');
    loadAllGraphs(currentTimeRange);
}

// Wait for DOM to be ready, then init charts
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCharts);
} else {
    // DOM already loaded
    initCharts();
}

function changeGlobalTimeRange(days) {
    currentTimeRange = days;

    // Update button states
    document.querySelectorAll('.time-range-btn').forEach(btn => {
        btn.classList.remove('active');
        if (parseInt(btn.getAttribute('data-days')) === days || (days > 365 && btn.getAttribute('data-days') === '999999')) {
            btn.classList.add('active');
        }
    });

    // Update subtitle
    const subtitle = document.getElementById('analytics-subtitle');
    const timeLabel = getTimeLabel(days);
    if (subtitle) subtitle.textContent = timeLabel;

    // Reload all time-dependent sections
    loadAllGraphs(days);
    loadTopPosts(days);
    loadUnfollowers(days);
    loadTopInteractors(days);
    loadEngagementBalance(days);
}

function getTimeLabel(days) {
    if (days === 1) return 'Last 24 hours';
    if (days === 7) return 'Last 7 days';
    if (days === 30) return 'Last 30 days';
    if (days === 90) return 'Last 90 days';
    if (days === 365) return 'Last year';
    return 'All time';
}

async function loadAllGraphs(days) {
    console.log('loadAllGraphs called with days:', days);
    try {
        await loadStatsSummary(days);
        console.log('Stats summary loaded');

        await loadFollowerGrowthChart(days);
        console.log('Follower growth chart loaded');

        await loadEngagementTimelineChart(days);
        console.log('Engagement timeline loaded');

        await loadPostingFrequencyChart(days);
        console.log('Posting frequency loaded');

        await loadEngagementBreakdownChart(days);
        console.log('Engagement breakdown loaded');

        console.log('All graphs loaded successfully!');
    } catch (error) {
        console.error('Error loading graphs:', error);
    }
}

async function loadStatsSummary(days) {
    try {
        const response = await fetch(`/api/graphs/stats-summary?days=${days}`);
        const data = await response.json();

        document.getElementById('stat-days-tracked').textContent = data.daysTracked || '0';

        const changeElem = document.getElementById('stat-follower-change');
        const change = data.followerChange || 0;
        changeElem.textContent = change >= 0 ? `+${change}` : change;
        changeElem.style.color = change >= 0 ? '#388E3C' : '#D32F2F';

        document.getElementById('stat-total-posts').textContent = data.totalPosts || '0';
        document.getElementById('stat-avg-engagement').textContent = (data.avgEngagementPerPost || 0).toFixed(1);

        // Update new engagement change cards
        const formatChange = (value, elem, positiveColor) => {
            elem.textContent = value >= 0 ? `+${value}` : value;
            elem.style.color = value >= 0 ? positiveColor : '#D32F2F';
        };

        formatChange(data.likesChange || 0, document.getElementById('stat-likes-change'), '#D32F2F');
        formatChange(data.repostsQuotesChange || 0, document.getElementById('stat-reposts-quotes-change'), '#00838F');
        formatChange(data.repliesChange || 0, document.getElementById('stat-replies-change'), '#FF8F00');
        formatChange(data.savesChange || 0, document.getElementById('stat-saves-change'), '#3949AB');

    } catch (error) {
        console.error('Error loading stats summary:', error);
    }
}

async function loadFollowerGrowthChart(days) {
    try {
        const response = await fetch(`/api/graphs/follower-growth?days=${days}`);
        const data = await response.json();

        const ctx = document.getElementById('followerGrowthChart').getContext('2d');

        // Destroy existing chart if it exists
        if (chartInstances.followerGrowth) {
            chartInstances.followerGrowth.destroy();
        }

        // Handle empty data
        if (!data.dates || data.dates.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        chartInstances.followerGrowth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Followers',
                        data: data.followers,
                        borderColor: '#1976D2',
                        backgroundColor: 'rgba(25, 118, 210, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Following',
                        data: data.following,
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            precision: 0
                        },
                        // Add some padding to y-axis
                        grace: '5%'
                    },
                    x: {
                        // Show grid for better visibility
                        grid: {
                            display: true
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading follower growth chart:', error);
    }
}

async function loadEngagementTimelineChart(days) {
    try {
        const response = await fetch(`/api/graphs/engagement-timeline?days=${days}`);
        const responseData = await response.json();

        // Store both daily and cumulative data
        engagementDataStore.daily = responseData.daily;
        engagementDataStore.cumulative = responseData.cumulative;

        // Use cumulative by default
        const data = engagementDataStore.cumulative;

        const ctx = document.getElementById('engagementTimelineChart').getContext('2d');

        if (chartInstances.engagementTimeline) {
            chartInstances.engagementTimeline.destroy();
        }

        // Handle empty data
        if (!data.dates || data.dates.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No engagement data available yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        chartInstances.engagementTimeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Likes',
                        data: data.likes,
                        borderColor: '#E91E63',
                        backgroundColor: 'rgba(233, 30, 99, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: data.dates.length === 1 ? 6 : 3,
                        borderWidth: 2
                    },
                    {
                        label: 'Reposts',
                        data: data.reposts,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: data.dates.length === 1 ? 6 : 3,
                        borderWidth: 2
                    },
                    {
                        label: 'Replies',
                        data: data.replies,
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: data.dates.length === 1 ? 6 : 3,
                        borderWidth: 2
                    },
                    {
                        label: 'Quotes',
                        data: data.quotes,
                        borderColor: '#9C27B0',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: data.dates.length === 1 ? 6 : 3,
                        borderWidth: 2
                    },
                    {
                        label: 'Bookmarks',
                        data: data.bookmarks,
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: data.dates.length === 1 ? 6 : 3,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        stacked: false,
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    },
                    x: {
                        stacked: false
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading engagement timeline chart:', error);
    }
}

async function loadPostingFrequencyChart(days) {
    try {
        const response = await fetch(`/api/graphs/posting-frequency?days=${days}`);
        const data = await response.json();

        const ctx = document.getElementById('postingFrequencyChart').getContext('2d');

        if (chartInstances.postingFrequency) {
            chartInstances.postingFrequency.destroy();
        }

        // Handle empty data
        if (!data.dates || data.dates.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No posting data available yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        chartInstances.postingFrequency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Posts',
                        data: data.posts,
                        backgroundColor: 'rgba(255, 152, 0, 0.8)',
                        borderWidth: 0,
                        barPercentage: 0.8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading posting frequency chart:', error);
    }
}

async function loadEngagementBreakdownChart(days) {
    try {
        const response = await fetch(`/api/graphs/engagement-breakdown?days=${days}`);
        const data = await response.json();

        const ctx = document.getElementById('engagementBreakdownChart').getContext('2d');

        if (chartInstances.engagementBreakdown) {
            chartInstances.engagementBreakdown.destroy();
        }

        // Handle empty data
        if (!data.values || data.values.every(v => v === 0)) {
            ctx.fillStyle = '#999';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No engagement data available yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        chartInstances.engagementBreakdown = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        data: data.values,
                        backgroundColor: [
                            'rgba(233, 30, 99, 0.8)',   // Likes - Pink
                            'rgba(76, 175, 80, 0.8)',   // Reposts - Green
                            'rgba(33, 150, 243, 0.8)',  // Replies - Blue
                            'rgba(156, 39, 176, 0.8)',  // Quotes - Purple
                            'rgba(255, 152, 0, 0.8)'    // Bookmarks - Orange
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading engagement breakdown chart:', error);
    }
}

// ========================================================================
// AJAX-LOADED SECTIONS
// ========================================================================

const blueskyHandle = '""" + bluesky_handle + """';
let userAvatarUrl = null;

// Fetch user avatar on page load
async function fetchUserAvatar() {
    try {
        const response = await fetch(`https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=${blueskyHandle}`);
        const data = await response.json();
        userAvatarUrl = data.avatar || null;
    } catch (e) {
        console.log('Could not fetch avatar:', e);
    }
}
fetchUserAvatar();

async function loadTopPosts(days) {
    const container = document.getElementById('top-posts-container');
    const countBadge = document.getElementById('top-posts-count');
    const subtitle = document.getElementById('top-posts-subtitle');

    try {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span><p>Loading top posts...</p></div>';

        const response = await fetch(`/api/top-posts?days=${days}`);
        const data = await response.json();

        countBadge.textContent = data.count || 0;
        subtitle.textContent = `Your most popular posts (${getTimeLabel(days).toLowerCase()})`;

        if (!data.posts || data.posts.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📊</div><h4>No posts in this time period</h4></div>';
            return;
        }

        let html = '';
        for (const post of data.posts) {
            const directScore = (post.likes || 0) + (post.reposts || 0) * 2 + (post.replies || 0) * 3 + (post.bookmarks || 0) * 2;
            const indirectScore = ((post.indirect_likes || 0) + (post.indirect_reposts || 0) * 2 + (post.indirect_replies || 0) * 3 + (post.indirect_bookmarks || 0) * 2) * 0.5;
            const engagementScore = Math.round(directScore + indirectScore);

            const postId = post.uri ? post.uri.split('/').pop() : '';
            const postUrl = postId ? `https://bsky.app/profile/${blueskyHandle}/post/${postId}` : '#';
            const postText = (post.text || '').replace(/'/g, "\\\\'").replace(/"/g, '&quot;');

            let formattedDate = 'Unknown date';
            if (post.created_at) {
                try {
                    const dt = new Date(post.created_at);
                    formattedDate = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' at ' + dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                } catch (e) {
                    formattedDate = post.created_at;
                }
            }

            const totalIndirect = (post.indirect_likes || 0) + (post.indirect_reposts || 0) + (post.indirect_replies || 0) + (post.indirect_bookmarks || 0);
            const indirectBadge = totalIndirect > 0 ?
                `<div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #E1F5FE; border-radius: 12px; font-size: 13px;" title="Indirect Engagement from quote posts"><span class="material-icons" style="font-size: 16px; color: #0277BD;">add_circle</span><span style="font-weight: 500; color: #0277BD;">+${totalIndirect} indirect</span></div>` : '';

            html += `
                <div class="post-card" onclick="window.open('${postUrl}', '_blank')" style="background: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 0; margin-bottom: 16px; cursor: pointer; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); overflow: hidden;">
                    <div style="display: flex; align-items: center; gap: 12px; padding: 16px 16px 12px 16px;">
                        ${userAvatarUrl
                            ? `<img src="${userAvatarUrl}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; flex-shrink: 0;" alt="avatar">`
                            : `<div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1976D2, #0288D1); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 20px; flex-shrink: 0;">${blueskyHandle[0].toUpperCase()}</div>`
                        }
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: 600; font-size: 15px; color: #1C1B1F;">@${blueskyHandle}</div>
                            <div style="font-size: 14px; color: #666;">Tracked Account</div>
                        </div>
                        <div style="font-size: 13px; color: #999;">${formattedDate}</div>
                    </div>
                    <div style="padding: 0 16px 12px 16px;">
                        <div style="font-size: 15px; color: #1C1B1F; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;">${postText}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 20px; padding: 12px 16px; border-top: 1px solid #E0E0E0; background: #FAFAFA; font-size: 14px; flex-wrap: wrap;">
                        <div style="display: inline-flex; align-items: center; gap: 6px;" title="Likes"><span class="material-icons" style="font-size: 18px; color: #1976D2;">favorite</span><span style="font-weight: 500;">${post.likes || 0}</span></div>
                        <div style="display: inline-flex; align-items: center; gap: 6px;" title="Reposts"><span class="material-icons" style="font-size: 18px; color: #1976D2;">repeat</span><span style="font-weight: 500;">${post.reposts || 0}</span></div>
                        <div style="display: inline-flex; align-items: center; gap: 6px;" title="Replies"><span class="material-icons" style="font-size: 18px; color: #1976D2;">chat_bubble_outline</span><span style="font-weight: 500;">${post.replies || 0}</span></div>
                        <div style="display: inline-flex; align-items: center; gap: 6px;" title="Quotes"><span class="material-icons" style="font-size: 18px; color: #1976D2;">format_quote</span><span style="font-weight: 500;">${post.quotes || 0}</span></div>
                        <div style="display: inline-flex; align-items: center; gap: 6px;" title="Saves"><span class="material-icons" style="font-size: 18px; color: #1976D2;">bookmark</span><span style="font-weight: 500;">${post.bookmarks || 0}</span></div>
                        ${indirectBadge}
                        <div style="display: inline-flex; align-items: center; gap: 6px; margin-left: auto; font-weight: 600; color: #1976D2; border-left: 1px solid #E0E0E0; padding-left: 20px;"><span class="material-icons" style="font-size: 18px;">trending_up</span><span>${engagementScore}</span></div>
                    </div>
                </div>`;
        }
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading top posts:', error);
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h4>Error loading posts</h4></div>';
    }
}

async function loadUnfollowers(days) {
    const container = document.getElementById('unfollowers-container');
    const countBadge = document.getElementById('unfollowers-count');
    const subtitle = document.getElementById('unfollowers-subtitle');

    try {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span><p>Loading unfollowers...</p></div>';

        const response = await fetch(`/api/unfollowers?days=${days}`);
        const data = await response.json();

        countBadge.textContent = data.unfollowers ? data.unfollowers.length : 0;
        subtitle.textContent = `People who unfollowed you (${getTimeLabel(days).toLowerCase()})`;

        if (!data.unfollowers || data.unfollowers.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🎉</div><h4>No unfollowers in this time period</h4></div>';
            return;
        }

        let html = '<div class="user-grid">';
        for (const user of data.unfollowers) {
            const handle = user.handle || '';
            const displayName = user.display_name || handle;
            const avatarUrl = user.avatar || '';
            const changeDate = user.change_date || '';
            const profileUrl = `https://bsky.app/profile/${handle}`;

            const avatarHtml = avatarUrl ?
                `<div class="user-avatar"><img src="${avatarUrl}" alt="${displayName}" onerror="this.parentNode.innerHTML='<div style=\\'width:56px;height:56px;border-radius:50%;background:#CAC4D0;display:flex;align-items:center;justify-content:center;font-size:24px;color:#666;\\'>${displayName[0] || '?'}</div>'" loading="lazy"></div>` :
                `<div class="user-avatar"><div style="width:56px;height:56px;border-radius:50%;background:#CAC4D0;display:flex;align-items:center;justify-content:center;font-size:24px;color:#666;">${displayName[0] || '?'}</div></div>`;

            html += `
                <div class="user-card" onclick="window.open('${profileUrl}', '_blank')">
                    ${avatarHtml}
                    <div class="user-content">
                        <div class="user-header">
                            <span class="user-name">${displayName}</span>
                            ${changeDate ? `<span class="user-meta">${changeDate}</span>` : ''}
                        </div>
                        <div class="user-handle">@${handle}</div>
                    </div>
                    <div class="user-action"><span class="material-icons">open_in_new</span></div>
                </div>`;
        }
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading unfollowers:', error);
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h4>Error loading unfollowers</h4></div>';
    }
}

async function loadTopInteractors(days) {
    const container = document.getElementById('top-interactors-container');
    const countBadge = document.getElementById('top-interactors-count');
    const subtitle = document.getElementById('top-interactors-subtitle');

    try {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><span class="material-icons" style="font-size: 48px; animation: spin 1s linear infinite;">sync</span><p>Loading top interactors...</p></div>';

        const response = await fetch(`/api/top-interactors?days=${days}`);
        const data = await response.json();

        countBadge.textContent = data.count || 0;
        subtitle.textContent = `People who engage most with your content (${getTimeLabel(days).toLowerCase()})`;

        if (!data.interactors || data.interactors.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">👥</div><h4>No interactors in this time period</h4></div>';
            return;
        }

        let html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;">';
        for (const interactor of data.interactors) {
            const handle = interactor.handle || '';
            const displayName = interactor.display_name || handle;
            const avatarUrl = interactor.avatar || '';
            const score = interactor.score || 0;
            const likes = interactor.likes || 0;
            const replies = interactor.replies || 0;
            const reposts = interactor.reposts || 0;
            const quotes = interactor.quotes || 0;
            const follows = interactor.follows || 0;
            const profileUrl = `https://bsky.app/profile/${handle}`;

            const avatarHtml = avatarUrl ?
                `<div style="width: 56px; height: 56px;"><img src="${avatarUrl}" alt="${displayName}" style="width: 56px; height: 56px; border-radius: 50%; object-fit: cover;" onerror="this.parentNode.style.display='none'" loading="lazy"></div>` : '';

            let badgesHtml = '';
            if (likes > 0) badgesHtml += `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E3F2FD; color: #1976D2;"><span class="material-icons" style="font-size: 14px;">favorite</span>${likes}</span>`;
            if (replies > 0) badgesHtml += `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E3F2FD; color: #1976D2; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">chat_bubble</span>${replies}</span>`;
            if (reposts > 0) badgesHtml += `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E1F5FE; color: #0288D1; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">repeat</span>${reposts}</span>`;
            if (quotes > 0) badgesHtml += `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #B3E5FC; color: #01579B; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">format_quote</span>${quotes}</span>`;
            if (follows > 0) badgesHtml += `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #BBDEFB; color: #1976D2; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">person_add</span>${follows}</span>`;

            html += `
                <div style="background: white; border: 1px solid #CAC4D0; border-radius: 12px; padding: 16px; display: flex; gap: 16px; transition: all 0.2s; cursor: pointer;" onclick="window.open('${profileUrl}', '_blank')">
                    ${avatarHtml}
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <div style="font-weight: 600; color: #1C1B1F; font-size: 15px;">${displayName}</div>
                            <div style="background: #1976D2; color: white; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;">${score}</div>
                        </div>
                        <div style="color: #49454F; font-size: 14px; margin-bottom: 12px;">@${handle}</div>
                        <div style="display: flex; gap: 4px; flex-wrap: wrap;">${badgesHtml}</div>
                    </div>
                </div>`;
        }
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading top interactors:', error);
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h4>Error loading top interactors</h4></div>';
    }
}

async function loadEngagementBalance(days) {
    try {
        const url = days ? `/api/engagement/balance?days=${days}` : '/api/engagement/balance';
        const response = await fetch(url);
        const data = await response.json();

        // Update Given column
        document.getElementById('given-likes').textContent = data.given?.likes || 0;
        document.getElementById('given-reposts').textContent = data.given?.reposts || 0;
        document.getElementById('given-replies').textContent = data.given?.replies || 0;
        document.getElementById('given-total').textContent = data.given?.total || 0;

        // Update Received column
        document.getElementById('received-likes').textContent = data.received?.likes || 0;
        document.getElementById('received-reposts').textContent = data.received?.reposts || 0;
        document.getElementById('received-replies').textContent = data.received?.replies || 0;
        document.getElementById('received-total').textContent = data.received?.total || 0;

        // Update ratio and balance type
        const ratio = data.ratio || 0;
        document.getElementById('balance-ratio').textContent = ratio.toFixed(2);

        const balanceType = data.balance_type || 'balanced';
        const balanceTypeElem = document.getElementById('balance-type');
        const balanceIndicator = document.getElementById('balance-indicator');

        if (balanceType === 'giver') {
            balanceTypeElem.textContent = 'You give more';
            balanceTypeElem.style.color = '#388E3C';
            balanceIndicator.style.background = '#E8F5E9';
        } else if (balanceType === 'receiver') {
            balanceTypeElem.textContent = 'You receive more';
            balanceTypeElem.style.color = '#1976D2';
            balanceIndicator.style.background = '#E3F2FD';
        } else {
            balanceTypeElem.textContent = 'Balanced';
            balanceTypeElem.style.color = '#666';
            balanceIndicator.style.background = '#F5F5F5';
        }

        // Update subtitle
        const subtitle = document.getElementById('engagement-balance-subtitle');
        if (subtitle) {
            subtitle.textContent = `Comparing what you give vs what you receive (${getTimeLabel(days || 999999).toLowerCase()})`;
        }
    } catch (error) {
        console.error('Error loading engagement balance:', error);
    }
}

// Load AJAX sections on page init
document.addEventListener('DOMContentLoaded', function() {
    loadTopPosts(currentTimeRange);
    loadUnfollowers(currentTimeRange);
    loadTopInteractors(currentTimeRange);
    loadEngagementBalance(currentTimeRange);
});

    </script>
    """

    return html
