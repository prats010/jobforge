import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, Loader2, ChevronDown, ChevronUp,
  Sparkles, BookOpen, Eye, EyeOff
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/client'
import CustomSelect from '../components/CustomSelect'

function StoryCard({ story, index }) {
  const [expanded, setExpanded] = useState(false)
  const [practiceMode, setPracticeMode] = useState(false)
  const [revealed, setRevealed] = useState({
    situation: false, task: false, action: false, result: false, reflection: false,
  })

  const revealNext = () => {
    const order = ['situation', 'task', 'action', 'result', 'reflection']
    for (const key of order) {
      if (!revealed[key]) {
        setRevealed((prev) => ({ ...prev, [key]: true }))
        return
      }
    }
  }

  const sections = [
    { key: 'situation', label: 'Situation', color: '#3b82f6' },
    { key: 'task', label: 'Task', color: '#a855f7' },
    { key: 'action', label: 'Action', color: '#00FF87' },
    { key: 'result', label: 'Result', color: '#ffd600' },
    { key: 'reflection', label: 'Reflection', color: '#f97316' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="glass-card overflow-hidden"
    >
      {/* Question Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 hover:bg-dark-700/30 transition-colors"
      >
        <div className="w-8 h-8 rounded-lg bg-forge-400/10 border border-forge-400/30 flex items-center justify-center flex-shrink-0">
          <span className="text-xs font-mono font-bold text-forge-400">{index + 1}</span>
        </div>
        <p className="text-sm font-medium text-white text-left flex-1">{story.question}</p>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-dark-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-dark-400" />
        )}
      </button>

      {/* Story Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-dark-600/30"
          >
            {/* Practice Mode Toggle */}
            <div className="px-4 py-2 flex items-center gap-2 border-b border-dark-700/30 bg-dark-800/30">
              <button
                onClick={() => {
                  setPracticeMode(!practiceMode)
                  setRevealed({ situation: false, task: false, action: false, result: false, reflection: false })
                }}
                className={`btn-ghost text-xs flex items-center gap-1 ${practiceMode ? 'text-forge-400' : ''}`}
              >
                {practiceMode ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                {practiceMode ? 'Exit Practice' : 'Practice Mode'}
              </button>
              {practiceMode && (
                <button onClick={revealNext} className="btn-ghost text-xs text-forge-400">
                  Reveal Next →
                </button>
              )}
            </div>

            <div className="p-4 space-y-3">
              {sections.map((section) => {
                const show = !practiceMode || revealed[section.key]
                return (
                  <div key={section.key}>
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: section.color }} />
                      <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: section.color }}>
                        {section.label}
                      </span>
                    </div>
                    {show ? (
                      <p className="text-sm text-dark-200 leading-relaxed pl-4">
                        {story[section.key]}
                      </p>
                    ) : (
                      <div className="pl-4 py-2">
                        <div className="skeleton h-4 w-full mb-1" />
                        <div className="skeleton h-4 w-3/4" />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function InterviewPrep() {
  const queryClient = useQueryClient()
  const [selectedJobId, setSelectedJobId] = useState('')

  // Fetch evaluated jobs
  const { data: jobs } = useQuery({
    queryKey: ['evaluatedJobsInterview'],
    queryFn: () => api.get('/jobs?limit=100').then((r) => r.data),
  })

  const evaluatedJobs = jobs?.filter((j) => j.score_letter) || []
  const selectedJob = evaluatedJobs.find((j) => j.id === Number(selectedJobId))

  // Fetch existing stories
  const { data: existingStories } = useQuery({
    queryKey: ['stories', selectedJobId],
    queryFn: () => api.get(`/interview/stories/${selectedJobId}`).then((r) => r.data),
    enabled: !!selectedJobId,
    retry: false,
  })

  // Generate stories mutation
  const generateMutation = useMutation({
    mutationFn: (jobId) => api.post(`/interview/generate/${jobId}`).then((r) => r.data),
    onSuccess: () => {
      toast.success('STAR stories generated!')
      queryClient.invalidateQueries({ queryKey: ['stories', selectedJobId] })
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Generation failed'),
  })

  const stories = existingStories?.stories || generateMutation.data?.stories || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <MessageSquare className="w-7 h-7 text-forge-400" />
          Interview Prep
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          STAR+Reflection stories tailored to your experience
        </p>
      </div>

      {/* Job Selector */}
      <div className="glass-card p-4 flex items-center gap-4 flex-wrap relative hover:z-50 focus-within:z-50">
        <CustomSelect
          value={selectedJobId}
          onChange={setSelectedJobId}
          options={evaluatedJobs.map((job) => ({
            value: String(job.id),
            label: `[${job.score_letter}] ${job.title} — ${job.company}`
          }))}
          placeholder="Select a job for interview prep..."
          className="w-full max-w-md"
        />

        <button
          onClick={() => generateMutation.mutate(Number(selectedJobId))}
          disabled={!selectedJobId || generateMutation.isPending}
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          {generateMutation.isPending ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
          ) : (
            <><Sparkles className="w-4 h-4" /> Generate STAR Stories</>
          )}
        </button>
      </div>

      {/* Loading */}
      {generateMutation.isPending && (
        <div className="glass-card p-8 flex flex-col items-center">
          <Loader2 className="w-8 h-8 text-forge-400 animate-spin mb-3" />
          <p className="text-white font-medium">Generating interview stories...</p>
          <p className="text-xs text-dark-400 mt-1">Using your resume + job description</p>
        </div>
      )}

      {/* Stories */}
      {stories.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-forge-400" />
            <span className="text-sm font-semibold text-white">{stories.length} Stories Generated</span>
          </div>
          {stories.map((story, i) => (
            <StoryCard key={i} story={story} index={i} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!selectedJobId && !generateMutation.isPending && stories.length === 0 && (
        <div className="glass-card p-12 flex flex-col items-center">
          <MessageSquare className="w-12 h-12 text-dark-400 mb-4" />
          <h3 className="text-lg font-semibold text-white">Interview Prep</h3>
          <p className="text-sm text-dark-400 text-center mt-2 max-w-sm">
            Select a job and generate tailored STAR stories based on your experience and the job requirements
          </p>
        </div>
      )}
    </div>
  )
}
