// file location: frontend/src/utils/visualization.ts
import Plotly from 'plotly.js-dist';

interface Point3D {
    word: string;
    coordinates: [number, number, number];
    is_target: boolean;
    similarity?: number;  // similarity in [0,1] ideally
}

function getColor(similarity: number | undefined, isTarget: boolean): string {
    // If it's the target, return a distinct color (e.g. bright red).
    if (isTarget) {
        return 'rgb(255, 0, 0)';
    }
    // If similarity isn't defined, use gray.
    if (similarity === undefined) {
        return 'rgb(128, 128, 128)';
    }

    // Clamp similarity to [0,1].
    const sim = Math.max(0, Math.min(1, similarity));
    // Continuous gradient from blue (0,0,255) to red (255,0,0).
    const r = Math.floor(sim * 255);
    const g = 0;
    const b = Math.floor((1 - sim) * 255);
    return `rgb(${r}, ${g}, ${b})`;
}

export function create3DVisualization(data: Point3D[], containerId: string) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Calculate container dimensions
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Prepare arrays for Plotly
    const words = data.map(p => (p.is_target ? '' : p.word));
    const x = data.map(p => p.coordinates[0]);
    const y = data.map(p => p.coordinates[1]);
    const z = data.map(p => p.coordinates[2]);

    // Map each point to a color based on its similarity
    const colors = data.map(p => getColor(p.similarity, p.is_target));

    // Marker sizes: bigger for more similar guesses
    const sizes = data.map(p => {
        if (p.is_target) return 15;
        if (!p.similarity) return 8;
        return 8 + p.similarity * 7;
    });

    const trace = {
        type: 'scatter3d',
        mode: 'markers+text',
        x: x,
        y: y,
        z: z,
        text: words,
        textposition: 'top center',
        textfont: {
            size: 12,
            color: 'rgb(60, 60, 60)'
        },
        hovertext: data.map(p => {
            if (p.is_target) return 'Mot cible';
            return `${p.word}${p.similarity ? ` (${(p.similarity * 100).toFixed(1)}%)` : ''}`;
        }),
        hoverinfo: 'text',
        hoverlabel: {
            bgcolor: 'rgba(255, 255, 255, 0.9)',
            bordercolor: 'rgba(0, 0, 0, 0.1)',
            font: { size: 14 }
        },
        marker: {
            size: sizes,
            color: colors,
            opacity: 0.85,
            line: {
                width: 1,
                color: 'rgb(255, 255, 255)'
            },
            symbol: data.map(p => (p.is_target ? 'diamond' : 'circle'))
        }
    };

    const layout = {
        width: width,
        height: height,
        margin: { l: 0, r: 0, b: 0, t: 0 },
        scene: {
            xaxis: {
                showticklabels: false,
                showgrid: true,
                zeroline: true,
                showline: false,
                gridcolor: 'rgb(240, 240, 240)',
                gridwidth: 1
            },
            yaxis: {
                showticklabels: false,
                showgrid: true,
                zeroline: true,
                showline: false,
                gridcolor: 'rgb(240, 240, 240)',
                gridwidth: 1
            },
            zaxis: {
                showticklabels: false,
                showgrid: true,
                zeroline: true,
                showline: false,
                gridcolor: 'rgb(240, 240, 240)',
                gridwidth: 1
            },
            camera: {
                eye: { x: 1.75, y: 1.75, z: 1.75 },
                center: { x: 0, y: 0, z: 0 },
                up: { x: 0, y: 0, z: 1 }
            },
            aspectmode: 'cube'
        },
        showlegend: false,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        annotations: [
            {
                text: 'Double-cliquez pour réinitialiser la vue',
                xref: 'paper',
                yref: 'paper',
                x: 0,
                y: 1,
                xanchor: 'left',
                yanchor: 'top',
                font: {
                    size: 12,
                    color: 'rgb(150, 150, 150)'
                },
                showarrow: false
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: [
            'toImage', 
            'sendDataToCloud',
            'select2d',
            'lasso2d',
            'zoomIn2d',
            'zoomOut2d',
            'autoScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian'
        ],
        displaylogo: false
    };

    // Create the plot
    Plotly.newPlot(containerId, [trace], layout, config);

    // Add window resize handler
    window.addEventListener('resize', () => {
        const el = document.getElementById(containerId);
        if (el) {
            Plotly.Plots.resize(el);
        }
    });
}
