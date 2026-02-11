import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import ForceGraph2D from 'react-force-graph-2d'

function GraphVisualization({ nodes, edges }) {
  const graphRef = useRef()
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => {
    const updateDimensions = () => {
      const container = graphRef.current?.parentElement
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: Math.min(600, window.innerHeight * 0.6),
        })
      }
    }
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  useEffect(() => {
    const transformedNodes = nodes.map((node, index) => ({
      id: node.id || `node-${index}`,
      name: node.name || node.id || `Node ${index}`,
      type: node.type || 'Unknown',
      description: node.description || '',
      val: 20,
    }))

    const nodeIds = new Set(transformedNodes.map(n => n.id))

    const transformedLinks = edges
      .filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target))
      .map((edge, index) => ({
        source: edge.source,
        target: edge.target,
        label: edge.relation || 'RELATED',
        id: `link-${index}`,
      }))

    setGraphData({ nodes: transformedNodes, links: transformedLinks })
  }, [nodes, edges])

  const getNodeColor = (node) => {
    const colorMap = {
      Gene: '#6ec1cc',
      Disease: '#ff6b6b',
      Drug: '#d4af37',
      Publication: '#8e99a4',
    }
    return colorMap[node.type] || '#2d9caa'
  }

  const paintNode = (node, ctx, globalScale) => {
    const label = node.name
    const fontSize = 12 / globalScale
    const nodeRadius = Math.sqrt(node.val) * 1.5

    ctx.shadowBlur = 15
    ctx.shadowColor = getNodeColor(node)
    ctx.fillStyle = getNodeColor(node)
    ctx.beginPath()
    ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI)
    ctx.fill()

    ctx.shadowBlur = 0
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2 / globalScale
    ctx.stroke()

    ctx.font = `${fontSize}px Inter, sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = '#ffffff'
    ctx.shadowBlur = 3
    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'
    ctx.fillText(label, node.x, node.y + nodeRadius + fontSize)
  }

  const paintLink = (link, ctx, globalScale) => {
    const start = link.source
    const end = link.target

    const textPos = {
      x: start.x + (end.x - start.x) / 2,
      y: start.y + (end.y - start.y) / 2,
    }

    ctx.strokeStyle = 'rgba(212, 175, 55, 0.6)'
    ctx.lineWidth = 2 / globalScale
    ctx.beginPath()
    ctx.moveTo(start.x, start.y)
    ctx.lineTo(end.x, end.y)
    ctx.stroke()

    if (link.label) {
      const fontSize = 10 / globalScale
      ctx.font = `${fontSize}px Inter, sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillStyle = '#fafafa'
      ctx.shadowBlur = 3
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)'
      ctx.fillText(link.label, textPos.x, textPos.y)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="glass-card glass-card-strong">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
        }}>
          <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            Knowledge Graph Visualization
          </h3>
          <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)' }}>
            {graphData.nodes.length} nodes &bull; {graphData.links.length} relationships
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem', flexWrap: 'wrap', fontSize: '0.9rem' }}>
          {[
            { color: '#6ec1cc', label: 'Genes' },
            { color: '#ff6b6b', label: 'Diseases' },
            { color: '#d4af37', label: 'Drugs' },
            { color: '#8e99a4', label: 'Publications' },
          ].map(({ color, label }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: color }} />
              <span>{label}</span>
            </div>
          ))}
        </div>

        <div
          ref={graphRef}
          style={{
            width: '100%',
            height: `${dimensions.height}px`,
            background: 'rgba(10, 79, 92, 0.3)',
            borderRadius: '15px',
            overflow: 'hidden',
            border: '2px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <ForceGraph2D
            graphData={graphData}
            width={dimensions.width}
            height={dimensions.height}
            nodeCanvasObject={paintNode}
            linkCanvasObject={paintLink}
            nodeLabel={(node) => `${node.name}\n${node.description || ''}`}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleColor={() => '#d4af37'}
            linkDirectionalParticleSpeed={0.005}
            backgroundColor="rgba(0,0,0,0)"
            cooldownTicks={100}
            onNodeClick={(node) => console.log('Node clicked:', node)}
          />
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          style={{
            marginTop: '1rem',
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '0.9rem',
            fontStyle: 'italic',
            textAlign: 'center',
          }}
        >
          Click and drag nodes to explore &middot; Scroll to zoom
        </motion.p>
      </div>
    </motion.div>
  )
}

export default GraphVisualization
