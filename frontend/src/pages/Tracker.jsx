import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Kanban, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/client'
import ScoreBar from '../components/ScoreBar'

const COLUMNS = [
  { id: 'discovered', label: 'Discovered', color: '#64748b' },
  { id: 'evaluating', label: 'Evaluating', color: '#3b82f6' },
  { id: 'shortlisted', label: 'Shortlisted', color: '#a855f7' },
  { id: 'applied', label: 'Applied', color: '#ffd600' },
  { id: 'interview', label: 'Interview', color: '#f97316' },
  { id: 'offer', label: 'Offer', color: '#00e676' },
  { id: 'rejected', label: 'Rejected', color: '#ff1744' },
]

function TrackerJobCard({ job, onMove }) {
  return (
    <div className="glass-card p-3 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-white break-words leading-snug">{job.title}</p>
          <p className="text-[11px] text-dark-300 truncate mt-0.5">{job.company}</p>
        </div>
        {job.score_letter && (
          <ScoreBar letter={job.score_letter} numeric={job.score_numeric} compact />
        )}
      </div>

      <div className="flex items-center justify-between">
        {job.domain ? (
          <span className="inline-block text-[10px] px-2 py-0.5 rounded-full bg-dark-700/50 text-dark-300 border border-dark-600/30">
            {job.domain}
          </span>
        ) : <div />}

        <div className="relative">
          <select
            value={job.status}
            onChange={(e) => onMove(job.id, e.target.value)}
            className="appearance-none bg-dark-800/80 border border-dark-600/50 text-[10px] text-dark-200 py-1 pl-2 pr-6 rounded-md outline-none focus:border-forge-400/50 cursor-pointer"
          >
            {COLUMNS.map((col) => (
              <option key={col.id} value={col.id} className="bg-dark-900 text-white">
                {col.label}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3 h-3 text-dark-400 absolute right-2 top-[5px] pointer-events-none" />
        </div>
      </div>
    </div>
  )
}

export default function Tracker() {
  const queryClient = useQueryClient()

  // Fetch board
  const { data: board, isLoading } = useQuery({
    queryKey: ['trackerBoard'],
    queryFn: () => api.get('/tracker/board').then((r) => r.data),
  })

  // Move mutation
  const moveMutation = useMutation({
    mutationFn: ({ jobId, status }) =>
      api.patch(`/tracker/move/${jobId}`, { status }).then((r) => r.data),
    onMutate: async ({ jobId, status }) => {
      // Cancel outgoing fetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['trackerBoard'] })

      const previousBoard = queryClient.getQueryData(['trackerBoard'])

      // Optimistically update to the new value
      queryClient.setQueryData(['trackerBoard'], (old) => {
        if (!old) return old
        const newBoard = { ...old }
        let movedJob = null

        // Find and remove job from old column
        for (const key of Object.keys(newBoard)) {
          const idx = newBoard[key].findIndex((j) => j.id === jobId)
          if (idx !== -1) {
            movedJob = { ...newBoard[key][idx], status }
            newBoard[key] = newBoard[key].filter((j) => j.id !== jobId)
            break
          }
        }

        // Add job to new column
        if (movedJob) {
          if (!newBoard[status]) newBoard[status] = []
          newBoard[status].push(movedJob)
        }

        return newBoard
      })

      return { previousBoard }
    },
    onError: (err, newTodo, context) => {
      // Rollback to previous board state on error
      queryClient.setQueryData(['trackerBoard'], context.previousBoard)
      toast.error(err.response?.data?.detail || 'Move failed')
    },
    onSettled: () => {
      // Invalidate to fetch definitive state
      queryClient.invalidateQueries({ queryKey: ['trackerBoard'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
  })

  const handleMove = (jobId, status) => {
    moveMutation.mutate({ jobId, status })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Kanban className="w-7 h-7 text-forge-400" />
          Application Tracker
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          Select a new status to manage your job application pipeline
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 overflow-x-auto pb-4 min-h-[calc(100vh-200px)]">
        {COLUMNS.map((col) => {
          const jobs = board?.[col.id] || []
          return (
            <div key={col.id} className="w-full sm:flex-shrink-0 sm:w-64">
              {/* Column Header */}
              <div className="flex items-center gap-2 mb-3 px-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: col.color }} />
                <span className="text-sm font-semibold text-white">{col.label}</span>
                <span className="text-xs font-mono text-dark-400 ml-auto">{jobs.length}</span>
              </div>

              {/* Column Content */}
              <div className="space-y-2 min-h-[100px] p-2 rounded-xl bg-dark-800/30 border border-dark-700/30">
                {jobs.map((job) => (
                  <TrackerJobCard key={job.id} job={job} onMove={handleMove} />
                ))}
                {jobs.length === 0 && (
                  <div className="flex items-center justify-center h-20 text-xs text-dark-500">
                    Empty
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
