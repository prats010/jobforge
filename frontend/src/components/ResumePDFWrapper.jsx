import { forwardRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './ResumePDFWrapper.css' // We will create this standard CSS file

const ResumePDFWrapper = forwardRef(({ contentMd }, ref) => {
  return (
    <div style={{ display: 'none' }}>
      {/* 
        This div is only visible to the printer. 
        It forces strict A4 sizing, white background, and standard black text padding.
      */}
      <div 
        ref={ref} 
        className="print-container resume-print-styles"
      >
        <ReactMarkdown>{contentMd || ''}</ReactMarkdown>
      </div>
    </div>
  )
})

ResumePDFWrapper.displayName = 'ResumePDFWrapper'
export default ResumePDFWrapper
