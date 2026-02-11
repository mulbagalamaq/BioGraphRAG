import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import ResultsPanel from './components/ResultsPanel'
import GraphVisualization from './components/GraphVisualization'
import ExampleQuestions from './components/ExampleQuestions'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || ''

function App() {
  const [question, setQuestion] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showGraph, setShowGraph] = useState(false)

  const handleSearch = async (searchQuestion) => {
    setLoading(true)
    setError(null)
    setQuestion(searchQuestion)

    try {
      const response = await fetch(`${API_BASE}/api/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: searchQuestion }),
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = await response.json()
      setResults(data)
      setShowGraph(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion)
    handleSearch(exampleQuestion)
  }

  return (
    <div className="app-container">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="app-content"
      >
        <Header />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <SearchBar
            value={question}
            onChange={setQuestion}
            onSearch={handleSearch}
            loading={loading}
          />
        </motion.div>

        {!results && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <ExampleQuestions onExampleClick={handleExampleClick} />
          </motion.div>
        )}

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="loading-container"
          >
            <div className="loading-spinner" />
            <motion.p
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="loading-text"
            >
              Fetching biomedical data and building knowledge graph...
            </motion.p>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card error-card"
          >
            <h3 className="error-title">Request Failed</h3>
            <p className="error-message">{error}</p>
          </motion.div>
        )}

        {results && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="results-container"
          >
            <div className="section-divider" />

            <ResultsPanel
              results={results}
              onToggleGraph={() => setShowGraph(!showGraph)}
              showGraph={showGraph}
            />

            {showGraph && results.nodes && results.nodes.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                transition={{ duration: 0.6 }}
                className="graph-container"
              >
                <GraphVisualization
                  nodes={results.nodes}
                  edges={results.edges || []}
                />
              </motion.div>
            )}
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

export default App
