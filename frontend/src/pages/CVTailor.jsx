import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { FileText, Download, Copy, Loader2, Sparkles, Check, Edit3, Save } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import { useReactToPrint } from 'react-to-print'
import api from '../api/client'
import ResumePDFWrapper from '../components/ResumePDFWrapper'

export default function CVTailor() {
  const queryClient = useQueryClient()
  const [selectedJobId, setSelectedJobId] = useState('')
  const [copied, setCopied] = useState(false)
  const printRef = useRef()

  // Edit states
  const [editBase, setEditBase] = useState(false)
  const [editTailored, setEditTailored] = useState(false)
  const [baseMdInput, setBaseMdInput] = useState('')
  const [tailoredMdInput, setTailoredMdInput] = useState('')

  // Setup react-to-print hook
  const handlePrint = useReactToPrint({
    contentRef: printRef,
    documentTitle: 'Tailored_Resume',
  })

  // Fetch base resume
  const { data: baseResume } = useQuery({
    queryKey: ['baseResume'],
    queryFn: () => api.get('/cv/base').then((r) => r.data),
  })

  // Fetch jobs that have been evaluated
  const { data: jobs } = useQuery({
    queryKey: ['evaluatedJobs'],
    queryFn: () => api.get('/jobs?limit=100').then((r) => r.data),
  })

  const evaluatedJobs = jobs?.filter((j) => j.score_letter) || []
  const selectedJob = evaluatedJobs.find((j) => j.id === Number(selectedJobId))

  const tailoredMd = selectedJob?.tailored_cv_md

  // Sync inputs with fetched data
  useEffect(() => {
    if (baseResume?.content_md && !editBase) {
      setBaseMdInput(baseResume.content_md)
    }
  }, [baseResume, editBase])

  useEffect(() => {
    if (tailoredMd && !editTailored) {
      setTailoredMdInput(tailoredMd)
    } else if (!tailoredMd && !editTailored) {
      setTailoredMdInput('')
    }
  }, [tailoredMd, editTailored, selectedJobId])

  // Mutations
  const tailorMutation = useMutation({
    mutationFn: (jobId) => api.post(`/cv/tailor/${jobId}`).then((r) => r.data),
    onSuccess: () => {
      toast.success('Resume tailored successfully!')
      queryClient.invalidateQueries({ queryKey: ['evaluatedJobs'] })
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Tailoring failed'),
  })

  const saveBaseMutation = useMutation({
    mutationFn: (content) => api.put('/cv/base', { content_md: content }).then((r) => r.data),
    onSuccess: () => {
      toast.success('Base resume saved!')
      setEditBase(false)
      queryClient.invalidateQueries({ queryKey: ['baseResume'] })
    },
    onError: () => toast.error('Failed to save base resume'),
  })

  const saveTailoredMutation = useMutation({
    mutationFn: ({ jobId, content }) => 
      api.put(`/cv/tailored/${jobId}`, { content_md: content }).then((r) => r.data),
    onSuccess: () => {
      toast.success('Tailored resume saved!')
      setEditTailored(false)
      queryClient.invalidateQueries({ queryKey: ['evaluatedJobs'] })
    },
    onError: () => toast.error('Failed to save tailored resume'),
  })

  const handleCopy = async () => {
    if (tailoredMd) {
      await navigator.clipboard.writeText(tailoredMd)
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <FileText className="w-7 h-7 text-forge-400" />
          CV Tailor
        </h1>
        <p className="text-sm text-dark-300 mt-1">
          AI-powered resume tailoring for specific job descriptions
        </p>
      </div>

      {/* Job Selector */}
      <div className="glass-card p-4 flex items-center gap-4 flex-wrap">
        <select
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
          className="input-field max-w-md text-sm"
        >
          <option value="">Select a job to tailor for...</option>
          {evaluatedJobs.map((job) => (
            <option key={job.id} value={job.id}>
              [{job.score_letter}] {job.title} — {job.company}
            </option>
          ))}
        </select>

        <button
          onClick={() => tailorMutation.mutate(Number(selectedJobId))}
          disabled={!selectedJobId || tailorMutation.isPending}
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          {tailorMutation.isPending ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Tailoring...</>
          ) : (
            <><Sparkles className="w-4 h-4" /> Tailor for This Job</>
          )}
        </button>

        {tailoredMd && (
          <div className="flex gap-2">
            <button onClick={handleCopy} className="btn-secondary flex items-center gap-2">
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={() => handlePrint()} className="px-4 py-2 bg-forge-500 hover:bg-forge-400 text-black font-semibold rounded-lg transition-all flex items-center gap-2 text-sm">
              <Download className="w-4 h-4" />
              Download PDF
            </button>
          </div>
        )}
      </div>

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Base Resume */}
        <div className="glass-card p-5 flex flex-col h-[700px]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">Base Resume</h3>
            {baseResume && (
              <button
                onClick={() => editBase ? saveBaseMutation.mutate(baseMdInput) : setEditBase(true)}
                disabled={saveBaseMutation.isPending}
                className="btn-ghost text-xs flex items-center gap-1"
              >
                {saveBaseMutation.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : editBase ? <Save className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
                {editBase ? 'Save Base' : 'Edit Base'}
              </button>
            )}
          </div>
          
          <div className="flex-1 overflow-hidden">
            {editBase ? (
              <textarea
                value={baseMdInput}
                onChange={(e) => setBaseMdInput(e.target.value)}
                className="w-full h-full bg-dark-900/50 border border-dark-600/30 rounded-lg p-4 text-sm font-mono text-dark-100 focus:outline-none focus:border-forge-500 resize-none"
              />
            ) : (
              <div className="prose prose-invert prose-sm max-w-none h-full overflow-y-auto pr-2">
                <ReactMarkdown>{baseResume?.content_md || 'No resume loaded. Go to Settings.'}</ReactMarkdown>
              </div>
            )}
          </div>
        </div>

        {/* Tailored Resume */}
        <div className="glass-card p-5 flex flex-col h-[700px]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              Tailored Resume
              {tailoredMd && !editTailored && <span className="badge-green">AI Generated</span>}
            </h3>
            {tailoredMd && (
              <button
                onClick={() => editTailored ? saveTailoredMutation.mutate({ jobId: selectedJob.id, content: tailoredMdInput }) : setEditTailored(true)}
                disabled={saveTailoredMutation.isPending}
                className="btn-ghost text-xs flex items-center gap-1"
              >
                {saveTailoredMutation.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : editTailored ? <Save className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
                {editTailored ? 'Save Tailored' : 'Edit Tailored'}
              </button>
            )}
          </div>

          <div className="flex-1 overflow-hidden">
            {tailorMutation.isPending ? (
              <div className="flex flex-col items-center justify-center h-full">
                <Loader2 className="w-8 h-8 text-forge-400 animate-spin mb-3" />
                <p className="text-sm text-dark-300">Tailoring your resume...</p>
              </div>
            ) : editTailored ? (
              <textarea
                value={tailoredMdInput}
                onChange={(e) => setTailoredMdInput(e.target.value)}
                className="w-full h-full bg-dark-900/50 border border-dark-600/30 rounded-lg p-4 text-sm font-mono text-dark-100 focus:outline-none focus:border-forge-500 resize-none"
              />
            ) : tailoredMd ? (
              <div className="prose prose-invert prose-sm max-w-none h-full overflow-y-auto pr-2">
                <ReactMarkdown>{tailoredMd}</ReactMarkdown>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-dark-400">
                <FileText className="w-12 h-12 mb-3 opacity-30" />
                <p className="text-sm">Select a job and click "Tailor" to generate</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hidden print payload injected with the tailored markdown */}
      <ResumePDFWrapper ref={printRef} contentMd={tailoredMdInput || tailoredMd} />
    </div>
  )
}
