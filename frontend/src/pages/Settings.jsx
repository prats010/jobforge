import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Settings as SettingsIcon, Key, FileText, Check, X,
  Loader2, Save, Trash2, AlertTriangle
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import api from '../api/client'

export default function Settings() {
  const queryClient = useQueryClient()
  const [resumeMd, setResumeMd] = useState('')
  const [previewMode, setPreviewMode] = useState(false)
  const [showClearConfirm, setShowClearConfirm] = useState(false)

  // Fetch settings
  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => api.get('/settings').then((r) => r.data),
  })

  // Fetch base resume
  const { data: baseResume } = useQuery({
    queryKey: ['baseResume'],
    queryFn: () => api.get('/cv/base').then((r) => r.data),
  })

  useEffect(() => {
    if (baseResume?.content_md) {
      setResumeMd(baseResume.content_md)
    }
  }, [baseResume])

  // Save resume
  const resumeMutation = useMutation({
    mutationFn: (content) => api.put('/cv/base', { content_md: content }).then((r) => r.data),
    onSuccess: () => {
      toast.success('Resume saved!')
      queryClient.invalidateQueries({ queryKey: ['baseResume'] })
    },
    onError: () => toast.error('Failed to save resume'),
  })

  // Upload PDF
  const uploadPdfMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      const r = await api.post('/cv/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return r.data
    },
    onSuccess: () => {
      toast.success('PDF extracted and saved!')
      queryClient.invalidateQueries({ queryKey: ['baseResume'] })
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to upload PDF')
    }
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <SettingsIcon className="w-7 h-7 text-forge-400" />
          Settings
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          Configure your AI key, resume, and preferences
        </p>
      </div>

      {/* Base Resume Editor */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-forge-400" />
            Base Resume
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => setPreviewMode(!previewMode)}
              className="btn-ghost text-xs"
            >
              {previewMode ? 'Edit' : 'Preview'}
            </button>
            <div className="relative">
              <input
                type="file"
                accept=".pdf"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) uploadPdfMutation.mutate(file)
                  e.target.value = ''
                }}
                disabled={uploadPdfMutation.isPending}
              />
              <button
                disabled={uploadPdfMutation.isPending}
                className="btn-secondary text-xs flex items-center gap-1"
              >
                {uploadPdfMutation.isPending ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <span className="text-xs font-semibold">Upload PDF</span>
                )}
              </button>
            </div>
            <button
              onClick={() => resumeMutation.mutate(resumeMd)}
              disabled={resumeMutation.isPending}
              className="btn-primary text-xs flex items-center gap-1"
            >
              {resumeMutation.isPending ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Save className="w-3 h-3" />
              )}
              Save Resume
            </button>
          </div>
        </div>

        {previewMode ? (
          <div className="prose prose-invert prose-sm max-w-none max-h-[500px] overflow-y-auto p-4 bg-dark-900/50 rounded-lg border border-dark-600/30">
            <ReactMarkdown>{resumeMd}</ReactMarkdown>
          </div>
        ) : (
          <textarea
            value={resumeMd}
            onChange={(e) => setResumeMd(e.target.value)}
            placeholder="Paste your resume in Markdown format..."
            className="input-field text-sm min-h-[500px] resize-y font-mono leading-relaxed"
          />
        )}
      </motion.div>

      {/* Danger Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card p-6 border-red-500/20"
      >
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          Danger Zone
        </h2>

        {showClearConfirm ? (
          <div className="flex items-center gap-3">
            <p className="text-sm text-red-400">Are you sure? This cannot be undone.</p>
            <button
              onClick={() => {
                toast.error('Clear all data — not implemented yet')
                setShowClearConfirm(false)
              }}
              className="px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-sm hover:bg-red-500/30 transition-colors"
            >
              Yes, Clear Everything
            </button>
            <button
              onClick={() => setShowClearConfirm(false)}
              className="btn-ghost text-sm"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowClearConfirm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-dark-700 text-dark-200 border border-dark-500/50 rounded-lg hover:border-red-500/30 hover:text-red-400 transition-all text-sm"
          >
            <Trash2 className="w-4 h-4" />
            Clear All Data
          </button>
        )}
      </motion.div>
    </div>
  )
}
