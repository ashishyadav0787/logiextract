import { useState } from 'react'
import { CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, Upload } from 'lucide-react'
import { validateAgainstPO } from '../hooks/api'

const DOC_LABELS = {
  bill_of_lading: 'Bill of Lading',
  invoice: 'Invoice',
  purchase_order: 'Purchase Order',
  unknown: 'Unknown'
}

const STATUS_CONFIG = {
  matched: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', label: 'Validated' },
  mismatch: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', label: 'Mismatch Detected' },
  warning: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', label: 'Warning' },
  pending: { icon: AlertTriangle, color: 'text-gray-500', bg: 'bg-gray-50', border: 'border-gray-200', label: 'Pending Validation' },
}

function FieldRow({ label, value }) {
  if (value === null || value === undefined) return null
  const display = typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)
  const isLong = display.length > 80

  return (
    <div className="flex gap-4 py-2.5 border-b border-gray-100 last:border-0">
      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide w-44 shrink-0 pt-0.5">
        {label.replace(/_/g, ' ')}
      </span>
      <span className={`text-sm text-gray-800 ${isLong ? 'font-mono text-xs whitespace-pre-wrap' : ''}`}>
        {display}
      </span>
    </div>
  )
}

function ValidationPanel({ result }) {
  if (!result) return null
  const { matched_fields = [], mismatched_fields = [], missing_fields = [], summary } = result

  return (
    <div className="mt-4 space-y-3">
      {summary && (
        <p className="text-sm text-gray-700 italic">{summary}</p>
      )}
      {matched_fields.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-green-700 mb-1">✓ Matched Fields ({matched_fields.length})</p>
          <div className="flex flex-wrap gap-1">
            {matched_fields.map(f => (
              <span key={f} className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">{f.replace(/_/g, ' ')}</span>
            ))}
          </div>
        </div>
      )}
      {mismatched_fields.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-red-700 mb-1">✗ Mismatches ({mismatched_fields.length})</p>
          <div className="space-y-1">
            {mismatched_fields.map((m, i) => (
              <div key={i} className="text-xs bg-red-50 border border-red-200 rounded-lg p-2">
                <span className="font-semibold">{m.field?.replace(/_/g, ' ')}</span>
                <span className={`ml-2 px-1.5 py-0.5 rounded text-white text-xs ${m.severity === 'error' ? 'bg-red-500' : 'bg-amber-500'}`}>{m.severity}</span>
                <div className="mt-1 text-gray-600">Expected: <span className="text-red-700">{m.expected}</span> · Found: <span className="text-green-700">{m.found}</span></div>
              </div>
            ))}
          </div>
        </div>
      )}
      {missing_fields.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-amber-700 mb-1">⚠ Missing Fields ({missing_fields.length})</p>
          <div className="flex flex-wrap gap-1">
            {missing_fields.map(f => (
              <span key={f} className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">{f.replace(/_/g, ' ')}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function ExtractionResult({ record, onValidated }) {
  const [showValidation, setShowValidation] = useState(true)
  const [poLoading, setPoLoading] = useState(false)

  const status = STATUS_CONFIG[record.validation_status] || STATUS_CONFIG.pending
  const StatusIcon = status.icon
  const confidence = Math.round((record.confidence_score || 0) * 100)

  const handlePOUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setPoLoading(true)
    try {
      const updated = await validateAgainstPO(record.id, file)
      onValidated(updated)
    } catch (err) {
      alert(err?.response?.data?.detail || 'Validation failed')
    } finally {
      setPoLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center text-lg">
            {record.doc_type === 'bill_of_lading' ? '🚢' : record.doc_type === 'invoice' ? '🧾' : '📋'}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{record.filename}</p>
            <p className="text-sm text-gray-500">{DOC_LABELS[record.doc_type] || record.doc_type}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-xs text-gray-400">Confidence</p>
            <div className="flex items-center gap-1">
              <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${confidence >= 80 ? 'bg-green-500' : confidence >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className="text-xs font-semibold text-gray-700">{confidence}%</span>
            </div>
          </div>
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${status.bg} ${status.border}`}>
            <StatusIcon className={`w-4 h-4 ${status.color}`} />
            <span className={`text-xs font-semibold ${status.color}`}>{status.label}</span>
          </div>
        </div>
      </div>

      {/* Extracted Fields */}
      <div className="px-6 py-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Extracted Fields</h3>
        <div className="divide-y divide-gray-100">
          {Object.entries(record.extracted_fields).map(([key, val]) => (
            <FieldRow key={key} label={key} value={val} />
          ))}
        </div>
      </div>

      {/* Validation Section */}
      <div className={`mx-6 mb-6 rounded-xl border ${status.border} ${status.bg} overflow-hidden`}>
        <button
          onClick={() => setShowValidation(!showValidation)}
          className="w-full px-4 py-3 flex items-center justify-between"
        >
          <span className="text-sm font-semibold text-gray-700">Validation Report</span>
          {showValidation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {showValidation && (
          <div className="px-4 pb-4">
            <ValidationPanel result={record.validation_result} />
          </div>
        )}
      </div>

      {/* Validate against PO */}
      {record.doc_type === 'invoice' && (
        <div className="px-6 pb-6">
          <label className={`flex items-center gap-2 justify-center w-full py-2.5 px-4 rounded-xl border-2 border-dashed border-blue-300 text-blue-600 text-sm font-medium cursor-pointer hover:bg-blue-50 transition-colors ${poLoading ? 'opacity-60 pointer-events-none' : ''}`}>
            <Upload className="w-4 h-4" />
            {poLoading ? 'Validating against PO...' : 'Upload Purchase Order to Validate'}
            <input type="file" accept=".pdf" className="hidden" onChange={handlePOUpload} />
          </label>
        </div>
      )}
    </div>
  )
}
