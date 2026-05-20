import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Radar, Play, Loader2, CheckCircle, XCircle, AlertTriangle,
  X, Plus, Clock, Hash
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/client'
import JobCard from '../components/JobCard'
import { SkeletonList } from '../components/LoadingSpinner'

const DEFAULT_KEYWORDS = ['data scientist', 'machine learning engineer', 'AI intern', 'NLP engineer', 'MLOps', 'deep learning']

export default function Scanner() {
  const queryClient = useQueryClient()
  const [selectedSources, setSelectedSources] = useState(['greenhouse', 'lever'])
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS)
  const [newKeyword, setNewKeyword] = useState('')
  const [evaluatingJobId, setEvaluatingJobId] = useState(null)

  // Fetch sources
  const { data: sources } = useQuery({
    queryKey: ['scannerSources'],
    queryFn: () => api.get('/scanner/sources').then((r) => r.data),
  })

  // Fetch scan history
  const { data: history } = useQuery({
    queryKey: ['scanHistory'],
    queryFn: () => api.get('/scanner/history').then((r) => r.data),
  })

  // Fetch discovered jobs
  const { data: discoveredJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['discoveredJobs'],
    queryFn: () => api.get('/jobs?status=discovered&limit=50').then((r) => r.data),
  })

  // Scan mutation
  const scanMutation = useMutation({
    mutationFn: (data) => api.post('/scanner/run', data).then((r) => r.data),
    onSuccess: (data) => {
      toast.success(`Scan complete! Found ${data.jobs_found} jobs (${data.new_jobs} new)`)
      queryClient.invalidateQueries({ queryKey: ['discoveredJobs'] })
      queryClient.invalidateQueries({ queryKey: ['scanHistory'] })
      queryClient.invalidateQueries({ queryKey: ['scannerSources'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Scan failed')
    },
  })

  // Evaluate single job
  const evalMutation = useMutation({
    mutationFn: (jobId) => api.post(`/evaluator/evaluate/${jobId}`).then((r) => r.data),
    onMutate: (jobId) => setEvaluatingJobId(jobId),
    onSettled: () => setEvaluatingJobId(null),
    onSuccess: (data) => {
      toast.success(`Evaluated: ${data.letter_grade} (${data.numeric_score.toFixed(1)}/5.0)`)
      queryClient.invalidateQueries({ queryKey: ['discoveredJobs'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Evaluation failed')
    },
  })

  const toggleSource = (slug) => {
    setSelectedSources((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug]
    )
  }

  const addKeyword = () => {
    const kw = newKeyword.trim()
    if (kw && !keywords.includes(kw)) {
      setKeywords([...keywords, kw])
      setNewKeyword('')
    }
  }

  const removeKeyword = (kw) => {
    setKeywords(keywords.filter((k) => k !== kw))
  }

  const runScan = () => {
    if (selectedSources.length === 0) {
      toast.error('Select at least one source')
      return
    }
    scanMutation.mutate({ sources: selectedSources, keywords })
  }

  const sourceStatusIcon = (status) => {
    switch (status) {
      case 'ready': return <CheckCircle className="w-4 h-4 text-emerald-400" />
      case 'stub': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <CheckCircle className="w-4 h-4 text-dark-400" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Radar className="w-7 h-7 text-forge-400" />
          Portal Scanner
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          Discover DS/ML/AI jobs from multiple platforms
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel — Controls */}
        <div className="space-y-4">
          {/* Sources */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Sources</h3>
            <div className="space-y-2">
              {sources?.map((source) => (
                <label
                  key={source.slug}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedSources.includes(source.slug)
                      ? 'bg-forge-400/10 border border-forge-400/30'
                      : 'bg-dark-700/30 border border-dark-600/20 hover:border-dark-500/40'
                  } ${source.status === 'stub' ? 'opacity-60' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source.slug)}
                    onChange={() => toggleSource(source.slug)}
                    className="sr-only"
                  />
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                    selectedSources.includes(source.slug)
                      ? 'bg-forge-400 border-forge-400'
                      : 'border-dark-400'
                  }`}>
                    {selectedSources.includes(source.slug) && (
                      <CheckCircle className="w-3 h-3 text-dark-900" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">{source.name}</span>
                      {sourceStatusIcon(source.status)}
                    </div>
                    <p className="text-[11px] text-dark-400 mt-0.5">{source.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Keywords */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Search Keywords</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {keywords.map((kw) => (
                <span key={kw} className="badge-blue flex items-center gap-1 pr-1">
                  {kw}
                  <button onClick={() => removeKeyword(kw)} className="hover:text-red-400 transition-colors">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addKeyword()}
                placeholder="Add keyword..."
                className="input-field text-sm flex-1"
              />
              <button onClick={addKeyword} className="btn-secondary px-3">
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Scan Button */}
          <button
            onClick={runScan}
            disabled={scanMutation.isPending}
            className="btn-primary w-full py-3 flex items-center justify-center gap-2 text-base disabled:opacity-50"
          >
            {scanMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Scan Now
              </>
            )}
          </button>

          {/* Scan Results */}
          <AnimatePresence>
            {scanMutation.data && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="glass-card p-4 glow-border"
              >
                <h4 className="text-sm font-semibold text-forge-400 mb-2">Scan Results</h4>
                <div className="space-y-1 text-xs">
                  {scanMutation.data.details?.map((d, i) => (
                    <div key={i} className="flex items-center justify-between text-dark-200">
                      <span>{d.source}</span>
                      <span className="font-mono">
                        {d.status === 'success'
                          ? `${d.jobs_found} found, ${d.new_jobs} new`
                          : d.message || 'Error'}
                      </span>
                    </div>
                  ))}
                  <div className="border-t border-dark-600/30 pt-1 mt-1 flex justify-between font-medium text-white">
                    <span>Total</span>
                    <span className="font-mono">
                      {scanMutation.data.jobs_found} found, {scanMutation.data.new_jobs} new
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Panel — Results */}
        <div className="lg:col-span-2 space-y-4">
          {/* Discovered Jobs */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Hash className="w-4 h-4 text-forge-400" />
                Discovered Jobs
                {discoveredJobs?.length > 0 && (
                  <span className="badge-green">{discoveredJobs.length}</span>
                )}
              </h3>
            </div>

            {jobsLoading ? (
              <SkeletonList count={4} />
            ) : discoveredJobs?.length > 0 ? (
              <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
                {discoveredJobs.map((job) => (
                  <div key={job.id} className="flex items-center gap-2">
                    <div className="flex-1 min-w-0">
                      <JobCard job={job} compact />
                    </div>
                    {!job.score_letter && (
                      <button
                        onClick={() => evalMutation.mutate(job.id)}
                        disabled={evalMutation.isPending}
                        className="btn-secondary text-xs px-3 py-1.5 flex-shrink-0 min-w-[70px]"
                      >
                        {evalMutation.isPending && evaluatingJobId === job.id ? (
                          <Loader2 className="w-3 h-3 animate-spin mx-auto" />
                        ) : (
                          'Evaluate'
                        )}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-40 flex items-center justify-center text-dark-400 text-sm">
                No jobs discovered yet. Run a scan!
              </div>
            )}
          </div>

          {/* Scan History */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-dark-300" />
              Scan History
            </h3>
            {history?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-dark-300 border-b border-dark-600/30">
                      <th className="text-left py-2 px-2 font-medium">Date</th>
                      <th className="text-left py-2 px-2 font-medium">Sources</th>
                      <th className="text-right py-2 px-2 font-medium">Found</th>
                      <th className="text-right py-2 px-2 font-medium">New</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((s) => (
                      <tr key={s.id} className="border-b border-dark-700/30 text-dark-200">
                        <td className="py-2 px-2 font-mono">
                          {new Date(s.ran_at).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
                        </td>
                        <td className="py-2 px-2">{s.source}</td>
                        <td className="py-2 px-2 text-right font-mono">{s.jobs_found}</td>
                        <td className="py-2 px-2 text-right font-mono text-forge-400">{s.new_jobs}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-dark-400 text-sm">No scans yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
