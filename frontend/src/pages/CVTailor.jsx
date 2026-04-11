import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { FileText, Download, Copy, Loader2, Sparkles, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import { useReactToPrint } from 'react-to-print'
import { useRef } from 'react'
import api from '../api/client'
import ResumePDFWrapper from '../components/ResumePDFWrapper'

export default function CVTailor() {
  const queryClient = useQueryClient()
  const [selectedJobId, setSelectedJobId] = useState('')
  const [copied, setCopied] = useState(false)
  const printRef = useRef()

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

  // Tailor mutation
  const tailorMutation = useMutation({
    mutationFn: (jobId) => api.post(`/cv/tailor/${jobId}`).then((r) => r.data),
    onSuccess: () => {
      toast.success('Resume tailored successfully!')
      queryClient.invalidateQueries({ queryKey: ['evaluatedJobs'] })
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Tailoring failed'),
  })

  const handleCopy = async () => {
    const md = selectedJob?.tailored_cv_md || tailorMutation.data?.tailored_md
    if (md) {
      await navigator.clipboard.writeText(md)
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const tailoredMd = selectedJob?.tailored_cv_md || tailorMutation.data?.tailored_md

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

      {/* Keyword Stats */}
      {tailorMutation.data?.keywords_injected?.length > 0 && (
        <div className="glass-card p-4">
          <p className="text-xs text-dark-300 mb-2">
            Keywords injected: {tailorMutation.data.keywords_injected.length}
          </p>
          <div className="flex flex-wrap gap-2">
            {tailorMutation.data.keywords_injected.map((kw, i) => (
              <span key={i} className="badge-green">{kw}</span>
            ))}
          </div>
        </div>
      )}

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Base Resume */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-white mb-3">Base Resume</h3>
          <div className="prose prose-invert prose-sm max-w-none max-h-[600px] overflow-y-auto pr-2">
            <ReactMarkdown>{baseResume?.content_md || 'No resume loaded. Go to Settings.'}</ReactMarkdown>
          </div>
        </div>

        {/* Tailored Resume */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            Tailored Resume
            {tailoredMd && <span className="badge-green">AI Generated</span>}
          </h3>
          {tailorMutation.isPending ? (
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-forge-400 animate-spin mb-3" />
              <p className="text-sm text-dark-300">Tailoring your resume...</p>
            </div>
          ) : tailoredMd ? (
            <div className="prose prose-invert prose-sm max-w-none max-h-[600px] overflow-y-auto pr-2">
              <ReactMarkdown>{tailoredMd}</ReactMarkdown>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-dark-400">
              <FileText className="w-12 h-12 mb-3 opacity-30" />
              <p className="text-sm">Select a job and click "Tailor" to generate</p>
            </div>
          )}
        </div>
      </div>

      {/* Hidden print payload injected with the tailored markdown */}
      <ResumePDFWrapper ref={printRef} contentMd={tailoredMd} />
    </div>
  )
}
