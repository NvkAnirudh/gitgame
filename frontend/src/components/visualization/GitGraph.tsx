import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GitCommit {
  id: string;
  message: string;
  branch: string;
  parents: string[];
  timestamp: Date;
}

interface GitGraphProps {
  commits?: GitCommit[];
  width?: number;
  height?: number;
}

// Sample data for demonstration
const defaultCommits: GitCommit[] = [
  {
    id: 'c1',
    message: 'Initial commit',
    branch: 'main',
    parents: [],
    timestamp: new Date('2025-01-01'),
  },
  {
    id: 'c2',
    message: 'Add README',
    branch: 'main',
    parents: ['c1'],
    timestamp: new Date('2025-01-02'),
  },
  {
    id: 'c3',
    message: 'Create feature branch',
    branch: 'feature',
    parents: ['c2'],
    timestamp: new Date('2025-01-03'),
  },
  {
    id: 'c4',
    message: 'Add new feature',
    branch: 'feature',
    parents: ['c3'],
    timestamp: new Date('2025-01-04'),
  },
  {
    id: 'c5',
    message: 'Fix bug in main',
    branch: 'main',
    parents: ['c2'],
    timestamp: new Date('2025-01-05'),
  },
  {
    id: 'c6',
    message: 'Merge feature into main',
    branch: 'main',
    parents: ['c5', 'c4'],
    timestamp: new Date('2025-01-06'),
  },
];

export default function GitGraph({ commits = defaultCommits, width = 600, height = 400 }: GitGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || commits.length === 0) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const margin = { top: 20, right: 20, bottom: 20, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Calculate positions for each commit
    const branches = Array.from(new Set(commits.map((c) => c.branch)));
    const branchColors: Record<string, string> = {
      main: '#00ffff',
      feature: '#a855f7',
      develop: '#00ff00',
      hotfix: '#ff6b00',
    };

    // Assign x position based on branch
    const xScale = d3.scalePoint()
      .domain(branches)
      .range([0, Math.min(innerWidth, branches.length * 100)])
      .padding(0.5);

    // Assign y position based on timestamp
    const yScale = d3.scaleLinear()
      .domain([0, commits.length - 1])
      .range([0, innerHeight]);

    // Draw connections (edges)
    const links = commits.flatMap((commit, i) =>
      commit.parents.map((parentId) => {
        const parent = commits.find((c) => c.id === parentId);
        return parent ? { source: parent, target: commit } : null;
      }).filter(Boolean)
    );

    g.selectAll('.link')
      .data(links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('x1', (d: any) => xScale(d.source.branch) || 0)
      .attr('y1', (d: any) => yScale(commits.indexOf(d.source)))
      .attr('x2', (d: any) => xScale(d.target.branch) || 0)
      .attr('y2', (d: any) => yScale(commits.indexOf(d.target)))
      .attr('stroke', '#00ffff')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Draw commits (nodes)
    const nodes = g.selectAll('.node')
      .data(commits)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d, i) => `translate(${xScale(d.branch)},${yScale(i)})`);

    // Commit circles
    nodes
      .append('circle')
      .attr('r', 8)
      .attr('fill', (d) => branchColors[d.branch] || '#00ffff')
      .attr('stroke', '#000000')
      .attr('stroke-width', 2)
      .style('filter', 'drop-shadow(0 0 5px currentColor)');

    // Commit messages
    nodes
      .append('text')
      .attr('x', 15)
      .attr('y', 5)
      .attr('fill', '#e0e0e0')
      .attr('font-size', '12px')
      .attr('font-family', 'JetBrains Mono, Fira Code, monospace')
      .text((d) => d.message);

    // Commit IDs
    nodes
      .append('text')
      .attr('x', 15)
      .attr('y', -8)
      .attr('fill', '#606060')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, Fira Code, monospace')
      .text((d) => d.id);

    // Branch labels
    branches.forEach((branch) => {
      g.append('text')
        .attr('x', xScale(branch) || 0)
        .attr('y', -10)
        .attr('fill', branchColors[branch] || '#00ffff')
        .attr('font-size', '12px')
        .attr('font-family', 'JetBrains Mono, Fira Code, monospace')
        .attr('font-weight', 'bold')
        .attr('text-anchor', 'middle')
        .text(branch);
    });

  }, [commits, width, height]);

  return (
    <div className="w-full bg-cyber-black border border-neon-cyan/30 rounded-lg p-4 overflow-auto">
      <div className="mb-4">
        <h3 className="text-lg font-bold heading-neon mb-2">
          {'>'} git commit graph
        </h3>
        <p className="text-text-secondary text-sm">
          Visual representation of your Git history
        </p>
      </div>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="mx-auto"
      />
      <div className="mt-4 flex gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-neon-cyan"></div>
          <span className="text-text-secondary">main</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-electric-purple"></div>
          <span className="text-text-secondary">feature</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-neon-green"></div>
          <span className="text-text-secondary">develop</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-neon-orange"></div>
          <span className="text-text-secondary">hotfix</span>
        </div>
      </div>
    </div>
  );
}
