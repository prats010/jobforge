import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Briefcase, Brain, Send, Users, Radar,
  FileText, ArrowRight, TrendingUp
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import api from '../api/client'
import { SkeletonCard } from '../components/LoadingSpinner'
import JobCard from '../components/JobCard'

const statCards = [
  { key: 'total_jobs', label: 'Jobs Discovered', icon: Briefcase, color: '#64748b' },
  { key: 'evaluated', label: 'Evaluated', icon: Brain, color: '#00bcd4' },
  { key: 'applied', label: 'Applied', icon: Send, color: '#ffd600' },
  { key: 'interviews', label: 'Interviews', icon: Users, color: '#00e676' },
]

const gradeColors = { A: '#00e676', B: '#00bcd4', C: '#ffd600', D: '#ff9100', F: '#ff1744' }
const DOMAIN_COLORS = ['#00FF87', '#00bcd4', '#ffd600', '#ff9100', '#a855f7', '#f43f5e', '#64748b', '#22d3ee']

export default function Dashboard() {
  const navigate = useNavigate()

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['jobStats'],
    queryFn: () => api.get('/jobs/stats').then((r) => r.data),
  })

  const { data: recentJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['recentJobs'],
    queryFn: () => api.get('/jobs?limit=8').then((r) => r.data),
  })

  // Transform score distribution for chart
  const scoreData = stats?.score_distribution
    ? ['A', 'B', 'C', 'D', 'F'].map((g) => ({
        grade: g,
        count: stats.score_distribution[g] || 0,
        fill: gradeColors[g],
      }))
    : []

  // Transform domain breakdown for pie
  const domainData = stats?.domain_breakdown
    ? Object.entries(stats.domain_breakdown).map(([name, value], i) => ({
        name,
        value,
        fill: DOMAIN_COLORS[i % DOMAIN_COLORS.length],
      }))
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-dark-300 mt-1">Your AI-powered job search command center</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-dark-400 uppercase tracking-widest">
            JobForge v1.0
          </span>
          <div className="w-2 h-2 rounded-full bg-forge-400 animate-pulse" />
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <motion.div
            key={card.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-dark-300 uppercase tracking-wider">{card.label}</p>
                <p className="text-3xl font-mono font-bold text-white mt-1">
                  {statsLoading ? '—' : stats?.[card.key] || 0}
                </p>
              </div>
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: `${card.color}15`, border: `1px solid ${card.color}30` }}
              >
                <card.icon className="w-6 h-6" style={{ color: card.color }} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-forge-400" />
            Score Distribution
          </h2>
          {scoreData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreData}>
                <XAxis dataKey="grade" stroke="#475569" fontSize={12} fontFamily="JetBrains Mono" />
                <YAxis stroke="#475569" fontSize={12} fontFamily="JetBrains Mono" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a1a2e',
                    border: '1px solid rgba(71,85,105,0.5)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'JetBrains Mono',
                    color: '#fff',
                  }}
                  itemStyle={{ color: '#fff' }}
                  labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {scoreData.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-dark-400 text-sm">
              No evaluations yet. Scan jobs and evaluate them!
            </div>
          )}
        </motion.div>

        {/* Domain Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-forge-400" />
            Domain Breakdown
          </h2>
          {domainData.length > 0 ? (
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <div className="w-full sm:w-1/2 h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={domainData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={70}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {domainData.map((entry, index) => (
                        <Cell key={index} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid rgba(71,85,105,0.5)',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: '#fff',
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-full sm:w-1/2 space-y-2">
                {domainData.map((d, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ backgroundColor: d.fill }} />
                    <span className="text-dark-200 truncate">{d.name}</span>
                    <span className="text-dark-400 font-mono ml-auto">{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-dark-400 text-sm">
              No jobs discovered yet. Run the scanner!
            </div>
          )}
        </motion.div>
      </div>

      {/* Quick Actions + Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card p-6 space-y-3"
        >
          <h2 className="text-sm font-semibold text-white mb-2">Quick Actions</h2>
          {[
            { label: 'Run Scanner', icon: Radar, path: '/scanner', desc: 'Discover new jobs' },
            { label: 'Paste JD', icon: FileText, path: '/evaluator', desc: 'Evaluate a job description' },
            { label: 'View Tracker', icon: Users, path: '/tracker', desc: 'Manage applications' },
          ].map((action) => (
            <button
              key={action.path}
              onClick={() => navigate(action.path)}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-dark-700/30 border border-dark-600/20 hover:border-forge-400/30 hover:bg-dark-700/50 transition-all duration-200 group"
            >
              <div className="w-9 h-9 rounded-lg bg-forge-400/10 flex items-center justify-center group-hover:bg-forge-400/20 transition-colors">
                <action.icon className="w-4 h-4 text-forge-400" />
              </div>
              <div className="flex-1 text-left">
                <p className="text-sm font-medium text-white">{action.label}</p>
                <p className="text-[11px] text-dark-400">{action.desc}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-dark-400 group-hover:text-forge-400 transition-colors" />
            </button>
          ))}
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="lg:col-span-2 glass-card p-6"
        >
          <h2 className="text-sm font-semibold text-white mb-4">Recent Jobs</h2>
          {jobsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : recentJobs?.length > 0 ? (
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {recentJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  compact
                  onClick={() => navigate(`/evaluator?job=${job.id}`)}
                />
              ))}
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-dark-400 text-sm">
              No jobs yet. Run the scanner to get started!
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
