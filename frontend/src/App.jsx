import { useState, useCallback, useEffect, useRef } from 'react'
import axios from 'axios'
import { 
  FiPlus, FiTrash2, FiCheckCircle, FiAlertCircle, 
  FiCopy, FiDownload, FiUpload, FiFile, FiLink,
  FiInfo, FiFilter, FiGrid, FiList, FiX, FiChevronDown,
  FiSearch, FiGlobe, FiShield, FiTrendingUp,
  FiLayers, FiZap, FiUsers, FiSettings, FiBookOpen
} from 'react-icons/fi'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import './App.css'

// Use environment variable for API URL, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'development' ? 'http://localhost:8002' : '/api')

function generateUUID() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2)+Date.now().toString(36)
}

function App() {
  // State management
  const [references, setReferences] = useState([''])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [contextHints, setContextHints] = useState('')
  const [audience, setAudience] = useState('Compliance')
  const [industry, setIndustry] = useState('')
  const [jurisdiction, setJurisdiction] = useState('')
  const [framework, setFramework] = useState('')
  const [detailLevel, setDetailLevel] = useState('comprehensive')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [checklists, setChecklists] = useState([])
  const [metadata, setMetadata] = useState(null)
  const [viewMode, setViewMode] = useState('grid')
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  const [showExamples, setShowExamples] = useState(false)
  const [supportedFormats, setSupportedFormats] = useState(null)
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState([])
  const [reqId, setRequestId] = useState(null)

  // Fetch supported formats on mount
  useEffect(() => {
    fetchSupportedFormats()
  }, [])

  const fetchSupportedFormats = async () => {
    try {
      const response = await axios.get(`${API_URL}/supported-formats`)
      setSupportedFormats(response.data)
    } catch (err) {
      console.error('Failed to fetch supported formats:', err)
    }
  }

  // File handling
  const handleFileUpload = useCallback((e) => {
    const files = Array.from(e.target.files)
    
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (event) => {
        const base64 = event.target.result.split(',')[1]
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          base64: base64,
          size: file.size,
          type: file.type
        }])
      }
      reader.readAsDataURL(file)
    })
  }, [])

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  // Reference management
  const addReference = () => {
    setReferences([...references, ''])
  }

  const updateReference = (index, value) => {
    const newRefs = [...references]
    newRefs[index] = value
    setReferences(newRefs)
  }

  const removeReference = (index) => {
    const newRefs = references.filter((_, i) => i !== index)
    setReferences(newRefs.length ? newRefs : [''])
  }

  // Checklist generation
  const pollingRef = useRef(null)

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }

  const generateChecklist = async () => {
    const validRefs = references.filter(ref => ref.trim())
    
    if (!validRefs.length && uploadedFiles.length === 0) {
      setError('Please provide at least one reference or upload a document')
      return
    }

    const reqId = generateUUID()
    setRequestId(reqId)

    setLoading(true)
    setError('')
    setChecklists([])
    setMetadata(null)
    setProgress(0)
    setLogs([])
    toast.info('🚀 Starting compliance analysis...', { autoClose: 5000 })

    // Start polling progress endpoint immediately
    pollingRef.current = setInterval(async () => {
      try {
        const resp = await axios.get(`${API_URL}/progress/${reqId}`)
        if (resp.data.progress !== undefined) {
          setProgress(resp.data.progress)
          setLogs(resp.data.logs)
        }
        if (resp.data.progress >= 1) {
          stopPolling()
        }
      } catch (e) {
        // ignore while backend not yet set
      }
    }, 3000)

    try {
      const requestData = {
        primary_references: validRefs,
        uploaded_files: uploadedFiles.map(f => f.base64),
        file_names: uploadedFiles.map(f => f.name),
        context_scope_hints: contextHints || null,
        audience: audience,
        industry: industry || null,
        jurisdiction: jurisdiction || null,
        compliance_framework: framework || null,
        detail_level: detailLevel
      }

      const response = await axios.post(`${API_URL}/generate-checklist`, requestData, {
        timeout: 300000, // Reduced timeout for serverless
        headers: {
          'X-Request-ID': reqId,
          'Content-Type': 'application/json'
        }
      })

      setChecklists(response.data.checklists)
      setMetadata(response.data.metadata)
      toast.success('✅ Compliance checklist generated successfully!', { autoClose: 4000 })
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to generate checklist. Please try again.'
      setError(errorMessage)
      toast.error('❌ Generation failed', { autoClose: 4000 })
    } finally {
      setLoading(false)
      stopPolling()
    }
  }

  // Export functions
  const copyToClipboard = () => {
    const json = JSON.stringify(checklists, null, 2)
    navigator.clipboard.writeText(json)
    toast.success('📋 Copied to clipboard!', { autoClose: 2000 })
  }

  const downloadJSON = () => {
    const data = {
      generated_at: new Date().toISOString(),
      metadata: metadata,
      checklists: checklists
    }
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `compliance-checklist-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('💾 Downloaded as JSON!', { autoClose: 2000 })
  }

  const downloadCSV = () => {
    let csv = 'Category,Name,Priority,Frequency,Description\n'
    checklists.forEach(checklist => {
      const desc = checklist.checklist_ai_description.replace(/"/g, '""')
      csv += `"${checklist.checklist_category}","${checklist.checklist_name}","${checklist.priority || 'N/A'}","${checklist.frequency || 'N/A'}","${desc}"\n`
    })
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `compliance-checklist-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('📊 Downloaded as CSV!', { autoClose: 2000 })
  }

  // Filtering
  const filteredChecklists = checklists.filter(checklist => {
    if (filterCategory !== 'all' && checklist.checklist_category !== filterCategory) return false
    if (filterPriority !== 'all' && checklist.priority !== filterPriority) return false
    return true
  })

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / 1048576).toFixed(1) + ' MB'
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-brand">
              <div className="header-icon">
                <FiShield />
              </div>
              <div>
                <h1>Compliance Dashboard</h1>
                <p>Advanced compliance checklist generation and analysis</p>
              </div>
            </div>
            <div className="header-actions">
              <div className="status-badges">
                <span className="badge badge-version">v2.1</span>
                <span className="badge badge-status">Live</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Section */}
      {loading && (
        <div className="progress-section">
          <div className="container">
            <div className="progress-card">
              <div className="progress-header">
                <div className="progress-title">
                  <div className="spinner-icon">
                    <FiZap />
                  </div>
                  <div>
                    <h3>AI Analysis in Progress</h3>
                    <p>Processing your compliance requirements with advanced AI...</p>
                  </div>
                </div>
                <div className="progress-percentage">{Math.round(progress*100)}%</div>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${Math.round(progress*100)}%` }} />
              </div>
              <div className="logs-container">
                <div className="logs-header">
                  <FiBookOpen />
                  <span>Live Processing Activity</span>
                </div>
                <div className="logs-content">
                  {logs.slice(-5).map((log, idx) => (
                    <div key={idx} className="log-entry">
                      <div className="log-dot"></div>
                      <span>{log}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Hero Section */}
          <div className="hero-section">
            <div className="hero-content">
              <h2>Transform Regulations into Actionable Checklists</h2>
              <p>Upload documents, paste URLs, or search for compliance frameworks to generate comprehensive audit checklists powered by advanced AI technology</p>
              <div className="hero-features">
                <div className="feature-tag">
                  <FiGlobe />
                  <span>Smart Web Search</span>
                </div>
                <div className="feature-tag">
                  <FiUpload />
                  <span>Document Analysis</span>
                </div>
                <div className="feature-tag">
                  <FiZap />
                  <span>AI-Powered</span>
                </div>
              </div>
            </div>
            <div className="hero-stats">
              <div className="stat-item">
                <FiGlobe />
                <div>
                  <span className="stat-number">50+</span>
                  <span className="stat-label">Jurisdictions</span>
                </div>
              </div>
              <div className="stat-item">
                <FiLayers />
                <div>
                  <span className="stat-number">200+</span>
                  <span className="stat-label">Frameworks</span>
                </div>
              </div>
              <div className="stat-item">
                <FiTrendingUp />
                <div>
                  <span className="stat-number">99.9%</span>
                  <span className="stat-label">Accuracy</span>
                </div>
              </div>
            </div>
          </div>

          {/* Input Form */}
          <div className="input-form">
            {/* References Section */}
            <div className="form-section">
              <div className="section-header">
                <div className="section-icon">
                  <FiLink />
                </div>
                <div>
                 <h3>Compliance Sources</h3>
                 <p>Add URLs to regulations, paste text, or use search terms for comprehensive analysis</p>
                 <div className="search-examples">
                   <span className="example-label">Popular Examples:</span>
                   <span 
                     className="example-tag"
                     onClick={() => updateReference(0, 'GDPR data processing requirements')}
                   >
                     GDPR data processing
                   </span>
                   <span 
                     className="example-tag"
                     onClick={() => updateReference(0, 'SOC 2 Type 2 security controls')}
                   >
                     SOC 2 Type 2 controls
                   </span>
                   <span 
                     className="example-tag"
                     onClick={() => updateReference(0, 'NIST cybersecurity framework')}
                   >
                     NIST cybersecurity framework
                   </span>
                 </div>
               </div>
              </div>
              
              <div className="references-container">
                {references.map((reference, index) => (
                  <div key={index} className="reference-item">
                    <div className="reference-input-group">
                      <div className="input-icon">
                        <FiSearch />
                      </div>
                      <input
                        type="text"
                        value={reference}
                        onChange={(e) => updateReference(index, e.target.value)}
                        placeholder="Enter URL, regulation name, or search term (e.g., 'GDPR Article 32', 'SOC 2 controls')"
                        className="reference-input"
                      />
                      {references.length > 1 && (
                        <button
                          onClick={() => removeReference(index)}
                          className="remove-btn"
                        >
                          <FiX />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                
                <button onClick={addReference} className="add-reference-btn">
                  <FiPlus />
                  Add Another Source
                </button>
              </div>
            </div>

            {/* File Upload Section */}
            <div className="form-section">
              <div className="section-header">
                <div className="section-icon">
                  <FiUpload />
                </div>
                <div>
                  <h3>Document Upload</h3>
                  <p>Upload compliance documents for intelligent analysis</p>
                </div>
              </div>

              <div className="upload-area">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleFileUpload}
                  className="file-input"
                />
                <label htmlFor="file-upload" className="upload-label">
                  <div className="upload-icon">
                    <FiUpload />
                  </div>
                  <div className="upload-text">
                    <strong>Click to upload</strong> or drag and drop
                    <br />
                    <span>PDF, DOCX, TXT, MD (Max 10MB each)</span>
                  </div>
                </label>
              </div>

              {uploadedFiles.length > 0 && (
                <div className="uploaded-files">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="file-item">
                      <div className="file-icon">
                        <FiFile />
                      </div>
                      <div className="file-details">
                        <div className="file-name">{file.name}</div>
                        <div className="file-size">{formatFileSize(file.size)}</div>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="file-remove"
                      >
                        <FiTrash2 />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Configuration Section */}
            <div className="form-section">
              <div className="section-header">
                <div className="section-icon">
                  <FiSettings />
                </div>
                <div>
                  <h3>Analysis Configuration</h3>
                  <p>Customize the AI analysis for your specific needs</p>
                </div>
              </div>

              <div className="config-grid">
                <div className="config-item">
                  <label className="config-label">Target Audience</label>
                  <select
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    className="config-select"
                  >
                    <option value="Compliance">Compliance Team</option>
                    <option value="Legal">Legal Department</option>
                    <option value="IT">IT Security</option>
                    <option value="Risk">Risk Management</option>
                    <option value="Audit">Internal Audit</option>
                  </select>
                </div>

                <div className="config-item">
                  <label className="config-label">Industry</label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="config-select"
                  >
                    <option value="">Select Industry...</option>
                    <option value="Banking & Financial Services">Banking & Financial</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Technology">Technology</option>
                    <option value="Insurance">Insurance</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Retail">Retail</option>
                  </select>
                </div>

                <div className="config-item">
                  <label className="config-label">Jurisdiction</label>
                  <select
                    value={jurisdiction}
                    onChange={(e) => setJurisdiction(e.target.value)}
                    className="config-select"
                  >
                    <option value="">Select Jurisdiction...</option>
                    <option value="United States">United States</option>
                    <option value="European Union">European Union</option>
                    <option value="United Kingdom">United Kingdom</option>
                    <option value="India">India</option>
                    <option value="Singapore">Singapore</option>
                    <option value="Australia">Australia</option>
                  </select>
                </div>

                <div className="config-item">
                  <label className="config-label">Framework</label>
                  <select
                    value={framework}
                    onChange={(e) => setFramework(e.target.value)}
                    className="config-select"
                  >
                    <option value="">Select Framework...</option>
                    <option value="SOC 2">SOC 2</option>
                    <option value="ISO 27001">ISO 27001</option>
                    <option value="GDPR">GDPR</option>
                    <option value="HIPAA">HIPAA</option>
                    <option value="PCI-DSS">PCI-DSS</option>
                    <option value="NIST">NIST</option>
                  </select>
                </div>
              </div>

              <div className="detail-level">
                <label className="config-label">Analysis Depth</label>
                <div className="radio-group">
                  <label className="radio-option">
                    <input
                      type="radio"
                      value="basic"
                      checked={detailLevel === 'basic'}
                      onChange={(e) => setDetailLevel(e.target.value)}
                    />
                    <span className="radio-custom"></span>
                    <div>
                      <strong>Basic</strong>
                      <p>Essential compliance points</p>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      value="standard"
                      checked={detailLevel === 'standard'}
                      onChange={(e) => setDetailLevel(e.target.value)}
                    />
                    <span className="radio-custom"></span>
                    <div>
                      <strong>Standard</strong>
                      <p>Comprehensive coverage</p>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      value="comprehensive"
                      checked={detailLevel === 'comprehensive'}
                      onChange={(e) => setDetailLevel(e.target.value)}
                    />
                    <span className="radio-custom"></span>
                    <div>
                      <strong>Comprehensive</strong>
                      <p>Deep regulatory analysis</p>
                    </div>
                  </label>
                </div>
              </div>

              <div className="context-hints">
                <label className="config-label">Focus Areas (Optional)</label>
                <textarea
                  value={contextHints}
                  onChange={(e) => setContextHints(e.target.value)}
                  placeholder="e.g., Focus on data privacy, customer due diligence, or specific risk areas for enhanced analysis..."
                  className="context-textarea"
                  rows={3}
                />
              </div>
            </div>

            {/* Generate Button */}
            <div className="generate-section">
              {error && (
                <div className="error-banner">
                  <FiAlertCircle />
                  <span>{error}</span>
                </div>
              )}
              
              <button
                onClick={generateChecklist}
                disabled={loading}
                className="generate-btn"
              >
                {loading ? (
                  <>
                    <div className="btn-spinner"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <FiZap />
                    Generate AI Compliance Checklist
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Section */}
          {checklists.length > 0 && (
            <div className="results-section">
              <div className="results-header">
                <div>
                  <h2>Generated Compliance Checklists</h2>
                  <p>{checklists.length} items generated • Ready for implementation</p>
                </div>
                <div className="results-actions">
                  <button onClick={copyToClipboard} className="action-btn">
                    <FiCopy />
                    Copy
                  </button>
                  <button onClick={downloadJSON} className="action-btn">
                    <FiDownload />
                    JSON
                  </button>
                  <button onClick={downloadCSV} className="action-btn">
                    <FiDownload />
                    CSV
                  </button>
                </div>
              </div>

              <div className="checklists-grid">
                {filteredChecklists.map((checklist, index) => (
                  <div key={index} className="checklist-card">
                    <div className="card-header">
                      <div className="card-category">
                        {checklist.checklist_category}
                      </div>
                      {checklist.priority && (
                        <div className={`priority-badge priority-${checklist.priority}`}>
                          {checklist.priority}
                        </div>
                      )}
                    </div>
                    <div className="card-content">
                      <h3 className="card-title">{checklist.checklist_name}</h3>
                      {checklist.frequency && (
                        <div className="card-frequency">
                          <FiUsers />
                          {checklist.frequency}
                        </div>
                      )}
                      <div className="card-description">
                        {checklist.checklist_ai_description}
                      </div>
                    </div>
                    <div className="card-actions">
                      <button className="card-action-btn">
                        <FiCheckCircle />
                      </button>
                      <button className="card-action-btn">
                        <FiCopy />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      <ToastContainer 
        theme="light"
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  )
}

export default App
