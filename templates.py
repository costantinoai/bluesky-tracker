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
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
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
                    <div class="auth-badge">
                        <span>Authenticated ✓</span>
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
"""

    html += """
<!-- HISTORICAL ANALYTICS SECTION -->
<!-- ================================================================ -->

<div class="section-card" style="margin-top: 32px;">
    <div class="section-header">
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

    <div class="section-content expanded" style="display: block;">
        <div class="section-body">
            <!-- Time Range Selector -->
            <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;">
                <button class="time-range-btn active" data-days="1" onclick="changeTimeRange(1)">1D</button>
                <button class="time-range-btn" data-days="7" onclick="changeTimeRange(7)">7D</button>
                <button class="time-range-btn" data-days="30" onclick="changeTimeRange(30)">30D</button>
                <button class="time-range-btn" data-days="90" onclick="changeTimeRange(90)">90D</button>
                <button class="time-range-btn" data-days="365" onclick="changeTimeRange(365)">1Y</button>
                <button class="time-range-btn" data-days="999999" onclick="changeTimeRange(999999)">All</button>
            </div>

            <!-- Stats Summary Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                <div style="background: #E3F2FD; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Days Tracked</div>
                    <div id="stat-days-tracked" style="font-size: 32px; font-weight: 700; color: #1976D2;">-</div>
                </div>
                <div style="background: #E8F5E9; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Follower Change</div>
                    <div id="stat-follower-change" style="font-size: 32px; font-weight: 700; color: #388E3C;">-</div>
                </div>
                <div style="background: #FFF3E0; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Total Posts</div>
                    <div id="stat-total-posts" style="font-size: 32px; font-weight: 700; color: #F57C00;">-</div>
                </div>
                <div style="background: #F3E5F5; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px;">Avg Engagement</div>
                    <div id="stat-avg-engagement" style="font-size: 32px; font-weight: 700; color: #7B1FA2;">-</div>
                </div>
            </div>

            <!-- Graphs Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 24px;">

                <!-- Follower Growth Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Network Growth</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="followerGrowthChart"></canvas>
                    </div>
                </div>

                <!-- Net Growth Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Daily Net Change</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="netGrowthChart"></canvas>
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

                <!-- Posting Frequency Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Posting Activity</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="postingFrequencyChart"></canvas>
                    </div>
                </div>

                <!-- Engagement Breakdown Chart -->
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 350px;">
                    <h4 style="margin: 0 0 16px 0; color: #1C1B1F; font-size: 16px; font-weight: 600;">Engagement Distribution</h4>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="engagementBreakdownChart"></canvas>
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

    # Top Posts Section
    if top_posts:
        html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">📊</div>
                    <div class="section-text">
                        <h3>Top Posts by Engagement</h3>
                        <p>Your most popular posts (original content only)</p>
                    </div>
                </div>
                <span class="section-badge">{len(top_posts)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">
"""
        for post in top_posts[:10]:
            # Calculate engagement score (including indirect engagement from quote posts)
            direct_score = (
                post.get("likes", 0)
                + post.get("reposts", 0) * 2
                + post.get("replies", 0) * 3
                + post.get("bookmarks", 0) * 2
            )
            indirect_score = (
                post.get("indirect_likes", 0)
                + post.get("indirect_reposts", 0) * 2
                + post.get("indirect_replies", 0) * 3
                + post.get("indirect_bookmarks", 0) * 2
            ) * 0.5
            engagement_score = int(direct_score + indirect_score)

            # Extract post ID from URI
            post_uri = post.get("uri", "")
            post_id = post_uri.split("/")[-1] if post_uri else ""
            post_url = (
                f"https://bsky.app/profile/{bluesky_handle}/post/{post_id}"
                if post_id
                else "#"
            )

            # Escape quotes in post text
            post_text = post.get("text", "").replace("'", "\\'").replace('"', "&quot;")

            # Format timestamp
            created_at = post.get("created_at", "")
            if created_at:
                from datetime import datetime

                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    formatted_date = dt.strftime("%b %d, %Y at %I:%M %p")
                except:
                    formatted_date = created_at
            else:
                formatted_date = "Unknown date"

            # Pre-calculate indirect engagement values (to avoid nested f-strings)
            indirect_likes = post.get("indirect_likes", 0)
            indirect_reposts = post.get("indirect_reposts", 0)
            indirect_replies = post.get("indirect_replies", 0)
            indirect_bookmarks = post.get("indirect_bookmarks", 0)
            total_indirect = (
                indirect_likes
                + indirect_reposts
                + indirect_replies
                + indirect_bookmarks
            )

            # Build indirect engagement badge HTML (if there's indirect engagement)
            indirect_badge = ""
            if total_indirect > 0:
                indirect_badge = f'<div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #E1F5FE; border-radius: 12px; font-size: 13px;" title="Indirect Engagement: {indirect_likes} likes, {indirect_reposts} reposts, {indirect_replies} replies, {indirect_bookmarks} bookmarks on quote posts"><span class="material-icons" style="font-size: 16px; color: #0277BD;">add_circle</span><span style="font-weight: 500; color: #0277BD;">+{total_indirect} indirect</span></div>'

            # Generate profile URL for avatar (generic Bluesky profile)
            profile_url_for_avatar = f"https://bsky.app/profile/{bluesky_handle}"

            html += f"""
                    <div class="post-card" onclick="window.open('{post_url}', '_blank')" style="background: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 0; margin-bottom: 16px; cursor: pointer; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); overflow: hidden;">
                        <!-- Post Header -->
                        <div style="display: flex; align-items: center; gap: 12px; padding: 16px 16px 12px 16px;">
                            <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1976D2, #0288D1); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 20px; flex-shrink: 0;">{bluesky_handle[0].upper()}</div>
                            <div style="flex: 1; min-width: 0;">
                                <div style="font-weight: 600; font-size: 15px; color: #1C1B1F;">@{bluesky_handle}</div>
                                <div style="font-size: 14px; color: #666;">Tracked Account</div>
                            </div>
                            <div style="font-size: 13px; color: #999;">{formatted_date}</div>
                        </div>

                        <!-- Post Content -->
                        <div style="padding: 0 16px 12px 16px;">
                            <div style="font-size: 15px; color: #1C1B1F; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;">{post_text}</div>
                        </div>

                        <!-- Metrics Bar -->
                        <div style="display: flex; align-items: center; gap: 20px; padding: 12px 16px; border-top: 1px solid #E0E0E0; background: #FAFAFA; font-size: 14px;">
                            <div style="display: inline-flex; align-items: center; gap: 6px;" title="Likes">
                                <span class="material-icons" style="font-size: 18px; color: #1976D2;">favorite</span>
                                <span style="font-weight: 500;">{post.get('likes', 0)}</span>
                            </div>
                            <div style="display: inline-flex; align-items: center; gap: 6px;" title="Reposts">
                                <span class="material-icons" style="font-size: 18px; color: #1976D2;">repeat</span>
                                <span style="font-weight: 500;">{post.get('reposts', 0)}</span>
                            </div>
                            <div style="display: inline-flex; align-items: center; gap: 6px;" title="Replies">
                                <span class="material-icons" style="font-size: 18px; color: #1976D2;">chat_bubble_outline</span>
                                <span style="font-weight: 500;">{post.get('replies', 0)}</span>
                            </div>
                            <div style="display: inline-flex; align-items: center; gap: 6px;" title="Quotes">
                                <span class="material-icons" style="font-size: 18px; color: #1976D2;">format_quote</span>
                                <span style="font-weight: 500;">{post.get('quotes', 0)}</span>
                            </div>
                            <div style="display: inline-flex; align-items: center; gap: 6px;" title="Bookmarks/Saves">
                                <span class="material-icons" style="font-size: 18px; color: #1976D2;">bookmark</span>
                                <span style="font-weight: 500;">{post.get('bookmarks', 0)}</span>
                            </div>
                            {indirect_badge}
                            <div style="display: inline-flex; align-items: center; gap: 6px; margin-left: auto; font-weight: 600; color: #1976D2; border-left: 1px solid #E0E0E0; padding-left: 20px;" title="Engagement Score: {engagement_score}&#10;Direct: {post.get('likes', 0)} likes + {post.get('reposts', 0)}×2 reposts + {post.get('replies', 0)}×3 replies + {post.get('bookmarks', 0)}×2 bookmarks = {int(direct_score)}&#10;Indirect (×0.5): {indirect_likes} likes + {indirect_reposts}×2 reposts + {indirect_replies}×3 replies + {indirect_bookmarks}×2 bookmarks = {int(indirect_score)}&#10;(Indirect = engagement on posts that quoted this post)">
                                <span class="material-icons" style="font-size: 18px;">trending_up</span>
                                <span>{engagement_score}</span>
                            </div>
                        </div>
                    </div>
"""
        html += """
                </div>
            </div>
        </div>
"""

    # Unfollowers Section
    unfollowers_body = ""
    if unfollowers:
        cards = "".join(
            [
                user_card(u, u.get("change_date", ""), True, i)
                for i, u in enumerate(unfollowers)
            ]
        )
        unfollowers_body = f'<div class="user-grid" id="unfollowers-grid">{cards}</div>'
        if len(unfollowers) > 50:
            unfollowers_body += f'<div class="show-more-container"><button class="show-more-btn" onclick="showMoreCards(\'unfollowers-grid\')">Show All {len(unfollowers)} Unfollowers</button></div>'
    else:
        unfollowers_body = '<div class="empty-state"><div class="empty-state-icon">🎉</div><h4>No unfollowers</h4></div>'

    html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">💔</div>
                    <div class="section-text">
                        <h3>Recent Unfollowers</h3>
                        <p>People who unfollowed you in the last 30 days</p>
                    </div>
                </div>
                <span class="section-badge">{len(unfollowers)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">{unfollowers_body}</div>
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

    # Top Interactors Section
    if top_interactors:
        html += f"""
        <div class="section-card">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <div class="section-icon">👥</div>
                    <div class="section-text">
                        <h3>Top Interactors</h3>
                        <p>People who engage most with your content</p>
                    </div>
                </div>
                <span class="section-badge">{len(top_interactors)}</span>
                <svg class="section-chevron" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="section-content">
                <div class="section-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;">
"""

        for interactor in top_interactors[:20]:
            handle = interactor.get("handle", "")
            display_name = interactor.get("display_name", handle)
            avatar_url = interactor.get("avatar", "")
            score = interactor.get("score", 0)
            likes = interactor.get("likes", 0)
            replies = interactor.get("replies", 0)
            reposts = interactor.get("reposts", 0)
            quotes = interactor.get("quotes", 0)
            follows = interactor.get("follows", 0)

            avatar_html = ""
            if avatar_url and avatar_url.strip():
                avatar_html = f'<div style="width: 56px; height: 56px;"><img src="{avatar_url}" alt="{display_name}" style="width: 56px; height: 56px; border-radius: 50%; object-fit: cover;" onerror="this.parentNode.style.display=&quot;none&quot;" loading="lazy"></div>'

            profile_url = f"https://bsky.app/profile/{handle}"

            badges_html = ""
            if likes > 0:
                badges_html += f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E3F2FD; color: #1976D2;"><span class="material-icons" style="font-size: 14px;">favorite</span>{likes}</span>'
            if replies > 0:
                badges_html += f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E3F2FD; color: #1976D2; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">chat_bubble</span>{replies}</span>'
            if reposts > 0:
                badges_html += f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #E1F5FE; color: #0288D1; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">repeat</span>{reposts}</span>'
            if quotes > 0:
                badges_html += f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #B3E5FC; color: #01579B; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">format_quote</span>{quotes}</span>'
            if follows > 0:
                badges_html += f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 500; background: #BBDEFB; color: #1976D2; margin-left: 4px;"><span class="material-icons" style="font-size: 14px;">person_add</span>{follows}</span>'

            html += f"""
                        <div style="background: white; border: 1px solid #CAC4D0; border-radius: 12px; padding: 16px; display: flex; gap: 16px; transition: all 0.2s; cursor: pointer;" onclick="window.open('{profile_url}', '_blank')">
                            {avatar_html}
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                    <div style="font-weight: 600; color: #1C1B1F; font-size: 15px;">{display_name}</div>
                                    <div style="background: #1976D2; color: white; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;">{score}</div>
                                </div>
                                <div style="color: #49454F; font-size: 14px; margin-bottom: 12px;">@{handle}</div>
                                <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                                    {badges_html}
                                </div>
                            </div>
                        </div>
"""

        html += """
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
        function toggleSection(header) {
            const content = header.nextElementSibling;
            const chevron = header.querySelector('.section-chevron');
            content.classList.toggle('expanded');
            chevron.classList.toggle('expanded');
        }

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

let currentTimeRange = 999999;  // Default to "All" data
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

function changeTimeRange(days) {
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
    if (days === 1) subtitle.textContent = 'Last 24 hours';
    else if (days === 7) subtitle.textContent = 'Last 7 days';
    else if (days === 30) subtitle.textContent = 'Last 30 days';
    else if (days === 90) subtitle.textContent = 'Last 90 days';
    else if (days === 365) subtitle.textContent = 'Last year';
    else subtitle.textContent = 'All time';

    // Reload all graphs
    loadAllGraphs(days);
}

async function loadAllGraphs(days) {
    console.log('loadAllGraphs called with days:', days);
    try {
        await loadStatsSummary(days);
        console.log('Stats summary loaded');

        await loadFollowerGrowthChart(days);
        console.log('Follower growth chart loaded');

        await loadNetGrowthChart(days);
        console.log('Net growth chart loaded');

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
                        pointRadius: 15,  // Make points visible
                        pointHoverRadius: 20
                    },
                    {
                        label: 'Following',
                        data: data.following,
                        borderColor: '#0288D1',
                        backgroundColor: 'rgba(2, 136, 209, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 15,
                        pointHoverRadius: 20
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

async function loadNetGrowthChart(days) {
    try {
        const response = await fetch(`/api/graphs/net-growth?days=${days}`);
        const data = await response.json();

        const ctx = document.getElementById('netGrowthChart').getContext('2d');

        if (chartInstances.netGrowth) {
            chartInstances.netGrowth.destroy();
        }

        // Handle empty data
        if (!data.dates || data.dates.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No daily change data yet (need 2+ days)', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        // Color bars based on positive/negative
        const followerColors = data.netFollowers.map(v => v >= 0 ? 'rgba(56, 142, 60, 0.8)' : 'rgba(211, 47, 47, 0.8)');

        chartInstances.netGrowth = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Net Followers',
                        data: data.netFollowers,
                        backgroundColor: followerColors,
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
                        display: true,
                        position: 'bottom'
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
        console.error('Error loading net growth chart:', error);
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

    </script>
    """

    return html
