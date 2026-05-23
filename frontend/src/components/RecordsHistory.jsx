import { useEffect, useState } from 'react'
import { getRecords, deleteRecord } from '../hooks/api'
import { Trash2, FileText, RefreshCw } from 'lucide-react'

const DOC_LABELS = {
  bill_of_lading: '🚢 Bill of Lading',
  invoice: '🧾 Invoice',
  purchase_order: '📋 Purchase Order',
  unknown: '❓ Unknown'
}

const STATUS_COLORS = {
  matched: 'bg-green-100 text-green-700',
  mismatch: 'bg-red-100 text-red-700',
  warning: 'bg-amber-100 text-amber-700',
  pending: 'bg-gray-100 text-gray-600'
}

export default function RecordsHistory({ onSelect }) {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await getRecords(filter)
      setRecords(data.records)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filter])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this record?')) return
    await deleteRecord(id)
    setRecords(r => r.filter(x => x.id !== id))
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Extraction History</h2>
        <div className="flex gap-2">
          {[null, 'bill_of_lading', 'invoice', 'purchase_order'].map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`text-xs px-3 py-1 rounded-full transition-colors ${filter === type ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              {type ? type.replace(/_/g, ' ') : 'All'}
            </button>
          ))}
          <button onClick={load} className="p-1 text-gray-400 hover:text-gray-600">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="divide-y divide-gray-50">
        {loading ? (
          <div className="py-12 text-center text-gray-400 text-sm">Loading...</div>
        ) : records.length === 0 ? (
          <div className="py-12 text-center text-gray-400 text-sm">No records yet. Upload a document above.</div>
        ) : records.map(r => (
          <div
            key={r.id}
            onClick={() => onSelect(r)}
            className="px-6 py-3 flex items-center gap-4 hover:bg-gray-50 cursor-pointer transition-colors group"
          >
            <FileText className="w-5 h-5 text-gray-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{r.filename}</p>
              <p className="text-xs text-gray-400">{DOC_LABELS[r.doc_type]} · {new Date(r.created_at).toLocaleDateString()}</p>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[r.validation_status] || STATUS_COLORS.pending}`}>
              {r.validation_status}
            </span>
            <span className="text-xs text-gray-400">{Math.round((r.confidence_score || 0) * 100)}%</span>
            <button
              onClick={(e) => handleDelete(r.id, e)}
              className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
