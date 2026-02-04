import { useState, useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users, UserPlus, UserMinus, Heart, Repeat2, MessageCircle,
  TrendingUp, TrendingDown, RefreshCw, Moon, Sun, ChevronDown,
  ExternalLink, BarChart3, Activity, Eye, EyeOff, Zap, Star,
  Calendar, FileText, Bookmark, Quote, Shield, AlertTriangle,
  Clock, PieChart as PieChartIcon, Ban, UserX, Search, ArrowUpDown,
  Download, X, Sparkles
} from 'lucide-react'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import './App.css'

// API fetch helper
const fetchAPI = async (endpoint) => {
  const res = await fetch(`/api${endpoint}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

// Last visit tracking for "New" badges
const LAST_VISIT_KEY = 'bluesky-tracker-last-visit'

function getLastVisit() {
  const stored = localStorage.getItem(LAST_VISIT_KEY)
  return stored ? new Date(stored) : null
}

function updateLastVisit() {
  localStorage.setItem(LAST_VISIT_KEY, new Date().toISOString())
}

function isNewSinceLastVisit(dateStr, lastVisit) {
  if (!lastVisit || !dateStr) return false
  const itemDate = new Date(dateStr)
  return itemDate > lastVisit
}

// Export helpers
function exportToCSV(data, filename) {
  if (!data || data.length === 0) return
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(h => {
      const val = row[h]
      if (val === null || val === undefined) return ''
      const str = String(val).replace(/"/g, '""')
      return str.includes(',') || str.includes('"') || str.includes('\n') ? `"${str}"` : str
    }).join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  link.click()
}

function exportToJSON(data, filename) {
  if (!data || data.length === 0) return
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.json`
  link.click()
}

// Search, Filter, Sort component for user lists
function ListToolbar({ onSearch, searchValue, sortValue, onSort, sortOptions, exportData, exportName }) {
  const [showExport, setShowExport] = useState(false)

  return (
    <div className="list-toolbar">
      <div className="search-box">
        <Search size={16} />
        <input
          type="text"
          placeholder="Search by name or handle..."
          value={searchValue}
          onChange={(e) => onSearch(e.target.value)}
        />
        {searchValue && (
          <button className="search-clear" onClick={() => onSearch('')}>
            <X size={14} />
          </button>
        )}
      </div>

      <div className="toolbar-right">
        <div className="sort-select">
          <ArrowUpDown size={14} />
          <select value={sortValue} onChange={(e) => onSort(e.target.value)}>
            {sortOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {exportData && exportData.length > 0 && (
          <div className="export-dropdown">
            <button
              className="export-btn"
              onClick={() => setShowExport(!showExport)}
            >
              <Download size={14} />
              Export
            </button>
            {showExport && (
              <div className="export-menu">
                <button onClick={() => { exportToCSV(exportData, exportName); setShowExport(false) }}>
                  Export as CSV
                </button>
                <button onClick={() => { exportToJSON(exportData, exportName); setShowExport(false) }}>
                  Export as JSON
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// New badge component
function NewBadge() {
  return (
    <span className="new-badge">
      <Sparkles size={10} />
      New
    </span>
  )
}

// Refresh Progress Modal
function RefreshModal({ isOpen, status, steps, error, onClose }) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <motion.div
        className="modal-content"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>
            <RefreshCw size={20} className={status === 'running' ? 'spin' : ''} />
            Data Collection
          </h3>
          {status !== 'running' && (
            <button className="modal-close" onClick={onClose}>
              <X size={18} />
            </button>
          )}
        </div>

        <div className="modal-body">
          {steps.map((step, i) => (
            <div key={i} className={`refresh-step ${step.status}`}>
              <div className="step-icon">
                {step.status === 'done' && <span className="check">&#10003;</span>}
                {step.status === 'running' && <span className="spinner" />}
                {step.status === 'pending' && <span className="dot" />}
                {step.status === 'error' && <span className="error-x">&#10007;</span>}
              </div>
              <span className="step-label">{step.label}</span>
            </div>
          ))}

          {error && (
            <div className="refresh-error">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          {status === 'done' && !error && (
            <div className="refresh-success">
              <Zap size={16} />
              Collection complete! Data refreshed.
            </div>
          )}
        </div>

        {status !== 'running' && (
          <div className="modal-footer">
            <button className="modal-btn" onClick={onClose}>
              Close
            </button>
          </div>
        )}
      </motion.div>
    </div>
  )
}

// Mini Stat Card for summary row
function MiniStatCard({ label, value, color, icon: Icon }) {
  return (
    <div className="mini-stat-card" style={{ '--accent': color }}>
      {Icon && <Icon size={14} className="mini-stat-icon" />}
      <span className="mini-stat-value font-mono">{value}</span>
      <span className="mini-stat-label">{label}</span>
    </div>
  )
}

// Stat Card Component
function StatCard({ icon: Icon, label, value, change, color, delay = 0 }) {
  const isPositive = change > 0
  const isNegative = change < 0

  return (
    <motion.div
      className="stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <div className="stat-card-header">
        <div className="stat-icon" style={{ color }}>
          <Icon size={20} strokeWidth={2} />
        </div>
        <span className="stat-label">{label}</span>
      </div>
      <div className="stat-value-row">
        <span className="stat-value font-mono">{value?.toLocaleString() ?? '—'}</span>
        {change !== undefined && change !== 0 && (
          <span className={`stat-change ${isPositive ? 'positive' : ''} ${isNegative ? 'negative' : ''}`}>
            {isPositive ? '+' : ''}{change}
          </span>
        )}
      </div>
    </motion.div>
  )
}

// User Card Component
function UserCard({ user, meta, isNew }) {
  const initial = (user.display_name?.[0] || user.handle?.[0] || '?').toUpperCase()

  return (
    <motion.a
      href={`https://bsky.app/profile/${user.handle}`}
      target="_blank"
      rel="noopener noreferrer"
      className={`user-card ${isNew ? 'is-new' : ''}`}
      whileHover={{ scale: 1.02, x: 4 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="user-avatar">
        {user.avatar_url || user.avatar ? (
          <img src={user.avatar_url || user.avatar} alt="" loading="lazy" />
        ) : (
          <span className="avatar-fallback">{initial}</span>
        )}
      </div>
      <div className="user-info">
        <div className="user-name-row">
          <span className="user-name">{user.display_name || user.handle}</span>
          {isNew && <NewBadge />}
        </div>
        <span className="user-handle font-mono">@{user.handle}</span>
        {user.bio && <p className="user-bio">{user.bio.slice(0, 80)}{user.bio.length > 80 ? '...' : ''}</p>}
      </div>
      {meta && <span className="user-meta">{meta}</span>}
      <ExternalLink size={14} className="user-external" />
    </motion.a>
  )
}

// Interactor Card with engagement stats
function InteractorCard({ user }) {
  const initial = (user.display_name?.[0] || user.handle?.[0] || '?').toUpperCase()
  const [showTooltip, setShowTooltip] = useState(false)

  return (
    <motion.a
      href={`https://bsky.app/profile/${user.handle}`}
      target="_blank"
      rel="noopener noreferrer"
      className="interactor-card"
      whileHover={{ scale: 1.02 }}
    >
      <div className="user-avatar">
        {user.avatar ? (
          <img src={user.avatar} alt="" loading="lazy" />
        ) : (
          <span className="avatar-fallback">{initial}</span>
        )}
      </div>
      <div className="interactor-info">
        <span className="user-name">{user.display_name || user.handle}</span>
        <span className="user-handle font-mono">@{user.handle}</span>
      </div>
      <div
        className="interactor-score-compact"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <span className="score-value font-mono">{user.score}</span>
        {showTooltip && (
          <div className="score-tooltip">
            <div className="score-breakdown">
              <span><Heart size={12} /> {user.likes || 0} likes</span>
              <span><Repeat2 size={12} /> {user.reposts || 0} reposts</span>
              <span><MessageCircle size={12} /> {user.replies || 0} replies</span>
              <span><Quote size={12} /> {user.quotes || 0} quotes</span>
              <span><UserPlus size={12} /> {user.follows ? 'Followed' : ''}</span>
            </div>
          </div>
        )}
      </div>
    </motion.a>
  )
}

// Post Card
function PostCard({ post, userHandle }) {
  // Extract the post ID (rkey) from the URI (format: at://did:xxx/app.bsky.feed.post/rkey)
  const rkey = post.uri?.split('/').pop()
  const handle = userHandle || 'costantinoai.bsky.social'
  const postUrl = `https://bsky.app/profile/${handle}/post/${rkey}`
  const date = post.created_at ? new Date(post.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  }) : ''

  // Calculate total engagement including indirect
  const totalLikes = (post.likes || 0) + (post.indirect_likes || 0)
  const totalReposts = (post.reposts || 0) + (post.indirect_reposts || 0)
  const totalReplies = (post.replies || 0) + (post.indirect_replies || 0)

  return (
    <motion.a
      href={postUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="post-card"
      whileHover={{ scale: 1.01 }}
    >
      <p className="post-text">{post.text?.slice(0, 200)}{post.text?.length > 200 ? '...' : ''}</p>
      <div className="post-meta">
        <span className="post-date font-mono">{date}</span>
        <div className="post-stats">
          <span><Heart size={14} /> {totalLikes}</span>
          <span><Repeat2 size={14} /> {totalReposts}</span>
          <span><MessageCircle size={14} /> {totalReplies}</span>
          <span><Quote size={14} /> {post.quotes || 0}</span>
          <span><Bookmark size={14} /> {post.bookmarks || 0}</span>
        </div>
      </div>
    </motion.a>
  )
}

// Expandable Section Component
function Section({ title, icon: Icon, count, children, defaultOpen = false, subtitle }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <button
        className="section-header"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className="section-title">
          <Icon size={22} strokeWidth={2} />
          <div>
            <span>{title}</span>
            {subtitle && <span className="section-subtitle">{subtitle}</span>}
          </div>
        </div>
        <div className="section-right">
          {count !== undefined && (
            <span className="section-count font-mono">{count}</span>
          )}
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown size={20} />
          </motion.div>
        </div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="section-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Chart tooltip
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null

  return (
    <div className="chart-tooltip">
      <p className="tooltip-label font-mono">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} className="tooltip-value" style={{ color: entry.color }}>
          {entry.name}: <span className="font-mono">{entry.value?.toLocaleString()}</span>
        </p>
      ))}
    </div>
  )
}

// Time range selector
function TimeRangeSelector({ value, onChange }) {
  const options = [
    { label: '7D', value: 7 },
    { label: '30D', value: 30 },
    { label: '90D', value: 90 },
    { label: '1Y', value: 365 },
    { label: 'All', value: 999999 },
  ]

  return (
    <div className="time-range-selector">
      {options.map(opt => (
        <button
          key={opt.value}
          className={`time-btn ${value === opt.value ? 'active' : ''}`}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

// Pie chart colors
const PIE_COLORS = ['#f778ba', '#3fb950', '#58a6ff', '#a371f7', '#d29922']

// Main App
export default function App() {
  const [theme, setTheme] = useState(() =>
    localStorage.getItem('theme') || 'dark'
  )
  const [timeRange, setTimeRange] = useState(30)

  // Last visit tracking
  const [lastVisit] = useState(() => getLastVisit())

  // Update last visit timestamp when app loads
  useEffect(() => {
    // Delay update so we can still show "new" badges from this session
    const timer = setTimeout(updateLastVisit, 5000)
    return () => clearTimeout(timer)
  }, [])

  // Search and sort state for each user list
  const [unfollowersSearch, setUnfollowersSearch] = useState('')
  const [unfollowersSort, setUnfollowersSort] = useState('date-desc')

  const [mutualSearch, setMutualSearch] = useState('')
  const [mutualSort, setMutualSort] = useState('name-asc')

  const [nonMutualSearch, setNonMutualSearch] = useState('')
  const [nonMutualSort, setNonMutualSort] = useState('name-asc')

  const [followersOnlySearch, setFollowersOnlySearch] = useState('')
  const [followersOnlySort, setFollowersOnlySort] = useState('name-asc')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  // Data queries
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => fetchAPI('/profile'),
  })

  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => fetchAPI('/stats'),
  })

  const { data: unfollowers } = useQuery({
    queryKey: ['unfollowers', timeRange],
    queryFn: () => fetchAPI(`/unfollowers?days=${timeRange}`),
  })

  const { data: mutualFollows } = useQuery({
    queryKey: ['mutual-follows'],
    queryFn: () => fetchAPI('/mutual-follows'),
  })

  const { data: nonMutual } = useQuery({
    queryKey: ['non-mutual'],
    queryFn: () => fetchAPI('/non-mutual'),
  })

  const { data: followersOnly } = useQuery({
    queryKey: ['followers-only'],
    queryFn: () => fetchAPI('/followers-only'),
  })

  const { data: followerGrowth } = useQuery({
    queryKey: ['follower-growth', timeRange],
    queryFn: () => fetchAPI(`/graphs/follower-growth?days=${timeRange}`),
  })

  const { data: engagementData } = useQuery({
    queryKey: ['engagement-timeline', timeRange],
    queryFn: () => fetchAPI(`/graphs/engagement-timeline?days=${timeRange}`),
  })

  const { data: engagementBalance } = useQuery({
    queryKey: ['engagement-balance', timeRange],
    queryFn: () => fetchAPI(`/engagement/balance?days=${timeRange}`),
  })

  const { data: topPosts } = useQuery({
    queryKey: ['top-posts', timeRange],
    queryFn: () => fetchAPI(`/top-posts?days=${timeRange}`),
  })

  const { data: topInteractors } = useQuery({
    queryKey: ['top-interactors', timeRange],
    queryFn: () => fetchAPI(`/top-interactors?days=${timeRange}`),
  })

  const { data: hiddenAnalytics } = useQuery({
    queryKey: ['hidden-analytics', timeRange],
    queryFn: () => fetchAPI(`/hidden-analytics?days=${timeRange}`),
  })

  const { data: statsSummary } = useQuery({
    queryKey: ['stats-summary', timeRange],
    queryFn: () => fetchAPI(`/graphs/stats-summary?days=${timeRange}`),
  })

  const { data: postingFrequency } = useQuery({
    queryKey: ['posting-frequency', timeRange],
    queryFn: () => fetchAPI(`/graphs/posting-frequency?days=${timeRange}`),
  })

  const { data: engagementBreakdown } = useQuery({
    queryKey: ['engagement-breakdown', timeRange],
    queryFn: () => fetchAPI(`/graphs/engagement-breakdown?days=${timeRange}`),
  })

  // Helper to create unified date range for all charts
  const createUnifiedChartData = useMemo(() => {
    // Collect all dates from all data sources
    const allDates = new Set()
    followerGrowth?.dates?.forEach(d => allDates.add(d))
    engagementData?.cumulative?.dates?.forEach(d => allDates.add(d))
    postingFrequency?.dates?.forEach(d => allDates.add(d))

    // Sort dates
    const sortedDates = Array.from(allDates).sort()
    if (sortedDates.length === 0) return []

    // Create lookup maps for each data source
    const followerMap = {}
    followerGrowth?.dates?.forEach((d, i) => {
      followerMap[d] = { followers: followerGrowth.followers[i], following: followerGrowth.following[i] }
    })

    const engagementMap = {}
    engagementData?.cumulative?.dates?.forEach((d, i) => {
      engagementMap[d] = {
        likes: engagementData.cumulative.likes[i] || 0,
        reposts: engagementData.cumulative.reposts[i] || 0,
        replies: engagementData.cumulative.replies[i] || 0,
      }
    })

    const postingMap = {}
    postingFrequency?.dates?.forEach((d, i) => {
      postingMap[d] = { posts: postingFrequency.posts[i] || 0 }
    })

    // Merge into unified data with forward-fill for missing values
    let lastFollower = { followers: null, following: null }
    let lastEngagement = { likes: 0, reposts: 0, replies: 0 }

    return sortedDates.map(date => {
      if (followerMap[date]) lastFollower = followerMap[date]
      if (engagementMap[date]) lastEngagement = engagementMap[date]

      return {
        date,
        dateLabel: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        ...lastFollower,
        ...lastEngagement,
        posts: postingMap[date]?.posts || 0,
      }
    })
  }, [followerGrowth, engagementData, postingFrequency])

  // Prepare chart data from unified source
  const growthChartData = createUnifiedChartData.map(d => ({
    date: d.dateLabel,
    followers: d.followers,
    following: d.following,
  })).filter(d => d.followers !== null)

  const engagementChartData = createUnifiedChartData.map(d => ({
    date: d.dateLabel,
    likes: d.likes,
    reposts: d.reposts,
    replies: d.replies,
  }))

  const postingChartData = createUnifiedChartData.map(d => ({
    date: d.dateLabel,
    posts: d.posts,
  }))

  const pieChartData = engagementBreakdown?.labels?.map((label, i) => ({
    name: label,
    value: engagementBreakdown.values[i] || 0,
  })).filter(d => d.value > 0) || []

  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshModal, setRefreshModal] = useState({
    isOpen: false,
    status: 'idle', // idle, running, done
    error: null,
    steps: []
  })

  // Sort options for user lists
  const userSortOptions = [
    { value: 'name-asc', label: 'Name A-Z' },
    { value: 'name-desc', label: 'Name Z-A' },
    { value: 'handle-asc', label: 'Handle A-Z' },
    { value: 'handle-desc', label: 'Handle Z-A' },
  ]

  const unfollowerSortOptions = [
    { value: 'date-desc', label: 'Most Recent' },
    { value: 'date-asc', label: 'Oldest First' },
    ...userSortOptions,
  ]

  // Filter and sort users helper
  const filterAndSortUsers = (users, search, sort) => {
    if (!users) return []

    let filtered = users.filter(user => {
      if (!search) return true
      const query = search.toLowerCase()
      const name = (user.display_name || '').toLowerCase()
      const handle = (user.handle || '').toLowerCase()
      return name.includes(query) || handle.includes(query)
    })

    return filtered.sort((a, b) => {
      switch (sort) {
        case 'name-asc':
          return (a.display_name || a.handle).localeCompare(b.display_name || b.handle)
        case 'name-desc':
          return (b.display_name || b.handle).localeCompare(a.display_name || a.handle)
        case 'handle-asc':
          return (a.handle || '').localeCompare(b.handle || '')
        case 'handle-desc':
          return (b.handle || '').localeCompare(a.handle || '')
        case 'date-desc':
          return new Date(b.date || b.change_date || 0) - new Date(a.date || a.change_date || 0)
        case 'date-asc':
          return new Date(a.date || a.change_date || 0) - new Date(b.date || b.change_date || 0)
        default:
          return 0
      }
    })
  }

  // Memoized filtered lists
  const filteredUnfollowers = useMemo(
    () => filterAndSortUsers(unfollowers?.unfollowers, unfollowersSearch, unfollowersSort),
    [unfollowers, unfollowersSearch, unfollowersSort]
  )

  const filteredMutual = useMemo(
    () => filterAndSortUsers(mutualFollows?.accounts, mutualSearch, mutualSort),
    [mutualFollows, mutualSearch, mutualSort]
  )

  const filteredNonMutual = useMemo(
    () => filterAndSortUsers(nonMutual?.accounts, nonMutualSearch, nonMutualSort),
    [nonMutual, nonMutualSearch, nonMutualSort]
  )

  const filteredFollowersOnly = useMemo(
    () => filterAndSortUsers(followersOnly?.accounts, followersOnlySearch, followersOnlySort),
    [followersOnly, followersOnlySearch, followersOnlySort]
  )

  const handleRefresh = async () => {
    setIsRefreshing(true)
    setRefreshModal({
      isOpen: true,
      status: 'running',
      error: null,
      steps: [
        { label: 'Starting data collection...', status: 'running' },
        { label: 'Fetching followers & following', status: 'pending' },
        { label: 'Analyzing changes', status: 'pending' },
        { label: 'Updating metrics', status: 'pending' },
      ]
    })

    try {
      // Step 1: Start collection
      setRefreshModal(m => ({
        ...m,
        steps: m.steps.map((s, i) => ({
          ...s,
          status: i === 0 ? 'done' : i === 1 ? 'running' : 'pending'
        }))
      }))

      const res = await fetch('/api/collect', { method: 'POST' })
      const data = await res.json()

      if (!data.success) {
        throw new Error(data.message || 'Collection failed')
      }

      // Step 2: Fetching complete
      setRefreshModal(m => ({
        ...m,
        steps: m.steps.map((s, i) => ({
          ...s,
          status: i <= 1 ? 'done' : i === 2 ? 'running' : 'pending'
        }))
      }))

      // Step 3: Analyzing
      await new Promise(r => setTimeout(r, 500))
      setRefreshModal(m => ({
        ...m,
        steps: m.steps.map((s, i) => ({
          ...s,
          status: i <= 2 ? 'done' : 'running'
        }))
      }))

      // Refetch all data
      await refetchStats()

      // Step 4: Done
      setRefreshModal(m => ({
        ...m,
        status: 'done',
        steps: m.steps.map(s => ({ ...s, status: 'done' }))
      }))

    } catch (e) {
      console.error('Refresh failed:', e)
      setRefreshModal(m => ({
        ...m,
        status: 'done',
        error: e.message || 'Failed to refresh data',
        steps: m.steps.map(s =>
          s.status === 'running' ? { ...s, status: 'error' } : s
        )
      }))
    } finally {
      setIsRefreshing(false)
    }
  }

  const closeRefreshModal = () => {
    setRefreshModal(m => ({ ...m, isOpen: false }))
  }

  const followerChange = (stats?.new_followers_30d || 0) - (stats?.unfollowers_30d || 0)
  const hidden = hiddenAnalytics?.current

  return (
    <div className="app grid-bg">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <Zap size={28} strokeWidth={2.5} />
          </div>
          <div className="header-titles">
            <h1 className="font-display">Bluesky Tracker</h1>
            <p className="header-handle font-mono">@{profile?.handle || 'loading...'}</p>
          </div>
        </div>
        <div className="header-right">
          <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
          <button
            className="icon-btn"
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button
            className={`refresh-btn ${isRefreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw size={16} className={isRefreshing ? 'spin' : ''} />
            <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </header>

      <main className="main">
        {/* Stats Grid */}
        <div className="stats-grid">
          <StatCard
            icon={Users}
            label="Followers"
            value={stats?.follower_count}
            change={followerChange}
            color="var(--accent-cyan)"
            delay={0}
          />
          <StatCard
            icon={UserPlus}
            label="Following"
            value={stats?.following_count}
            color="var(--accent-blue)"
            delay={0.05}
          />
          <StatCard
            icon={Heart}
            label="Mutual"
            value={mutualFollows?.count}
            color="var(--accent-pink)"
            delay={0.1}
          />
          <StatCard
            icon={EyeOff}
            label="Non-Mutual"
            value={stats?.non_mutual_following}
            color="var(--accent-orange)"
            delay={0.15}
          />
          <StatCard
            icon={Eye}
            label="Fans"
            value={stats?.followers_only}
            color="var(--accent-purple)"
            delay={0.2}
          />
        </div>

        {/* Engagement Balance */}
        {engagementBalance && (
          <motion.div
            className="balance-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <h3 className="chart-title">
              <BarChart3 size={18} />
              Engagement Balance
              <span className="chart-subtitle">Comparing what you give vs what you receive</span>
            </h3>
            <div className="balance-grid">
              <div className="balance-side given">
                <h4>Given (Outgoing)</h4>
                <div className="balance-stats">
                  <div className="balance-stat">
                    <Heart size={16} />
                    <span>Likes</span>
                    <span className="font-mono">{engagementBalance.given?.likes?.toLocaleString() || 0}</span>
                  </div>
                  <div className="balance-stat">
                    <Repeat2 size={16} />
                    <span>Reposts</span>
                    <span className="font-mono">{engagementBalance.given?.reposts?.toLocaleString() || 0}</span>
                  </div>
                  <div className="balance-stat">
                    <MessageCircle size={16} />
                    <span>Replies</span>
                    <span className="font-mono">{engagementBalance.given?.replies?.toLocaleString() || 0}</span>
                  </div>
                </div>
                <div className="balance-total">
                  <span>Total</span>
                  <span className="font-mono">{engagementBalance.given?.total?.toLocaleString() || 0}</span>
                </div>
              </div>

              <div className="balance-ratio">
                <div className="ratio-circle">
                  <span className="ratio-value font-mono">
                    {engagementBalance.ratio?.toFixed(2) || '—'}
                  </span>
                  <span className="ratio-label">ratio</span>
                </div>
                <p className="ratio-hint">
                  {engagementBalance.ratio > 1 ? 'You give more' : engagementBalance.ratio < 1 ? 'You receive more' : 'Balanced'}
                </p>
              </div>

              <div className="balance-side received">
                <h4>Received (Incoming)</h4>
                <div className="balance-stats">
                  <div className="balance-stat">
                    <Heart size={16} />
                    <span>Likes</span>
                    <span className="font-mono">{engagementBalance.received?.likes?.toLocaleString() || 0}</span>
                  </div>
                  <div className="balance-stat">
                    <Repeat2 size={16} />
                    <span>Reposts</span>
                    <span className="font-mono">{engagementBalance.received?.reposts?.toLocaleString() || 0}</span>
                  </div>
                  <div className="balance-stat">
                    <MessageCircle size={16} />
                    <span>Replies</span>
                    <span className="font-mono">{engagementBalance.received?.replies?.toLocaleString() || 0}</span>
                  </div>
                </div>
                <div className="balance-total">
                  <span>Total</span>
                  <span className="font-mono">{engagementBalance.received?.total?.toLocaleString() || 0}</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Historical Analytics Section */}
        <Section
          title="Historical Analytics"
          icon={TrendingUp}
          subtitle="Tracking trends over time"
          defaultOpen={true}
        >
          {/* Stats Summary Row */}
          {statsSummary && (
            <div className="stats-summary-grid">
              <MiniStatCard label="Days Tracked" value={statsSummary.daysTracked || 0} color="var(--accent-blue)" icon={Calendar} />
              <MiniStatCard label="Follower Δ" value={`${statsSummary.followerChange >= 0 ? '+' : ''}${statsSummary.followerChange || 0}`} color="var(--accent-green)" icon={TrendingUp} />
              <MiniStatCard label="Total Posts" value={statsSummary.totalPosts || 0} color="var(--accent-orange)" icon={FileText} />
              <MiniStatCard label="Avg Engagement" value={(statsSummary.avgEngagementPerPost || 0).toFixed(1)} color="var(--accent-purple)" icon={Activity} />
              <MiniStatCard label="Likes Δ" value={`${statsSummary.likesChange >= 0 ? '+' : ''}${statsSummary.likesChange || 0}`} color="var(--accent-pink)" icon={Heart} />
              <MiniStatCard label="Reposts Δ" value={`${statsSummary.repostsQuotesChange >= 0 ? '+' : ''}${statsSummary.repostsQuotesChange || 0}`} color="var(--accent-cyan)" icon={Repeat2} />
              <MiniStatCard label="Replies Δ" value={`${statsSummary.repliesChange >= 0 ? '+' : ''}${statsSummary.repliesChange || 0}`} color="var(--accent-blue)" icon={MessageCircle} />
              <MiniStatCard label="Saves Δ" value={`${statsSummary.savesChange >= 0 ? '+' : ''}${statsSummary.savesChange || 0}`} color="var(--accent-purple)" icon={Bookmark} />
            </div>
          )}

          {/* Charts Grid */}
          <div className="charts-grid">
            <div className="chart-card">
              <h3 className="chart-title">
                <TrendingUp size={18} />
                Network Growth
              </h3>
              <div className="chart-container">
                {growthChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <AreaChart data={growthChartData}>
                      <defs>
                        <linearGradient id="gradFollowers" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gradFollowing" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--accent-orange)" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="var(--accent-orange)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                      <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={{ stroke: 'var(--border-subtle)' }} />
                      <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={false} domain={['dataMin - 5', 'dataMax + 5']} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Area type="monotone" dataKey="followers" stroke="var(--accent-cyan)" strokeWidth={2} fill="url(#gradFollowers)" name="Followers" />
                      <Area type="monotone" dataKey="following" stroke="var(--accent-orange)" strokeWidth={2} fill="url(#gradFollowing)" name="Following" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="chart-empty">No data available</div>
                )}
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">
                <Activity size={18} />
                Engagement Timeline
              </h3>
              <div className="chart-container">
                {engagementChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={engagementChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                      <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={{ stroke: 'var(--border-subtle)' }} />
                      <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Line type="monotone" dataKey="likes" stroke="var(--accent-pink)" strokeWidth={2} dot={false} name="Likes" />
                      <Line type="monotone" dataKey="reposts" stroke="var(--accent-green)" strokeWidth={2} dot={false} name="Reposts" />
                      <Line type="monotone" dataKey="replies" stroke="var(--accent-blue)" strokeWidth={2} dot={false} name="Replies" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="chart-empty">No data available</div>
                )}
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">
                <PieChartIcon size={18} />
                Engagement Distribution
              </h3>
              <div className="chart-container">
                {pieChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="chart-empty">No engagement data yet</div>
                )}
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">
                <FileText size={18} />
                Posting Activity
              </h3>
              <div className="chart-container">
                {postingChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={postingChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                      <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={{ stroke: 'var(--border-subtle)' }} />
                      <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="posts" fill="var(--accent-purple)" radius={[4, 4, 0, 0]} name="Posts" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="chart-empty">No posting data yet</div>
                )}
              </div>
            </div>
          </div>
        </Section>

        {/* Top Posts */}
        <Section
          title="Top Posts"
          icon={Star}
          count={topPosts?.posts?.length || 0}
          subtitle="Your most engaging content"
        >
          {topPosts?.posts?.length > 0 ? (
            <div className="posts-grid">
              {topPosts.posts.slice(0, 10).map((post, i) => (
                <PostCard key={post.uri || i} post={post} userHandle={profile?.handle} />
              ))}
            </div>
          ) : (
            <p className="empty-state">No posts tracked yet</p>
          )}
        </Section>

        {/* Top Interactors */}
        <Section
          title="Top Interactors"
          icon={Users}
          count={topInteractors?.interactors?.length || 0}
          subtitle="People who engage most with your content"
        >
          {topInteractors?.interactors?.length > 0 ? (
            <div className="interactors-grid">
              {topInteractors.interactors.slice(0, 20).map((user, i) => (
                <InteractorCard key={user.did || i} user={user} />
              ))}
            </div>
          ) : (
            <p className="empty-state">No interactors tracked yet</p>
          )}
        </Section>

        {/* Hidden Accounts Analysis */}
        {hidden && (hidden.suspected_blocks_or_suspensions > 0 || hidden.blocked_count > 0) && (
          <Section
            title="Hidden Accounts"
            icon={Shield}
            count={hidden.hidden_followers || 0}
            subtitle="Accounts filtered from the API"
          >
            <div className="hidden-grid">
              <div className="hidden-stat-card">
                <div className="hidden-stat-value font-mono">{hidden.profile_followers || 0}</div>
                <div className="hidden-stat-label">Profile Shows</div>
              </div>
              <div className="hidden-stat-card">
                <div className="hidden-stat-value font-mono">{hidden.api_followers || 0}</div>
                <div className="hidden-stat-label">API Returns</div>
              </div>
              <div className="hidden-stat-card accent">
                <div className="hidden-stat-value font-mono">{hidden.hidden_followers || 0}</div>
                <div className="hidden-stat-label">Hidden</div>
              </div>
            </div>

            <div className="hidden-breakdown">
              {hidden.blocked_count > 0 && (
                <div className="hidden-item">
                  <Ban size={16} />
                  <span>You blocked: <strong>{hidden.blocked_count}</strong></span>
                </div>
              )}
              {hidden.muted_count > 0 && (
                <div className="hidden-item">
                  <EyeOff size={16} />
                  <span>You muted: <strong>{hidden.muted_count}</strong></span>
                </div>
              )}
              {hidden.suspected_blocks_or_suspensions > 0 && (
                <div className="hidden-item warning">
                  <AlertTriangle size={16} />
                  <span>Blocked you / Deactivated / Suspended: <strong>{hidden.suspected_blocks_or_suspensions}</strong></span>
                </div>
              )}
            </div>

            <p className="hidden-note">
              These accounts are in your follower count but not returned by the API.
              This includes deactivated accounts, suspended users, and people who blocked you.
            </p>
          </Section>
        )}

        {/* Unfollowers */}
        <Section
          title="Recent Unfollowers"
          icon={UserMinus}
          count={unfollowers?.unfollowers?.length || 0}
          defaultOpen={true}
        >
          <ListToolbar
            searchValue={unfollowersSearch}
            onSearch={setUnfollowersSearch}
            sortValue={unfollowersSort}
            onSort={setUnfollowersSort}
            sortOptions={unfollowerSortOptions}
            exportData={unfollowers?.unfollowers}
            exportName="unfollowers"
          />
          <div className="user-grid">
            {filteredUnfollowers.length > 0 ? (
              filteredUnfollowers.map((user, i) => (
                <UserCard
                  key={user.did || i}
                  user={user}
                  meta={user.date}
                  isNew={isNewSinceLastVisit(user.date || user.change_date, lastVisit)}
                />
              ))
            ) : unfollowers?.unfollowers?.length > 0 ? (
              <p className="empty-state">No matches found</p>
            ) : (
              <p className="empty-state">No unfollowers in this period</p>
            )}
          </div>
        </Section>

        {/* Mutual Follows */}
        <Section
          title="Mutual Follows"
          icon={Heart}
          count={mutualFollows?.count || 0}
        >
          <ListToolbar
            searchValue={mutualSearch}
            onSearch={setMutualSearch}
            sortValue={mutualSort}
            onSort={setMutualSort}
            sortOptions={userSortOptions}
            exportData={mutualFollows?.accounts}
            exportName="mutual-follows"
          />
          <div className="user-grid">
            {filteredMutual.slice(0, 50).map((user, i) => (
              <UserCard key={user.did || i} user={user} />
            ))}
          </div>
          {filteredMutual.length > 50 && (
            <p className="more-indicator">+{filteredMutual.length - 50} more</p>
          )}
          {filteredMutual.length === 0 && mutualFollows?.accounts?.length > 0 && (
            <p className="empty-state">No matches found</p>
          )}
        </Section>

        {/* Non-Mutual */}
        <Section
          title="Not Following Back"
          icon={EyeOff}
          count={nonMutual?.count || 0}
          subtitle="People you follow who don't follow you"
        >
          <ListToolbar
            searchValue={nonMutualSearch}
            onSearch={setNonMutualSearch}
            sortValue={nonMutualSort}
            onSort={setNonMutualSort}
            sortOptions={userSortOptions}
            exportData={nonMutual?.accounts}
            exportName="non-mutual"
          />
          <div className="user-grid">
            {filteredNonMutual.slice(0, 50).map((user, i) => (
              <UserCard key={user.did || i} user={user} />
            ))}
          </div>
          {filteredNonMutual.length > 50 && (
            <p className="more-indicator">+{filteredNonMutual.length - 50} more</p>
          )}
          {filteredNonMutual.length === 0 && nonMutual?.accounts?.length > 0 && (
            <p className="empty-state">No matches found</p>
          )}
        </Section>

        {/* Followers Only */}
        <Section
          title="Followers Only"
          icon={Eye}
          count={followersOnly?.count || 0}
          subtitle="People who follow you but you don't follow back"
        >
          <ListToolbar
            searchValue={followersOnlySearch}
            onSearch={setFollowersOnlySearch}
            sortValue={followersOnlySort}
            onSort={setFollowersOnlySort}
            sortOptions={userSortOptions}
            exportData={followersOnly?.accounts}
            exportName="followers-only"
          />
          <div className="user-grid">
            {filteredFollowersOnly.slice(0, 50).map((user, i) => (
              <UserCard key={user.did || i} user={user} />
            ))}
          </div>
          {filteredFollowersOnly.length > 50 && (
            <p className="more-indicator">+{filteredFollowersOnly.length - 50} more</p>
          )}
          {filteredFollowersOnly.length === 0 && followersOnly?.accounts?.length > 0 && (
            <p className="empty-state">No matches found</p>
          )}
        </Section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p className="font-mono">Bluesky Tracker • Built with data from the AT Protocol</p>
      </footer>

      {/* Refresh Modal */}
      <RefreshModal
        isOpen={refreshModal.isOpen}
        status={refreshModal.status}
        steps={refreshModal.steps}
        error={refreshModal.error}
        onClose={closeRefreshModal}
      />
    </div>
  )
}
