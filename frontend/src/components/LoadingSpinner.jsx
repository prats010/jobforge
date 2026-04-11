import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }
  return (
    <Loader2 className={`${sizes[size]} animate-spin text-forge-400 ${className}`} />
  )
}

export function LoadingOverlay({ message = 'Processing...' }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-50 flex items-center justify-center"
    >
      <div className="glass-card p-8 flex flex-col items-center gap-4 max-w-sm">
        <div className="w-16 h-16 rounded-2xl bg-forge-400/10 border border-forge-400/30 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
        <div className="text-center">
          <p className="text-white font-medium">{message}</p>
          <p className="text-xs text-dark-300 mt-1">This may take a few seconds...</p>
        </div>
        {/* Animated dots */}
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
              className="w-2 h-2 rounded-full bg-forge-400"
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-4 space-y-3">
      <div className="skeleton h-4 w-3/4" />
      <div className="skeleton h-3 w-1/2" />
      <div className="flex gap-2">
        <div className="skeleton h-5 w-16 rounded-full" />
        <div className="skeleton h-5 w-20 rounded-full" />
      </div>
    </div>
  )
}

export function SkeletonList({ count = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  )
}

export default Spinner
