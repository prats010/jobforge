import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Radar, Brain, FileText,
  Kanban, MessageSquare, Settings, ChevronLeft,
  ChevronRight, Hammer, X
} from 'lucide-react'
import useStore from '../store/useStore'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/scanner', icon: Radar, label: 'Scanner' },
  { path: '/evaluator', icon: Brain, label: 'Evaluator' },
  { path: '/cv-tailor', icon: FileText, label: 'CV Tailor' },
  { path: '/tracker', icon: Kanban, label: 'Tracker' },
  { path: '/interview', icon: MessageSquare, label: 'Interview Prep' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const sidebarOpen = useStore((s) => s.sidebarOpen)
  const toggleSidebar = useStore((s) => s.toggleSidebar)
  const mobileSidebarOpen = useStore((s) => s.mobileSidebarOpen)
  const setMobileSidebarOpen = useStore((s) => s.setMobileSidebarOpen)

  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // On mobile, the sidebar is always "open" (expanded width) when it's visible.
  const isExpanded = isMobile ? true : sidebarOpen

  return (
    <>
      {/* Mobile Backdrop */}
      <AnimatePresence>
        {isMobile && mobileSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setMobileSidebarOpen(false)}
            className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-40 md:hidden"
          />
        )}
      </AnimatePresence>

      <motion.aside
        initial={false}
        animate={{ 
          width: isMobile ? 256 : (sidebarOpen ? 256 : 80),
          x: isMobile ? (mobileSidebarOpen ? 0 : -256) : 0
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 h-screen bg-dark-800/95 md:bg-dark-800/80 backdrop-blur-xl border-r border-dark-600/30 z-50 flex flex-col shadow-2xl md:shadow-none"
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-5 py-6 border-b border-dark-600/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-forge-400/10 border border-forge-400/30 flex items-center justify-center flex-shrink-0">
              <Hammer className="w-5 h-5 text-forge-400" />
            </div>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <h1 className="text-lg font-bold text-white tracking-tight">
                  Job<span className="text-forge-400">Forge</span>
                </h1>
                <p className="text-[10px] text-dark-300 font-mono tracking-widest uppercase">
                  AI Pipeline
                </p>
              </motion.div>
            )}
          </div>
          {isMobile && (
            <button 
              onClick={() => setMobileSidebarOpen(false)}
              className="p-1 rounded-md text-dark-300 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              onClick={() => isMobile && setMobileSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative ${
                  isActive
                    ? 'bg-forge-400/10 text-forge-400'
                    : 'text-dark-200 hover:text-white hover:bg-dark-700/50'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-forge-400 rounded-r-full"
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-forge-400' : ''}`} />
                  {isExpanded && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-sm font-medium whitespace-nowrap"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Collapse Toggle (Desktop Only) */}
        {!isMobile && (
          <div className="p-3 border-t border-dark-600/30">
            <button
              onClick={toggleSidebar}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-dark-300 hover:text-white hover:bg-dark-700/50 transition-all duration-200"
            >
              {sidebarOpen ? (
                <>
                  <ChevronLeft className="w-4 h-4" />
                  <span className="text-xs">Collapse</span>
                </>
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          </div>
        )}
      </motion.aside>
    </>
  )
}
