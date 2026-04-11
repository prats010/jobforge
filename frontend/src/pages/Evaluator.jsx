import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Send, Loader2, CheckCircle2, AlertCircle,
  Lightbulb, Target, FileText, ArrowRight, Sparkles
} from 'lucide-react'
import toast from 'react-hot-toast'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import api from '../api/client'
import ScoreBar from '../components/ScoreBar'
import JobCard from '../components/JobCard'
import { SkeletonList } from '../components/LoadingSpinner'

const dimensionLabels = {
  technical_skills_match: 'Technical Skills',
  domain_alignment: 'Domain Alignment',
  experience_level_fit: 'Experience Fit',
  project_portfolio_relevance: 'Portfolio Relevance',
  growth_potential: 'Growth Potential',
  company_quality: 'Company Quality',
  location_remote_compatibility: 'Location Match',
  compensation_estimate: 'Compensation',
  tech_stack_modernity: 'Tech Modernity',
  application_success_probability: 'Success Probability',
}

const dimColors = [
  '#00FF87', '#00bcd4', '#a855f7', '#ffd600', '#f97316',
  '#f43f5e', '#22d3ee', '#84cc16', '#e879f9', '#64748b',
]

export default function Evaluator() {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState('paste') // 'paste' or 'saved'
  const [jdText, setJdText] = useState('')
  const [jdTitle, setJdTitle] = useState('')
  const [jdCompany, setJdCompany] = useState('')
  const [result, setResult] = useState(null)

  // Fetch unevaluated jobs
  const { data: savedJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['unevaluatedJobs'],
    queryFn: () => api.get('/jobs?limit=50').then((r) => r.data),
  })

  const unevaluatedJobs = savedJobs?.filter((j) => !j.score_letter) || []

  // Paste-and-evaluate mutation
  const pasteMutation = useMutation({
    mutationFn: (data) => api.post('/evaluator/paste-evaluate', data).then((r) => r.data),
    onSuccess: (data) => {
      setResult(data)
      toast.success(`Evaluation: ${data.letter_grade} (${data.numeric_score.toFixed(1)}/5.0)`)
      queryClient.invalidateQueries({ queryKey: ['unevaluatedJobs'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Evaluation failed')
    },
  })

  // Evaluate saved job mutation
  const evalMutation = useMutation({
    mutationFn: (jobId) => api.post(`/evaluator/evaluate/${jobId}`).then((r) => r.data),
    onSuccess: (data) => {
      setResult(data)
      toast.success(`Evaluation: ${data.letter_grade} (${data.numeric_score.toFixed(1)}/5.0)`)
      queryClient.invalidateQueries({ queryKey: ['unevaluatedJobs'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Evaluation failed')
    },
  })

  const handlePasteEvaluate = () => {
    if (!jdText.trim()) {
      toast.error('Paste a job description first')
      return
    }
    pasteMutation.mutate({
      title: jdTitle || null,
      company: jdCompany || null,
      jd_text: jdText,
    })
  }

  const isLoading = pasteMutation.isPending || evalMutation.isPending

  // Prepare dimension chart data
  const dimData = result?.dimensions
    ? Object.entries(result.dimensions).map(([key, val], i) => ({
        name: dimensionLabels[key] || key.replace(/_/g, ' '),
        score: val,
        fill: dimColors[i % dimColors.length],
      }))
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Brain className="w-7 h-7 text-forge-400" />
          Job Evaluator
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          AI-powered job match scoring with 10-dimension analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel — Input */}
        <div className="space-y-4">
          {/* Mode Toggle */}
          <div className="glass-card p-1 flex gap-1">
            <button
              onClick={() => setMode('paste')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                mode === 'paste'
                  ? 'bg-forge-400/15 text-forge-400 border border-forge-400/30'
                  : 'text-dark-300 hover:text-white'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Paste JD
            </button>
            <button
              onClick={() => setMode('saved')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                mode === 'saved'
                  ? 'bg-forge-400/15 text-forge-400 border border-forge-400/30'
                  : 'text-dark-300 hover:text-white'
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Saved Jobs
            </button>
          </div>

          {mode === 'paste' ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  placeholder="Job title (optional, AI extracts)"
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  value={jdCompany}
                  onChange={(e) => setJdCompany(e.target.value)}
                  placeholder="Company (optional)"
                  className="input-field text-sm"
                />
              </div>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the full job description here...&#10;&#10;The AI will extract the title, company, and all details automatically, then score the match against your resume across 10 dimensions."
                className="input-field text-sm min-h-[350px] resize-y font-mono"
              />
              <button
                onClick={handlePasteEvaluate}
                disabled={isLoading || !jdText.trim()}
                className="btn-primary w-full py-3 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Evaluate Match
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="glass-card p-4">
              <h3 className="text-sm font-semibold text-white mb-3">
                Unevaluated Jobs ({unevaluatedJobs.length})
              </h3>
              {jobsLoading ? (
                <SkeletonList count={3} />
              ) : unevaluatedJobs.length > 0 ? (
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
                  {unevaluatedJobs.map((job) => (
                    <div key={job.id} className="flex items-center gap-2">
                      <div className="flex-1">
                        <JobCard job={job} compact />
                      </div>
                      <button
                        onClick={() => evalMutation.mutate(job.id)}
                        disabled={isLoading}
                        className="btn-primary text-xs px-3 py-1.5 flex-shrink-0"
                      >
                        Evaluate
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-dark-400 text-sm py-8 text-center">
                  All jobs evaluated! Run the scanner to find more.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Right Panel — Results */}
        <div>
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass-card p-8 flex flex-col items-center justify-center min-h-[400px]"
              >
                <div className="w-16 h-16 rounded-2xl bg-forge-400/10 border border-forge-400/30 flex items-center justify-center mb-4">
                  <Loader2 className="w-8 h-8 text-forge-400 animate-spin" />
                </div>
                <p className="text-white font-medium">Analyzing with Groq Llama 3...</p>
                <p className="text-xs text-dark-400 mt-1">Comparing against your resume</p>
                <div className="flex gap-1 mt-4">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      animate={{ y: [0, -6, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                      className="w-2 h-2 rounded-full bg-forge-400"
                    />
                  ))}
                </div>
              </motion.div>
            ) : result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {/* Score Card */}
                <div className="glass-card p-6 glow-border">
                  <ScoreBar letter={result.letter_grade} numeric={result.numeric_score} />
                  <p className="text-sm text-dark-200 mt-3 italic">
                    "{result.one_liner}"
                  </p>
                </div>

                {/* 10-Dimension Breakdown */}
                <div className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-white mb-3">10-Dimension Analysis</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dimData} layout="vertical" margin={{ left: 120 }}>
                      <XAxis type="number" domain={[0, 5]} stroke="#475569" fontSize={10} fontFamily="JetBrains Mono" />
                      <YAxis type="category" dataKey="name" stroke="#475569" fontSize={10} width={120} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1a1a2e',
                          border: '1px solid rgba(71,85,105,0.5)',
                          borderRadius: '8px',
                          fontSize: '12px',
                          fontFamily: 'JetBrains Mono',
                        }}
                        formatter={(val) => [`${val.toFixed(1)} / 5.0`]}
                      />
                      <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                        {dimData.map((entry, index) => (
                          <Cell key={index} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Strengths & Gaps */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="glass-card p-4">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Strengths
                    </h4>
                    <ul className="space-y-1.5">
                      {result.strengths?.map((s, i) => (
                        <li key={i} className="text-xs text-dark-200 flex items-start gap-2">
                          <span className="text-emerald-400 mt-0.5">•</span> {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="glass-card p-4">
                    <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <AlertCircle className="w-3.5 h-3.5" /> Gaps
                    </h4>
                    <ul className="space-y-1.5">
                      {result.gaps?.map((g, i) => (
                        <li key={i} className="text-xs text-dark-200 flex items-start gap-2">
                          <span className="text-red-400 mt-0.5">•</span> {g}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Recommendation */}
                <div className="glass-card p-4">
                  <h4 className="text-xs font-semibold text-forge-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Lightbulb className="w-3.5 h-3.5" /> Recommendation
                  </h4>
                  <p className="text-sm text-dark-200 leading-relaxed">{result.recommendation}</p>
                </div>

                {/* Keywords to Add */}
                {result.keywords_to_add?.length > 0 && (
                  <div className="glass-card p-4">
                    <h4 className="text-xs font-semibold text-yellow-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <Target className="w-3.5 h-3.5" /> Keywords to Add to Resume
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.keywords_to_add.map((kw, i) => (
                        <span key={i} className="badge-yellow">{kw}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={() => window.location.href = `/cv-tailor?job=${result.job_id}`}
                    className="btn-primary flex-1 flex items-center justify-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Tailor Resume
                  </button>
                  <button
                    onClick={() => window.location.href = `/interview?job=${result.job_id}`}
                    className="btn-secondary flex-1 flex items-center justify-center gap-2"
                  >
                    <Brain className="w-4 h-4" />
                    Interview Prep
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card p-12 flex flex-col items-center justify-center min-h-[400px]"
              >
                <div className="w-20 h-20 rounded-2xl bg-dark-700/50 flex items-center justify-center mb-4">
                  <Brain className="w-10 h-10 text-dark-400" />
                </div>
                <h3 className="text-lg font-semibold text-white">Ready to Evaluate</h3>
                <p className="text-sm text-dark-400 text-center mt-2 max-w-xs">
                  Paste a job description or select a saved job to get an AI-powered match analysis
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
