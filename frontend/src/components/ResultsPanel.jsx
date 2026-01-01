import { motion } from 'framer-motion'
import { useState } from 'react'
import { BiNetworkChart } from 'react-icons/bi'
import { GiScroll, GiTwoCoins } from 'react-icons/gi'
import { MdScience } from 'react-icons/md'
import ReactMarkdown from 'react-markdown'

function ResultsPanel({ results, onToggleGraph, showGraph }) {
  const [activeTab, setActiveTab] = useState('answer')

  const tabs = [
    { id: 'answer', label: 'Answer', icon: <GiScroll size={20} /> },
    { id: 'nodes', label: 'Entities', icon: <GiTwoCoins size={20} /> },
    { id: 'evidence', label: 'Evidence', icon: <MdScience size={20} /> },
  ]

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="glass-card glass-card-strong">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '2rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}>
            <h2 style={{
              margin: 0,
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
            }}>
              <span style={{ color: 'var(--gold-accent)' }}>📜</span>
              Oracle's Response
            </h2>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-greek"
              onClick={onToggleGraph}
              style={{
                padding: '0.8rem 1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <BiNetworkChart size={20} />
              {showGraph ? 'Hide Graph' : 'Show Graph'}
            </motion.button>
          </div>

          {/* Tabs */}
          <div style={{
            display: 'flex',
            gap: '1rem',
            marginBottom: '2rem',
            borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
            flexWrap: 'wrap',
          }}>
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: activeTab === tab.id
                    ? 'linear-gradient(135deg, var(--sea-medium), var(--sea-light))'
                    : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === tab.id
                    ? '3px solid var(--gold-accent)'
                    : '3px solid transparent',
                  padding: '1rem 1.5rem',
                  color: 'var(--white-pearl)',
                  fontWeight: activeTab === tab.id ? 700 : 500,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.3s ease',
                  borderRadius: '10px 10px 0 0',
                }}
              >
                {tab.icon}
                {tab.label}
              </motion.button>
            ))}
          </div>

          {/* Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'answer' && (
              <div className="glass-card" style={{
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '2rem',
              }}>
                <div style={{
                  fontSize: '1.1rem',
                  lineHeight: '1.8',
                  color: 'var(--white-pearl)',
                }}>
                  <ReactMarkdown>{results.answer || 'No answer available'}</ReactMarkdown>
                </div>
              </div>
            )}

            {activeTab === 'nodes' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.nodes && results.nodes.length > 0 ? (
                  results.nodes.map((node, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-card"
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        padding: '1.5rem',
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '1rem',
                      }}>
                        <div style={{
                          minWidth: '40px',
                          height: '40px',
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, var(--gold-accent), var(--bronze-accent))',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                        }}>
                          {index + 1}
                        </div>
                        <div style={{ flex: 1 }}>
                          <h4 style={{
                            color: 'var(--sea-crystal)',
                            marginBottom: '0.5rem',
                          }}>
                            {node.name || node['~id']}
                          </h4>
                          {node.type && (
                            <div style={{
                              display: 'inline-block',
                              padding: '0.3rem 0.8rem',
                              background: 'rgba(110, 193, 204, 0.2)',
                              borderRadius: '20px',
                              fontSize: '0.85rem',
                              color: 'var(--sea-foam)',
                              marginBottom: '0.5rem',
                            }}>
                              {node.type}
                            </div>
                          )}
                          <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: '0.5rem 0' }}>
                            {node.description || 'No description available'}
                          </p>
                          {node.pmids && (
                            <div style={{
                              marginTop: '0.5rem',
                              fontSize: '0.9rem',
                              color: 'var(--gold-accent)',
                            }}>
                              📚 PMIDs: {Array.isArray(node.pmids) ? node.pmids.join(', ') : node.pmids}
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', textAlign: 'center' }}>
                    No entities found
                  </p>
                )}
              </div>
            )}

            {activeTab === 'evidence' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.evidence && results.evidence.length > 0 ? (
                  results.evidence.map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-card"
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        padding: '1.5rem',
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        gap: '1rem',
                        alignItems: 'flex-start',
                      }}>
                        <div style={{
                          color: 'var(--gold-accent)',
                          fontSize: '1.5rem',
                        }}>
                          🔬
                        </div>
                        <div>
                          <div style={{ color: 'var(--sea-crystal)', fontWeight: 600 }}>
                            {item.id || item.name || `Evidence ${index + 1}`}
                          </div>
                          <div style={{
                            color: 'rgba(255, 255, 255, 0.8)',
                            marginTop: '0.5rem',
                            fontSize: '0.95rem',
                          }}>
                            Score: {item.score ? item.score.toFixed(4) : 'N/A'}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', textAlign: 'center' }}>
                    No evidence available
                  </p>
                )}
              </div>
            )}
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}

export default ResultsPanel
