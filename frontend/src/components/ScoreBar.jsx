import { motion } from 'framer-motion'

const gradeColors = {
  A: { text: '#00e676', bg: 'rgba(0, 230, 118, 0.15)', border: 'rgba(0, 230, 118, 0.3)' },
  B: { text: '#00bcd4', bg: 'rgba(0, 188, 212, 0.15)', border: 'rgba(0, 188, 212, 0.3)' },
  C: { text: '#ffd600', bg: 'rgba(255, 214, 0, 0.15)', border: 'rgba(255, 214, 0, 0.3)' },
  D: { text: '#ff9100', bg: 'rgba(255, 145, 0, 0.15)', border: 'rgba(255, 145, 0, 0.3)' },
  F: { text: '#ff1744', bg: 'rgba(255, 23, 68, 0.15)', border: 'rgba(255, 23, 68, 0.3)' },
}

export default function ScoreBar({ letter, numeric, compact = false }) {
  const colors = gradeColors[letter] || gradeColors.C

  if (compact) {
    return (
      <div
        className="flex items-center gap-1.5 px-2 py-1 rounded-lg border font-mono"
        style={{ backgroundColor: colors.bg, borderColor: colors.border }}
      >
        <span className="text-sm font-bold" style={{ color: colors.text }}>
          {letter}
        </span>
        {numeric !== undefined && numeric !== null && (
          <span className="text-[10px] text-dark-200">
            {Number(numeric).toFixed(1)}
          </span>
        )}
      </div>
    )
  }

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex items-center gap-4"
    >
      {/* Big letter grade */}
      <div
        className="w-20 h-20 rounded-2xl border-2 flex items-center justify-center"
        style={{ backgroundColor: colors.bg, borderColor: colors.border }}
      >
        <span className="text-4xl font-mono font-black" style={{ color: colors.text }}>
          {letter}
        </span>
      </div>

      {/* Numeric + bar */}
      <div className="flex-1">
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-mono font-bold text-white">
            {numeric !== undefined && numeric !== null ? Number(numeric).toFixed(1) : '—'}
          </span>
          <span className="text-sm text-dark-300 font-mono">/ 5.0</span>
        </div>
        <div className="w-full h-2 bg-dark-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${((numeric || 0) / 5) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full rounded-full"
            style={{ backgroundColor: colors.text }}
          />
        </div>
      </div>
    </motion.div>
  )
}
