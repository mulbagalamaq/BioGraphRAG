import { motion } from 'framer-motion'
import { GiGreekTemple, GiDna2 } from 'react-icons/gi'
import { BiNetworkChart } from 'react-icons/bi'

function Header() {
  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      style={{
        textAlign: 'center',
        marginBottom: '3rem',
      }}
    >
      <div className="glass-card glass-card-strong" style={{ padding: '3rem 2rem' }}>
        {/* Greek Temple Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '1rem',
            marginBottom: '1.5rem',
          }}
        >
          <GiGreekTemple size={50} color="var(--gold-accent)" className="float-animation" />
          <GiDna2 size={45} color="var(--sea-crystal)" className="pulse" />
          <BiNetworkChart size={48} color="var(--gold-accent)" className="float-animation" />
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          style={{
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            marginBottom: '1rem',
            letterSpacing: '2px',
          }}
        >
          BioGraphRAG
        </motion.h1>

        {/* Greek-style subtitle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '1rem',
          }}
        >
          <span style={{ color: 'var(--gold-accent)', fontSize: '1.5rem' }}>◆</span>
          <h2 style={{
            fontSize: 'clamp(1.2rem, 3vw, 1.8rem)',
            fontWeight: 400,
            color: 'var(--sea-crystal)',
            fontStyle: 'italic',
          }}>
            The Oracle of Biomedical Knowledge
          </h2>
          <span style={{ color: 'var(--gold-accent)', fontSize: '1.5rem' }}>◆</span>
        </motion.div>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          style={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontSize: '1.1rem',
            maxWidth: '800px',
            margin: '0 auto',
            lineHeight: '1.6',
          }}
        >
          Navigate the vast seas of biomedical research with the wisdom of ancient Greece.
          <br />
          Ask questions about genes, diseases, and drugs, and receive grounded answers
          from our knowledge graph.
        </motion.p>

        {/* Greek wave pattern */}
        <div className="greek-pattern" style={{ marginTop: '2rem' }}>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
            style={{
              height: '3px',
              background: 'linear-gradient(90deg, transparent, var(--gold-accent), transparent)',
              transformOrigin: 'center',
            }}
          />
        </div>
      </div>
    </motion.header>
  )
}

export default Header
