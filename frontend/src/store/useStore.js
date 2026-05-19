import { create } from 'zustand'

const useStore = create((set) => ({
  // Sidebar
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  // Selected job for detail view
  selectedJob: null,
  setSelectedJob: (job) => set({ selectedJob: job }),

  // Scanner state
  isScanning: false,
  setIsScanning: (v) => set({ isScanning: v }),
  scanProgress: null,
  setScanProgress: (p) => set({ scanProgress: p }),

  // Evaluator state
  isEvaluating: false,
  setIsEvaluating: (v) => set({ isEvaluating: v }),

  // Active evaluation result (for paste-and-evaluate flow)
  activeEvaluation: null,
  setActiveEvaluation: (e) => set({ activeEvaluation: e }),
}))

export default useStore
