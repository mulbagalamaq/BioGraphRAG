import { motion } from 'framer-motion'
import { GiDna1, GiHeartOrgan, GiChemicalDrop } from 'react-icons/gi'
import { MdBiotech } from 'react-icons/md'

const examples = [
  {
    icon: <GiDna1 size={28} />,
    question: "Which genes are associated with colon cancer?",
    category: "Gene-Disease",
  },
  {
    icon: <GiChemicalDrop size={28} />,
    question: "What drugs target EGFR?",
    category: "Drug-Target",
  },
  {
    icon: <GiHeartOrgan size={28} />,
    question: "How is BRCA1 related to breast cancer?",
    category: "Disease Mechanism",
  },
  {
    icon: <MdBiotech size={28} />,
    question: "What is the relationship between KRAS and colon cancer treatment?",
    category: "Treatment",
  },
]

function ExampleQuestions({ onExampleClick }) {
  return (
    <div style={{ marginTop: '3rem' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div style={{
          textAlign: 'center',
          marginBottom: '2rem',
        }}>
          <h3 style={{
            color: 'var(--sea-crystal)',
            fontSize: '1.8rem',
            marginBottom: '0.5rem',
          }}>
            🏛️ Explore Ancient Wisdom
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
            Try these example questions to begin your journey
          </p>
        </div>

        <div className="card-grid">
          {examples.map((example, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div
                className="glass-card"
                onClick={() => onExampleClick(example.question)}
                style={{
                  cursor: 'pointer',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  transition: 'all 0.3s ease',
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  color: 'var(--gold-accent)',
                }}>
                  {example.icon}
                  <span style={{
                    fontSize: '0.85rem',
                    color: 'var(--sea-foam)',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                  }}>
                    {example.category}
                  </span>
                </div>

                <p style={{
                  color: 'var(--white-pearl)',
                  fontSize: '1.05rem',
                  lineHeight: '1.5',
                  margin: 0,
                }}>
                  "{example.question}"
                </p>

                <div style={{
                  marginTop: 'auto',
                  paddingTop: '1rem',
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  color: 'var(--sea-crystal)',
                  fontSize: '0.9rem',
                  fontStyle: 'italic',
                }}>
                  Click to explore →
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default ExampleQuestions
