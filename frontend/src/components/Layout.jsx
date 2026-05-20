import { useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Menu, Hammer } from 'lucide-react'
import Sidebar from './Sidebar'
import useStore from '../store/useStore'

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -12 },
}

export default function Layout({ children }) {
  const location = useLocation()
  const sidebarOpen = useStore((s) => s.sidebarOpen)
  const setMobileSidebarOpen = useStore((s) => s.setMobileSidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-dark-900 grid-bg relative">
      <Sidebar />
      
      <main
        className={`flex-1 flex flex-col h-screen overflow-hidden transition-all duration-300 ${
          sidebarOpen ? 'md:ml-64' : 'md:ml-20'
        }`}
      >
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-dark-800/90 backdrop-blur-md border-b border-dark-600/30 z-30">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-forge-400/10 border border-forge-400/30 flex items-center justify-center">
              <Hammer className="w-4 h-4 text-forge-400" />
            </div>
            <h1 className="text-base font-bold text-white tracking-tight">
              Job<span className="text-forge-400">Forge</span>
            </h1>
          </div>
          <button 
            onClick={() => setMobileSidebarOpen(true)}
            className="p-2 -mr-2 text-dark-200 hover:text-white transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="p-4 sm:p-6 lg:p-8 min-h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}
