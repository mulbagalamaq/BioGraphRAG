import { motion } from 'framer-motion'

function GreekDecorations() {
  return (
    <>
      {/* Floating Greek columns */}
      <motion.div
        initial={{ opacity: 0, x: -100 }}
        animate={{ opacity: 0.1, x: 0 }}
        transition={{ duration: 2 }}
        style={{
          position: 'fixed',
          left: '5%',
          top: '20%',
          fontSize: '10rem',
          color: 'var(--gold-accent)',
          zIndex: 1,
          pointerEvents: 'none',
        }}
        className="float-animation"
      >
        🏛️
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: 0.1, x: 0 }}
        transition={{ duration: 2, delay: 0.5 }}
        style={{
          position: 'fixed',
          right: '5%',
          top: '60%',
          fontSize: '10rem',
          color: 'var(--gold-accent)',
          zIndex: 1,
          pointerEvents: 'none',
        }}
        className="float-animation"
      >
        🏛️
      </motion.div>

      {/* DNA helix decorations */}
      <motion.div
        initial={{ opacity: 0, rotate: -45 }}
        animate={{ opacity: 0.08, rotate: 0 }}
        transition={{ duration: 3 }}
        style={{
          position: 'fixed',
          left: '10%',
          bottom: '10%',
          fontSize: '8rem',
          color: 'var(--sea-crystal)',
          zIndex: 1,
          pointerEvents: 'none',
        }}
        className="float-animation"
      >
        🧬
      </motion.div>

      <motion.div
        initial={{ opacity: 0, rotate: 45 }}
        animate={{ opacity: 0.08, rotate: 0 }}
        transition={{ duration: 3, delay: 0.3 }}
        style={{
          position: 'fixed',
          right: '15%',
          bottom: '20%',
          fontSize: '8rem',
          color: 'var(--sea-crystal)',
          zIndex: 1,
          pointerEvents: 'none',
        }}
        className="float-animation"
      >
        🧬
      </motion.div>

      {/* Greek wave pattern at bottom */}
      <div
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          height: '60px',
          background: 'repeating-linear-gradient(90deg, transparent, transparent 20px, rgba(212, 175, 55, 0.1) 20px, rgba(212, 175, 55, 0.1) 40px)',
          zIndex: 1,
          pointerEvents: 'none',
        }}
      />
    </>
  )
}

export default GreekDecorations
