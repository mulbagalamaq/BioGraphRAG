import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import ResultsPanel from './components/ResultsPanel'
import GraphVisualization from './components/GraphVisualization'
import ExampleQuestions from './components/ExampleQuestions'
import GreekDecorations from './components/GreekDecorations'
import './styles/App.css'

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
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: searchQuestion }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch results')
      }

      const data = await response.json()
      setResults(data)
      setShowGraph(true)
    } catch (err) {
      setError(err.message)
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion)
    handleSearch(exampleQuestion)
  }

  return (
    <div className="app-container" style={{ position: 'relative', minHeight: '100vh' }}>
      <GreekDecorations />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        style={{
          position: 'relative',
          zIndex: 10,
          padding: '2rem',
          maxWidth: '1400px',
          margin: '0 auto',
        }}
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
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: '400px',
              flexDirection: 'column',
              gap: '2rem',
            }}
          >
            <div className="loading-spiral"></div>
            <motion.p
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{
                fontSize: '1.2rem',
                color: 'var(--sea-crystal)',
                textAlign: 'center',
              }}
            >
              Consulting the Oracle of Delphi...
              <br />
              <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                Searching biomedical knowledge graphs
              </span>
            </motion.p>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card"
            style={{
              marginTop: '2rem',
              padding: '2rem',
              textAlign: 'center',
              borderColor: '#ff6b6b',
            }}
          >
            <h3 style={{ color: '#ff6b6b', marginBottom: '1rem' }}>⚠️ Error</h3>
            <p>{error}</p>
          </motion.div>
        )}

        {results && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{ marginTop: '3rem' }}
          >
            <div className="greek-divider"></div>

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
                style={{ marginTop: '2rem' }}
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
