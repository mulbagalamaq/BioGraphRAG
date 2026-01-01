import { motion } from 'framer-motion'
import { FiSearch } from 'react-icons/fi'
import { GiScrollUnfurled } from 'react-icons/gi'

function SearchBar({ value, onChange, onSearch, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (value.trim() && !loading) {
      onSearch(value)
    }
  }

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          marginBottom: '1.5rem',
        }}>
          <GiScrollUnfurled size={32} color="var(--gold-accent)" />
          <h3 style={{ margin: 0, color: 'var(--sea-crystal)' }}>
            Ask the Oracle
          </h3>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              className="input-glass"
              placeholder="Ask about genes, diseases, or drugs... (e.g., 'Which genes are associated with colon cancer?')"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              disabled={loading}
              style={{
                paddingRight: '60px',
                fontSize: '1.1rem',
              }}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={loading || !value.trim()}
              className="btn-greek"
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                padding: '0.8rem 1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                opacity: loading || !value.trim() ? 0.5 : 1,
                cursor: loading || !value.trim() ? 'not-allowed' : 'pointer',
              }}
            >
              <FiSearch size={20} />
              <span>Search</span>
            </motion.button>
          </div>
        </form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          style={{
            marginTop: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: '0.9rem',
          }}
        >
          <span style={{ color: 'var(--gold-accent)' }}>✨</span>
          <span>Powered by GraphRAG • Grounded in biomedical knowledge graphs</span>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default SearchBar
