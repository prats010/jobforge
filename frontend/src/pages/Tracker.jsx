import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  DndContext, closestCorners, PointerSensor,
  useSensor, useSensors, DragOverlay, useDroppable
} from '@dnd-kit/core'
import {
  SortableContext, verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Kanban, GripVertical } from 'lucide-react'
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

function DroppableColumn({ id, children }) {
  const { setNodeRef } = useDroppable({ id })
  return (
    <div ref={setNodeRef} className="space-y-2 min-h-[200px] p-2 rounded-xl bg-dark-800/30 border border-dark-700/30">
      {children}
    </div>
  )
}

function SortableJobCard({ job }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `job-${job.id}`,
    data: { job },
  })

  const style = {
    transform: CSS.Translate.toString(transform),
    transition: transition || 'transform 250ms cubic-bezier(0.18, 0.67, 0.6, 1.22)',
    opacity: isDragging ? 0.4 : 1,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}
      className={`glass-card p-3 cursor-grab active:cursor-grabbing group ${isDragging ? 'ring-2 ring-forge-400 z-50' : ''}`}
    >
      <div className="flex items-start gap-2">
        <GripVertical className="w-4 h-4 text-dark-500 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-white truncate">{job.title}</p>
          <p className="text-[11px] text-dark-300 truncate">{job.company}</p>
        </div>
        {job.score_letter && (
          <ScoreBar letter={job.score_letter} numeric={job.score_numeric} compact />
        )}
      </div>
      {job.domain && (
        <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full bg-dark-700/50 text-dark-300 border border-dark-600/30">
          {job.domain}
        </span>
      )}
    </div>
  )
}

export default function Tracker() {
  const queryClient = useQueryClient()
  const [activeJob, setActiveJob] = useState(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
  )

  // Fetch board
  const { data: board, isLoading } = useQuery({
    queryKey: ['trackerBoard'],
    queryFn: () => api.get('/tracker/board').then((r) => r.data),
  })

  // Move mutation
  const moveMutation = useMutation({
    mutationFn: ({ jobId, status }) =>
      api.patch(`/tracker/move/${jobId}`, { status }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trackerBoard'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Move failed'),
  })

  const handleDragStart = (event) => {
    const { active } = event
    const jobData = active.data?.current?.job
    setActiveJob(jobData)
  }

  const handleDragEnd = (event) => {
    const { active, over } = event
    setActiveJob(null)

    if (!over) return

    const jobId = active.data?.current?.job?.id
    const overId = over.id

    // Determine target column
    let targetColumn = null
    if (typeof overId === 'string' && overId.startsWith('column-')) {
      targetColumn = overId.replace('column-', '')
    } else if (typeof overId === 'string' && overId.startsWith('job-')) {
      // Dropped on another job — find which column it's in
      const overJobId = parseInt(overId.replace('job-', ''))
      for (const col of COLUMNS) {
        const jobs = board?.[col.id] || []
        if (jobs.find((j) => j.id === overJobId)) {
          targetColumn = col.id
          break
        }
      }
    }

    if (targetColumn && jobId) {
      const currentStatus = active.data?.current?.job?.status
      if (currentStatus !== targetColumn) {
        moveMutation.mutate({ jobId, status: targetColumn })
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Kanban className="w-7 h-7 text-forge-400" />
          Application Tracker
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          Drag and drop to manage your job application pipeline
        </p>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4 min-h-[calc(100vh-200px)]">
          {COLUMNS.map((col) => {
            const jobs = board?.[col.id] || []
            return (
              <div key={col.id} className="flex-shrink-0 w-64">
                {/* Column Header */}
                <div className="flex items-center gap-2 mb-3 px-1">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: col.color }} />
                  <span className="text-sm font-semibold text-white">{col.label}</span>
                  <span className="text-xs font-mono text-dark-400 ml-auto">{jobs.length}</span>
                </div>

                {/* Column Drop Zone */}
                <SortableContext
                  id={`column-${col.id}`}
                  items={jobs.map((j) => `job-${j.id}`)}
                  strategy={verticalListSortingStrategy}
                >
                  <DroppableColumn id={`column-${col.id}`}>
                    {jobs.map((job) => (
                      <SortableJobCard key={job.id} job={job} />
                    ))}
                    {jobs.length === 0 && (
                      <div className="flex items-center justify-center h-20 text-xs text-dark-500">
                        Drop jobs here
                      </div>
                    )}
                  </DroppableColumn>
                </SortableContext>
              </div>
            )
          })}
        </div>

        <DragOverlay dropAnimation={{
          duration: 250,
          easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
        }}>
          {activeJob && (
            <div className="glass-card p-3 w-64 shadow-2xl border-forge-400/30 ring-2 ring-forge-400">
              <p className="text-xs font-medium text-white truncate">{activeJob.title}</p>
              <p className="text-[11px] text-dark-300">{activeJob.company}</p>
            </div>
          )}
        </DragOverlay>
      </DndContext>
    </div>
  )
}
