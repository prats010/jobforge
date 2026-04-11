import { motion } from 'framer-motion'
import { MapPin, Calendar, ExternalLink, Briefcase } from 'lucide-react'
import ScoreBar from './ScoreBar'

const sourceBadge = {
  Greenhouse: 'badge-green',
  Lever: 'badge-blue',
  Internshala: 'badge-purple',
  LinkedIn: 'badge-blue',
  Naukri: 'badge-orange',
  Manual: 'badge-slate',
}

export default function JobCard({ job, onClick, compact = false }) {
  const daysAgo = job.created_at
    ? Math.floor((Date.now() - new Date(job.created_at).getTime()) / 86400000)
    : null

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      onClick={() => onClick?.(job)}
      className="glass-card-hover p-4 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-sm font-semibold text-white truncate">
            {job.title}
          </h3>
          {/* Company */}
          <p className="text-xs text-dark-200 mt-0.5">{job.company}</p>

          {!compact && (
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {/* Location */}
              {job.location && (
                <span className="flex items-center gap-1 text-[11px] text-dark-300">
                  <MapPin className="w-3 h-3" />
                  {job.location}
                </span>
              )}
              {/* Type */}
              {job.job_type && (
                <span className="flex items-center gap-1 text-[11px] text-dark-300">
                  <Briefcase className="w-3 h-3" />
                  {job.job_type}
                </span>
              )}
              {/* Days ago */}
              {daysAgo !== null && (
                <span className="flex items-center gap-1 text-[11px] text-dark-300">
                  <Calendar className="w-3 h-3" />
                  {daysAgo === 0 ? 'Today' : `${daysAgo}d ago`}
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex flex-col items-end gap-2">
          {/* Score */}
          {job.score_letter && (
            <ScoreBar letter={job.score_letter} numeric={job.score_numeric} compact />
          )}
          {/* Source */}
          <span className={sourceBadge[job.source] || 'badge-slate'}>
            {job.source}
          </span>
        </div>
      </div>

      {/* Domain */}
      {!compact && job.domain && (
        <div className="mt-2">
          <span className="badge-purple">{job.domain}</span>
        </div>
      )}

      {/* Source URL */}
      {!compact && job.source_url && (
        <a
          href={job.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="flex items-center gap-1 text-[11px] text-forge-400/70 hover:text-forge-400 mt-2 transition-colors"
        >
          <ExternalLink className="w-3 h-3" />
          View original posting
        </a>
      )}
    </motion.div>
  )
}
