import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import {
  Upload,
  FileText,
  Download,
  Loader2,
  CheckCircle,
  AlertCircle,
  Eye,
  Clock,
  Database,
  Sparkles,
  Zap,
  TrendingUp,
  FileCheck,
  BarChart3,
} from 'lucide-react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const navigationItems = [
  {
    id: 'upload',
    label: 'Upload & Extract',
    caption: 'Process a new document in seconds',
    icon: Upload,
  },
  {
    id: 'history',
    label: 'History & Analytics',
    caption: 'Review processed files and insights',
    icon: Database,
  },
]

const historyFilters = [
  { id: 'all', label: 'All' },
  { id: 'completed', label: 'Completed' },
  { id: 'processing', label: 'Processing' },
  { id: 'failed', label: 'Failed' },
]

function App() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [documents, setDocuments] = useState([])
  const [activeTab, setActiveTab] = useState('upload')
  const [historyFilter, setHistoryFilter] = useState('all')
  const [stats, setStats] = useState({ total: 0, avgConfidence: 0 })
  const [batchFiles, setBatchFiles] = useState([])
  const [batchUploading, setBatchUploading] = useState(false)
  const [batchResults, setBatchResults] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      if (acceptedFiles.length === 1) {
        setFile(acceptedFiles[0])
        setBatchFiles([])
      } else {
        setBatchFiles(acceptedFiles)
        setFile(null)
      }
      setError(null)
      setResult(null)
      setBatchResults(null)
    }
  }, [])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    open,
  } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
      'application/pdf': ['.pdf'],
      'application/zip': ['.zip']
    },
    maxFiles: 10,  // Changed from 1 to 10
    multiple: true,  // Added this
    noClick: true,
    noKeyboard: true,
  })

  useEffect(() => {
    if (activeTab === 'history') {
      loadDocuments()
    }
  }, [activeTab])

  useEffect(() => {
    if (documents.length > 0) {
      const avgConf =
        documents.reduce((sum, doc) => sum + (doc.confidence || 0), 0) /
        documents.length
      setStats({ total: documents.length, avgConfidence: avgConf })
    } else {
      setStats({ total: 0, avgConfidence: 0 })
    }
  }, [documents])

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/api/ocr/extract`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setResult(response.data)
      if (activeTab === 'history') {
        loadDocuments()
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process document')
    } finally {
      setUploading(false)
    }
  }

  const handleBatchUpload = async () => {
    if (batchFiles.length === 0) {
      setError('Please select files first')
      return
    }

    setBatchUploading(true)
    setError(null)
    setBatchResults(null)

    const formData = new FormData()
    batchFiles.forEach((file) => {
      formData.append('files', file)
    })

    try {
      const response = await axios.post(`${API_URL}/api/batch/upload-multiple`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setBatchResults(response.data)
      loadDocuments()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process batch upload')
    } finally {
      setBatchUploading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/ocr/documents`)
      setDocuments(response.data.documents || [])
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleExport = async (format) => {
    if (!result?.file_id) return

    try {
      const response = await axios.get(
        `${API_URL}/api/export/document/${result.file_id}/${format}`,
        { responseType: 'blob' },
      )

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ocr_result.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError(`Failed to export as ${format.toUpperCase()}`)
    }
  }

  const handleQuickAction = (action) => {
    if (action === 'browse') {
      open()
    }
    if (action === 'process') {
      handleUpload()
    }
    if (action === 'history') {
      setActiveTab('history')
    }
  }

  const filteredDocuments = documents.filter((doc) => {
    if (historyFilter === 'all') return true
    return (doc.status || '').toLowerCase() === historyFilter
  })

  const topConfidence = filteredDocuments.reduce(
    (acc, doc) => Math.max(acc, doc.confidence || 0),
    0,
  )

  const statusClass = (status) => {
    const normalized = (status || '').toLowerCase()
    if (normalized === 'completed') return 'status-pill status-pill-success'
    if (normalized === 'failed') return 'status-pill status-pill-danger'
    return 'status-pill status-pill-warning'
  }

  const quickActions = [
    {
      id: 'browse',
      label: 'Browse Local Files',
      description: 'Select a document from your device',
      icon: Upload,
      disabled: uploading,
    },
    {
      id: 'process',
      label: uploading ? 'Processing…' : 'Run Extraction',
      description: file ? 'Process the selected document' : 'Choose a file to process',
      icon: Zap,
      disabled: uploading || !file,
    },
    {
      id: 'history',
      label: 'View History',
      description: 'Explore processed documents',
      icon: Clock,
      disabled: documents.length === 0,
    },
  ]

  const exportOptions = [
    { format: 'txt', label: 'Plain Text', tone: 'bg-slate-100 text-slate-800' },
    { format: 'json', label: 'Structured JSON', tone: 'bg-amber-100 text-amber-800' },
    { format: 'docx', label: 'Word Document', tone: 'bg-blue-100 text-blue-800' },
    { format: 'pdf', label: 'PDF Report', tone: 'bg-rose-100 text-rose-800' },
  ]

  return (
    <div className="app-shell">
      <div className="app-gradient" />
      <div className="app-orb orb-left" />
      <div className="app-orb orb-right" />

      <div className="relative z-10 min-h-screen flex flex-col">
        <header className="max-w-7xl mx-auto w-full px-6 pt-12">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
            <div className="flex items-center gap-5">
              <div className="nav-icon">
                <Sparkles size={26} />
              </div>
              <div>
                <p className="badge badge-success">AI-POWERED</p>
                <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mt-3">
                  Enterprise-grade OCR workspace
                </h1>
                <p className="text-slate-500 mt-3 text-lg max-w-2xl">
                  Upload documents, extract structured insights, and monitor processing quality in a vibrant,
                  data-driven experience designed for modern teams.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <button className="btn-soft" onClick={open}>
                <Upload size={16} className="mr-2" />
                Quick Upload
              </button>
              <button
                className="btn-soft-secondary"
                onClick={() => setActiveTab('history')}
                disabled={documents.length === 0}
              >
                <BarChart3 size={16} className="mr-2" />
                Analytics
              </button>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto w-full px-6 pb-16 flex flex-col lg:flex-row gap-10 mt-12">
          <aside className="w-full lg:w-72 flex flex-col gap-8">
            <div className="glass-card card-shadow p-6 flex flex-col gap-5">
              {navigationItems.map((item) => {
                const Icon = item.icon
                const active = activeTab === item.id
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`nav-pill ${active ? 'nav-pill-active' : ''}`}
                  >
                    <div className="flex items-center gap-3 text-left">
                      <div className="pill-icon bg-white/40">
                        <Icon size={18} className="text-purple-600" />
                      </div>
                      <div>
                        <span className="font-semibold text-sm md:text-base">
                          {item.label}
                        </span>
                        <p className="text-[12px] text-slate-500 mt-1">{item.caption}</p>
                      </div>
                    </div>
                    <span className="pill-chevron">›</span>
                  </button>
                )
              })}
            </div>

            <div className="glass-card card-shadow p-6 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-400 tracking-[0.25em] uppercase">Quick Actions</p>
                  <p className="text-base font-semibold text-slate-700">Streamline your workflow</p>
                </div>
                <Zap size={20} className="text-yellow-500" />
              </div>
              {quickActions.map((action) => {
                const Icon = action.icon
                return (
                  <button
                    key={action.id}
                    onClick={() => handleQuickAction(action.id)}
                    disabled={action.disabled}
                    className="quick-action"
                  >
                    <div className="flex items-center gap-3 text-left">
                      <div className="quick-action-icon">
                        <Icon size={18} />
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-slate-700">{action.label}</p>
                        <p className="text-xs text-slate-500">{action.description}</p>
                      </div>
                    </div>
                    <span className="quick-action-chevron">›</span>
                  </button>
                )
              })}
            </div>

            <div className="glass-card card-shadow p-6 flex flex-col gap-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-600">Portfolio Health</p>
                <TrendingUp size={18} className="text-purple-500" />
              </div>
              <div className="metric-card">
                <span className="metric-label">Processed Documents</span>
                <span className="metric-value text-purple-600">{stats.total}</span>
                <div className="metric-bar">
                  <div style={{ width: `${Math.min(stats.total * 10, 100)}%` }} />
                </div>
              </div>
              <div className="metric-card">
                <span className="metric-label">Average Confidence</span>
                <span className="metric-value text-indigo-600">
                  {(stats.avgConfidence * 100 || 0).toFixed(1)}%
                </span>
                <div className="metric-bar">
                  <div style={{ width: `${Math.min(stats.avgConfidence * 100, 100)}%` }} />
                </div>
              </div>
            </div>
          </aside>

          <main className="flex-1 flex flex-col gap-10">
            {activeTab === 'upload' && (
            <>
            <section className="glass-card card-shadow p-10">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="badge badge-success">REAL-TIME OCR</p>
                  <h2 className="text-3xl font-bold text-slate-800 mt-3">Upload a document</h2>
                  <p className="text-slate-500 mt-2 max-w-xl">
                    Drag in a PDF, image, or office scan. Our hybrid PaddleOCR + Tesseract pipeline will extract
                    structured text and provide confidence analytics instantly.
                  </p>
                </div>
                {file && (
                  <button className="btn-soft-secondary" onClick={() => setFile(null)}>
                    Remove File
                  </button>
                )}
              </div>

              <div
                {...getRootProps({ className: `modern-dropzone ${isDragActive ? 'modern-dropzone-active' : ''}` })}
              >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center">
                  {file ? (
                    <>
                      <div className="p-6 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-2xl mb-6">
                        <FileCheck size={56} className="text-purple-600" />
                      </div>
                      <p className="text-xl font-bold text-gray-800 mb-2">{file.name}</p>
                      <p className="text-sm text-gray-500 bg-gray-100 px-4 py-2 rounded-full">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setFile(null)
                        }}
                        className="mt-4 text-sm text-red-500 hover:text-red-700 font-semibold"
                      >
                        Remove file
                      </button>
                    </>
                  ) : batchFiles.length > 0 ? (
                    <>
                      <div className="p-6 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl mb-6">
                        <FileCheck size={56} className="text-green-600" />
                      </div>
                      <p className="text-xl font-bold text-gray-800 mb-2">
                        {batchFiles.length} files selected
                      </p>
                      <div className="max-h-40 overflow-y-auto w-full mt-4">
                        {batchFiles.map((f, idx) => (
                          <div key={idx} className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg mb-2">
                            <span className="text-sm font-medium text-gray-700 truncate flex-1">{f.name}</span>
                            <span className="text-xs text-gray-500 ml-2">{(f.size / 1024).toFixed(1)} KB</span>
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setBatchFiles([])
                        }}
                        className="mt-4 text-sm text-red-500 hover:text-red-700 font-semibold"
                      >
                        Clear all files
                      </button>
                    </>
                  ) : (
                    <>
                      <div className="p-6 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-2xl mb-6">
                        <Upload size={56} className="text-purple-600" />
                      </div>
                      <p className="text-2xl font-bold text-gray-800 mb-3">
                        {isDragActive ? 'Drop it like it\'s hot! 🔥' : 'Drag & Drop Your Files'}
                      </p>
                      <p className="text-gray-500 mb-6">
                        Single or multiple files, or click to browse
                      </p>
                      <div className="flex flex-wrap justify-center gap-2">
                        {['PDF', 'PNG', 'JPG', 'TIFF', 'BMP', 'ZIP'].map((format) => (
                          <span
                            key={format}
                            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-xs font-bold"
                          >
                            {format}
                          </span>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>

              {error && (
                <div className="mt-5 bg-red-50 border border-red-200 rounded-2xl p-5 flex items-start">
                  <AlertCircle className="text-red-500 mr-3 flex-shrink-0" size={22} />
                  <div>
                    <p className="font-semibold text-red-700">Upload failed</p>
                    <p className="text-sm text-red-500">{error}</p>
                  </div>
                </div>
              )}

              <div className="mt-6 flex flex-col md:flex-row gap-4">
                <button
                  onClick={batchFiles.length > 0 ? handleBatchUpload : handleUpload}
                  disabled={(!file && batchFiles.length === 0) || uploading || batchUploading}
                  className="btn-gradient text-white py-4 px-6 rounded-2xl text-lg font-semibold flex items-center justify-center"
                >
                  {uploading || batchUploading ? (
                    <>
                      <Loader2 className="animate-spin mr-3" size={20} />
                      Processing {batchFiles.length > 0 ? `${batchFiles.length} files` : 'Magic'}...
                    </>
                  ) : (
                    <>
                      <Zap size={18} className="mr-3" />
                      <span>{batchFiles.length > 0 ? `Extract ${batchFiles.length} Files` : 'Run Extraction'}</span>
                    </>
                  )}
                </button>
                <button
                  className="btn-soft-secondary flex items-center justify-center"
                  onClick={() => setActiveTab('history')}
                >
                  <HistoryIcon />
                  <span className="ml-2">View History</span>
                </button>
              </div>
            </section>

            <section className="grid gap-10 xl:grid-cols-2">
              <div className="glass-card card-shadow p-10 min-h-[340px]">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <p className="badge badge-success">LATEST OUTPUT</p>
                    <h3 className="text-2xl font-bold text-slate-800 mt-3">Extraction summary</h3>
                  </div>
                  <FileText className="text-purple-500" size={28} />
                </div>

                {batchResults ? (
                  <div className="space-y-6">
                    <div className={`bg-gradient-to-r ${batchResults.successful > 0 ? 'from-green-50 to-emerald-50 border-green-200' : 'from-red-50 to-orange-50 border-red-200'} border-2 rounded-2xl p-6`}>
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <p className="font-bold text-gray-800 text-xl">Batch Upload Complete</p>
                          <p className="text-sm text-gray-600 mt-1">{batchResults.message}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-3xl font-extrabold text-green-600">{batchResults.successful}</p>
                          <p className="text-xs text-gray-500">Successful</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-3 mb-4">
                        <div className="bg-white rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-purple-600">{batchResults.total_files}</p>
                          <p className="text-xs text-gray-500">Total</p>
                        </div>
                        <div className="bg-white rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-green-600">{batchResults.successful}</p>
                          <p className="text-xs text-gray-500">Success</p>
                        </div>
                        <div className="bg-white rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-red-600">{batchResults.failed}</p>
                          <p className="text-xs text-gray-500">Failed</p>
                        </div>
                      </div>

                      <div className="max-h-64 overflow-y-auto space-y-2">
                        {batchResults.results.map((result, idx) => (
                          <div key={idx} className={`p-4 rounded-xl ${result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="font-semibold text-gray-800">{result.filename}</p>
                                {result.success ? (
                                  <div className="mt-2 space-y-1">
                                    <p className="text-sm text-gray-600">
                                      <span className="font-semibold">Confidence:</span> {(result.confidence * 100).toFixed(1)}%
                                    </p>
                                    <p className="text-sm text-gray-600">
                                      <span className="font-semibold">Lines:</span> {result.line_count}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-2 italic">
                                      {result.extracted_text_preview}...
                                    </p>
                                  </div>
                                ) : (
                                  <p className="text-sm text-red-600 mt-1">{result.error}</p>
                                )}
                              </div>
                              <div className="ml-4">
                                {result.success ? (
                                  <CheckCircle size={24} className="text-green-600" />
                                ) : (
                                  <AlertCircle size={24} className="text-red-600" />
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : result ? (
                  <div className="space-y-6">
                    <div className="metric-card">
                      <span className="metric-label">Confidence</span>
                      <span className="metric-value text-purple-600">
                        {(result.confidence * 100 || 0).toFixed(1)}%
                      </span>
                      <div className="metric-bar">
                        <div style={{ width: `${Math.min((result.confidence || 0) * 100, 100)}%` }} />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="metric-card">
                        <span className="metric-label">Total Lines</span>
                        <span className="metric-value text-indigo-600">
                          {result.line_count ?? 0}
                        </span>
                      </div>
                      <div className="metric-card">
                        <span className="metric-label">Status</span>
                        <span className="metric-value text-emerald-600 capitalize">
                          {(result.status || 'completed').toString()}
                        </span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-[0.3em] mb-3">
                        Text Preview
                      </h4>
                      <div className="preview-pane">
                        <pre className="whitespace-pre-wrap break-words">
                          {result.extracted_text || '—'}
                        </pre>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      {exportOptions.map((option) => (
                        <button
                          key={option.format}
                          onClick={() => handleExport(option.format)}
                          className={`export-btn ${option.tone}`}
                        >
                          <Download size={16} />
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Eye size={62} className="mx-auto text-purple-200 mb-4" />
                    <p className="text-slate-500 font-semibold">
                      Upload a document to see extraction highlights here
                    </p>
                  </div>
                )}
              </div>

              <div className="glass-card card-shadow p-10">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <p className="badge badge-success">INTELLIGENCE</p>
                    <h3 className="text-2xl font-bold text-slate-800 mt-3">
                      Quality overview
                    </h3>
                  </div>
                  <TrendingUp size={28} className="text-purple-500" />
                </div>

                <div className="grid gap-4">
                  <div className="metric-card">
                    <span className="metric-label">Average confidence</span>
                    <span className="metric-value text-purple-600">
                      {(stats.avgConfidence * 100 || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-label">Top performing document</span>
                    <span className="metric-value text-indigo-600">
                      {(topConfidence * 100 || 0).toFixed(1)}%
                    </span>
                    <p className="text-xs text-slate-400 mt-2">
                      Highest confidence across the currently filtered records.
                    </p>
                  </div>
                  <div className="metric-card">
                    <span className="metric-label">Documents in view</span>
                    <span className="metric-value text-purple-600">
                      {filteredDocuments.length}
                    </span>
                  </div>
                </div>
              </div>
            </section>
            </>
            )}

            {activeTab === 'history' && (
            <section className="glass-card card-shadow p-10">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                <div>
                  <p className="badge badge-success">DOCUMENT HISTORY</p>
                  <h3 className="text-2xl font-bold text-slate-800 mt-3">
                    Processed records
                  </h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {historyFilters.map((filter) => (
                    <button
                      key={filter.id}
                      onClick={() => setHistoryFilter(filter.id)}
                      className={`filter-chip ${historyFilter === filter.id ? 'filter-chip-active' : ''}`}
                    >
                      {filter.label}
                    </button>
                  ))}
                </div>
              </div>

              {filteredDocuments.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 text-slate-500">
                      <tr>
                        <th className="px-6 py-3 text-left font-semibold">Filename</th>
                        <th className="px-6 py-3 text-left font-semibold">Date</th>
                        <th className="px-6 py-3 text-left font-semibold">Confidence</th>
                        <th className="px-6 py-3 text-left font-semibold">Lines</th>
                        <th className="px-6 py-3 text-left font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white/90">
                      {filteredDocuments.map((doc) => (
                        <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4 font-semibold text-slate-700">
                            {doc.original_filename}
                          </td>
                          <td className="px-6 py-4 text-slate-500">
                            {doc.processed_at
                              ? new Date(doc.processed_at).toLocaleString()
                              : '—'}
                          </td>
                          <td className="px-6 py-4 text-slate-600 font-semibold">
                            {((doc.confidence || 0) * 100).toFixed(1)}%
                          </td>
                          <td className="px-6 py-4 text-slate-500">{doc.line_count ?? '—'}</td>
                          <td className="px-6 py-4">
                            <span className={statusClass(doc.status)}>
                              {(doc.status || 'pending').toUpperCase()}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-16 text-slate-400">
                  <Database size={64} className="mx-auto mb-4 opacity-40" />
                  <p className="text-lg font-semibold">
                    No documents match the selected filter
                  </p>
                  <p className="text-sm text-slate-500 mt-2">
                    Upload a document or adjust your filters to see analytics.
                  </p>
                </div>
              )}
            </section>
            )}
          </main>
        </div>

        <footer className="w-full py-12 mt-auto">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 text-slate-500">
            <p>
              Built with ❤️ using React, FastAPI, PaddleOCR & Tesseract — delivering enterprise OCR intelligence.
            </p>
            <div className="flex items-center gap-2 text-sm">
              <Sparkles size={16} className="text-purple-500" />
              <span>Lightning-fast pipelines · Confidence analytics · Seamless exports</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

const HistoryIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    className="w-4 h-4"
  >
    <path d="M3 12a9 9 0 1 0 4.5-7.794" />
    <path d="M3 4v4h4" />
    <path d="M12 7v5l3 3" />
  </svg>
)

export default App
