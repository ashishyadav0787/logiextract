import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ExtractionResult from './components/ExtractionResult'
import RecordsHistory from './components/RecordsHistory'
import { Package, Zap, Shield, Database } from 'lucide-react'

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleExtracted = (data) => {
    setResult(data)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleValidated = (updated) => {
    setResult(updated)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Nav */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900">LogiExtract</span>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full ml-1">AI-Powered</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-blue-500" />
              <span>LangGraph Pipeline</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-green-500" />
              <span>Auto-Validation</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Database className="w-4 h-4 text-purple-500" />
              <span>PostgreSQL</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Hero */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Logistics Document Extraction Agent
          </h1>
          <p className="text-gray-500 mt-2 max-w-xl mx-auto">
            Upload a Bill of Lading, Invoice, or Purchase Order. The 5-stage LangGraph pipeline extracts all structured fields and validates them automatically.
          </p>
        </div>

        {/* Pipeline stages indicator */}
        <div className="flex items-center justify-center gap-2">
          {[
            { label: 'Scope Resolution', desc: 'Doc type detection' },
            { label: 'Context Compilation', desc: 'Schema selection' },
            { label: 'Schema Routing', desc: 'Field mapping' },
            { label: 'Plan + Execute', desc: 'LLM extraction' },
            { label: 'Evidence Delivery', desc: 'Structured output' },
          ].map((stage, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="text-center">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center mx-auto">
                  {i + 1}
                </div>
                <p className="text-xs font-medium text-gray-700 mt-1 w-20 text-center leading-tight">{stage.label}</p>
              </div>
              {i < 4 && <div className="w-8 h-px bg-blue-200 mb-5" />}
            </div>
          ))}
        </div>

        {/* Upload */}
        <UploadZone onExtracted={handleExtracted} loading={loading} setLoading={setLoading} />

        {/* Result */}
        {result && (
          <ExtractionResult
            record={result}
            onValidated={handleValidated}
          />
        )}

        {/* History */}
        <RecordsHistory onSelect={setResult} />
      </div>
    </div>
  )
}
