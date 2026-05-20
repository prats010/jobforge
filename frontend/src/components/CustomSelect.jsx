import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function CustomSelect({ value, onChange, options, placeholder, className = '', small = false }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  const selectedOption = options.find((opt) => String(opt.value) === String(value))

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between gap-2 bg-dark-800/80 border border-dark-600/50 outline-none hover:border-forge-400/50 transition-colors ${
          small ? 'text-xs text-dark-200 py-1.5 px-2 rounded-md' : 'text-sm text-dark-100 py-2.5 px-3 rounded-lg'
        }`}
      >
        <span className="truncate">{selectedOption ? selectedOption.label : (placeholder || 'Select...')}</span>
        <ChevronDown className={`w-4 h-4 text-dark-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            transition={{ duration: 0.15 }}
            className={`absolute z-50 w-full mt-1 bg-dark-800 border border-dark-600/50 shadow-xl overflow-hidden ${
              small ? 'rounded-md' : 'rounded-lg'
            }`}
          >
            <div className="max-h-60 overflow-y-auto custom-scrollbar">
              {options.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => {
                    onChange(opt.value)
                    setIsOpen(false)
                  }}
                  className={`w-full text-left px-3 py-2.5 transition-colors flex items-center justify-between ${
                    small ? 'text-xs' : 'text-sm'
                  } ${
                    String(value) === String(opt.value)
                      ? 'bg-forge-400/10 text-forge-400'
                      : 'text-dark-200 hover:bg-dark-700/50 hover:text-white'
                  }`}
                >
                  <span className="truncate">{opt.label}</span>
                  {String(value) === String(opt.value) && <Check className="w-3 h-3 text-forge-400 flex-shrink-0 ml-2" />}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
