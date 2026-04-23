# CDN Libraries for Visualizations

Approved CDN libraries for use in HTML widgets. Always use specific version numbers to ensure stability.

---

## Chart.js — Simple, Responsive Charts

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
```

**Usage:**
```html
<canvas id="myChart"></canvas>
<script>
new Chart(document.getElementById('myChart'), {
  type: 'bar',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Sales',
      data: [12, 19, 3],
      backgroundColor: ['#4F46E5', '#7C3AED', '#EC4899']
    }]
  },
  options: { responsive: true }
});
</script>
```

**Best for:** Bar, line, pie, doughnut, radar, and polar area charts. Great default choice for most chart types.

---

## D3.js — Custom Data Visualizations

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
```

**Usage:**
```html
<svg id="chart" width="600" height="400"></svg>
<script>
const data = [30, 86, 168, 281, 303, 365];
const svg = d3.select('#chart');
svg.selectAll('rect')
  .data(data)
  .join('rect')
  .attr('x', (d, i) => i * 90)
  .attr('y', d => 400 - d)
  .attr('width', 80)
  .attr('height', d => d)
  .attr('fill', '#4F46E5');
</script>
```

**Best for:** Highly custom or complex visualizations — Sankey diagrams, force-directed graphs, geographic maps, treemaps.

---

## Plotly.js — Interactive Scientific Charts

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.3/plotly.min.js"></script>
```

**Usage:**
```html
<div id="plot"></div>
<script>
Plotly.newPlot('plot', [{
  x: [1, 2, 3, 4],
  y: [10, 15, 13, 17],
  type: 'scatter',
  mode: 'lines+markers'
}], { title: 'Sample Plot' });
</script>
```

**Best for:** Scientific charts, 3D plots, statistical charts, heatmaps, contour plots.

---

## Leaflet — Interactive Maps

**CDN:**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css" />
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>
```

**Usage:**
```html
<div id="map" style="height: 400px;"></div>
<script>
const map = L.map('map').setView([51.505, -0.09], 13);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);
L.marker([51.5, -0.09]).addTo(map).bindPopup('Hello!');
</script>
```

**Best for:** Interactive maps with markers, shapes, layers, and geographic data.

---

## Three.js — 3D Graphics

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.min.js"></script>
```

**Best for:** 3D visualizations, product viewers, interactive 3D scenes, generative art.

---

## Anime.js — Lightweight Animations

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
```

**Best for:** UI animations, animated dashboards, number counters, entrance effects.

---

## Mermaid — Diagrams from Text

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
```

**Usage:**
```html
<pre class="mermaid">
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Do something]
    B -->|No| D[Do something else]
</pre>
<script>mermaid.initialize({ startOnLoad: true });</script>
```

**Best for:** Flowcharts, sequence diagrams, Gantt charts, entity-relationship diagrams.
