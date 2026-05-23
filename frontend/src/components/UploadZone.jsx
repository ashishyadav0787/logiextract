import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Loader2 } from 'lucide-react'

export default function UploadZone({ onExtracted, loading, setLoading }) {
  const [filename, setFilename] = useState(null)

  const onDrop = useCallback(async (files) => {
    const file = files[0]
    if (!file) return
    setFilename(file.name)
    setLoading(true)
    try {
      const { extractDocument } = await import('../hooks/api')
      const result = await extractDocument(file)
      onExtracted(result)
    } catch (e) {
      const msg = e?.response?.data?.detail || 'Extraction failed'
      alert(msg)
    } finally {
      setLoading(false)
    }
  }, [onExtracted, setLoading])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: loading
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
        ${loading ? 'opacity-60 cursor-not-allowed' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        {loading ? (
          <>
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
            <p className="text-gray-600 font-medium">Running extraction pipeline...</p>
            <p className="text-sm text-gray-400">LangGraph agent is processing {filename}</p>
            <div className="flex gap-2 mt-2">
              {['Scope Resolution', 'Context Compilation', 'Schema Routing', 'Extraction', 'Evidence Delivery'].map((stage, i) => (
                <span key={i} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full animate-pulse">{stage}</span>
              ))}
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <p className="text-lg font-semibold text-gray-800">
                {isDragActive ? 'Drop your PDF here' : 'Upload Logistics Document'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Bill of Lading · Invoice · Purchase Order
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <FileText className="w-4 h-4" />
              <span>PDF only · Max 10MB</span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
