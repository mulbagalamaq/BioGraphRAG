/**
 * BioGraphRAG Application
 *
 * Main application component providing biomedical question-answering capabilities
 * using graph-based retrieval-augmented generation (GraphRAG) architecture.
 *
 * @module App
 * @requires react
 * @requires framer-motion
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ResultsPanel from './components/ResultsPanel';
import GraphVisualization from './components/GraphVisualization';
import ExampleQuestions from './components/ExampleQuestions';
import BackgroundDecorations from './components/BackgroundDecorations';
import './styles/App.css';

/**
 * Application root component
 *
 * Manages application state including user input, API responses,
 * loading states, error handling, and graph visualization controls.
 *
 * @component
 * @returns {JSX.Element} The rendered application
 */
function App() {
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showGraph, setShowGraph] = useState(false);

  /**
   * Handles question submission and API interaction
   *
   * Sends POST request to /api/qa endpoint with the user's question
   * and processes the response containing answer, nodes, edges, and evidence.
   *
   * @async
   * @param {string} searchQuestion - The biomedical question to process
   * @throws {Error} When API request fails or returns non-OK status
   */
  const handleSearch = async (searchQuestion) => {
    setLoading(true);
    setError(null);
    setQuestion(searchQuestion);

    try {
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: searchQuestion }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setShowGraph(true);
    } catch (err) {
      setError(err.message);
      console.error('Error processing question:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles example question selection
   *
   * @param {string} exampleQuestion - Pre-defined example question
   */
  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion);
    handleSearch(exampleQuestion);
  };

  return (
    <div className="app-container">
      <BackgroundDecorations />

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
              Processing query and retrieving knowledge graph data
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
  );
}

export default App;
