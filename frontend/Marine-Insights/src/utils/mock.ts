// Centralized mock data generators to simulate backend responses

export type MockPlot = { data: any[]; layout: any };

export function mockForecastInteractive(): MockPlot {
	// Mimic screenshot: Actual Stock (dots) 2000-2020 and Polynomial Forecast (blue line) to 2030
	const yearsFull: number[] = [];
	for (let y = 2000; y <= 2030; y += 1) yearsFull.push(y);

	// Build a gentle accelerating curve reaching ~260 by 2030
	const baseYear = 2000;
	const forecast: number[] = yearsFull.map((y) => {
		const t = y - baseYear; // 0..30
		return 55 + 0.6 * t + 0.22 * t * t; // quadratic growth
	});

	// Actuals up to 2020 around the curve with slight noise
	const actualYears: number[] = [];
	const actualValues: number[] = [];
	for (let y = 2000; y <= 2020; y += 1) {
		actualYears.push(y);
		const t = y - baseYear;
		const trueVal = 55 + 0.6 * t + 0.22 * t * t;
		const noise = (Math.random() - 0.5) * 2.0; // small jitter
		actualValues.push(Math.max(50, trueVal + noise));
	}

	return {
		data: [
			{
				x: actualYears.map(String),
				y: actualValues,
				type: 'scatter',
				mode: 'markers',
				name: 'Actual Stock',
				marker: { color: 'black', size: 6 }
			},
			{
				x: yearsFull.map(String),
				y: forecast,
				type: 'scatter',
				mode: 'lines',
				name: 'Polynomial Forecast',
				line: { color: '#1f77b4', width: 3 }
			}
		],
		layout: {
			title: { text: 'Fish Stock Forecast (Crystal Ball)', font: { color: 'white', size: 18 } },
			xaxis: { title: 'Year', color: 'white', gridcolor: 'rgba(255,255,255,0.15)' },
			yaxis: { title: 'Stock Quantity', color: 'white', gridcolor: 'rgba(255,255,255,0.15)' },
			plot_bgcolor: 'rgba(0,0,0,0)',
			paper_bgcolor: 'rgba(0,0,0,0)',
			font: { color: 'white' },
			legend: { bgcolor: 'rgba(255,255,255,0.1)', bordercolor: 'rgba(255,255,255,0.2)' }
		}
	};
}

export function mockSST(): MockPlot {
	// Generate realistic seasonal SST with slight warming trend and 18-month forecast
	const histStart = new Date(Date.UTC(2020, 0, 1));
	const histEnd = new Date(Date.UTC(2024, 11, 1));
	const histX: string[] = [];
	const histY: number[] = [];

	const monthlyTrend = 0.02; // ~0.24°C/year warming
	const baseline = 20; // °C
	const amplitude = 6; // seasonal swing

	let cursor = new Date(histStart);
	let monthIndex = 0;
	while (cursor <= histEnd) {
		const label = `${cursor.getUTCFullYear()}-${String(cursor.getUTCMonth() + 1).padStart(2, '0')}`;
		histX.push(label);
		const seasonal = amplitude * Math.sin((2 * Math.PI * (cursor.getUTCMonth())) / 12 - Math.PI / 2); // warmest ~Aug
		const trend = monthlyTrend * monthIndex;
		const noise = (Math.random() - 0.5) * 0.6;
		histY.push(Number((baseline + seasonal + trend + noise).toFixed(2)));
		monthIndex += 1;
		cursor = new Date(Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1));
	}

	// Forecast next 18 months continuing seasonality & trend with reduced noise
	const fcX: string[] = [];
	const fcY: number[] = [];
	for (let i = 1; i <= 18; i += 1) {
		const date = new Date(Date.UTC(histEnd.getUTCFullYear(), histEnd.getUTCMonth() + i, 1));
		const label = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
		fcX.push(label);
		const seasonal = amplitude * Math.sin((2 * Math.PI * (date.getUTCMonth())) / 12 - Math.PI / 2);
		const trend = monthlyTrend * (monthIndex + i - 1);
		const noise = (Math.random() - 0.5) * 0.3;
		fcY.push(Number((baseline + seasonal + trend + noise).toFixed(2)));
	}

	return {
		data: [
			{ x: histX, y: histY, type: 'scatter', mode: 'lines', name: 'Historical SST', line: { color: '#00C9D9', width: 3 } },
			{ x: fcX, y: fcY, type: 'scatter', mode: 'lines', name: 'SST Forecast', line: { color: '#F1C40F', width: 3, dash: 'dash' } }
		],
		layout: {
			title: { text: 'Sea Surface Temperature - Historical & Forecast', font: { color: 'white', size: 18 } },
			xaxis: { title: 'Date', color: 'white', gridcolor: 'rgba(255,255,255,0.1)' },
			yaxis: { title: 'Temperature (°C)', color: 'white', gridcolor: 'rgba(255,255,255,0.1)' },
			plot_bgcolor: 'rgba(0,0,0,0)',
			paper_bgcolor: 'rgba(0,0,0,0)',
			font: { color: 'white' }
		}
	};
}

export function mockDepth(): MockPlot {
	// Build depth profile mimicking provided screenshot
	const depths: number[] = [];
	for (let d = 900; d >= 0; d -= 10) depths.push(d);

	const chlorophyll: number[] = depths.map((d) => {
		// Low at deep ocean, sharp peak around ~80 m, drop to surface
		const peakDepth = 80; // meters
		const peak = Math.exp(-Math.pow(d - peakDepth, 2) / (2 * Math.pow(18, 2))) * 0.8; // peak ~0.8
		const baseline = 0.02 + (d > 300 ? 0.01 : 0.0);
		const noise = (Math.random() - 0.5) * 0.01;
		return Math.max(0, baseline + peak + noise);
	});

	const pH: number[] = depths.map((d) => {
		// Slightly higher pH at depth (~8.1) tapering to ~6.0 near surface
		const val = 6.0 + 2.1 * (d / 900);
		const noise = (Math.random() - 0.5) * 0.03;
		return Math.max(5.5, Math.min(9.0, val + noise));
	});

	const salinity: number[] = depths.map((d) => {
		// Around 34.9 PSU with small variability, occasional spikes/dips
		let val = 34.8 + 0.2 * (d / 900); // slightly higher at depth
		val += (Math.random() - 0.5) * 0.08;
		// Introduce a few localized anomalies similar to screenshot
		if (d > 820 && d < 860) val -= 0.8;
		if (d > 740 && d < 780) val -= 0.5;
		if (d > 380 && d < 420) val -= 0.9;
		return Math.max(33.0, Math.min(35.5, val));
	});

	return {
		data: [
			{ x: depths, y: chlorophyll, type: 'scatter', mode: 'lines', name: 'Chlorophyll (mg/m³)', line: { color: '#2ECC71', width: 3 } },
			{ x: depths, y: pH, type: 'scatter', mode: 'lines', name: 'pH Level', line: { color: '#F1C40F', width: 3 }, yaxis: 'y2' },
			{ x: depths, y: salinity, type: 'scatter', mode: 'lines', name: 'Salinity (PSU)', line: { color: '#FF6B6B', width: 3 }, yaxis: 'y3' }
		],
		layout: {
			title: { text: 'Ocean Depth Profiles', font: { color: 'white', size: 18 } },
			xaxis: { title: 'Depth (m)', color: 'white', gridcolor: 'rgba(255,255,255,0.1)', autorange: 'reversed' },
			yaxis: { title: 'Chlorophyll (mg/m³)', color: '#2ECC71', gridcolor: 'rgba(255,255,255,0.1)', side: 'left', range: [0, 0.9] },
			yaxis2: { title: 'pH / Salinity', color: '#F1C40F', overlaying: 'y', side: 'right', showgrid: false, range: [5, 36] },
			yaxis3: { title: 'Salinity (PSU)', color: '#FF6B6B', overlaying: 'y', side: 'right', position: 0.85, showgrid: false, range: [5, 36], showticklabels: false },
			plot_bgcolor: 'rgba(0,0,0,0)',
			paper_bgcolor: 'rgba(0,0,0,0)',
			font: { color: 'white' },
			legend: { bgcolor: 'rgba(255,255,255,0.1)', bordercolor: 'rgba(255,255,255,0.2)' }
		}
	};
}

export type MockEdnaItem = {
	sequence: string;
	sequenceId: string;
	species: string;
	confidence: number;
	invasive?: boolean;
};

export function mockEdnaAnalyze(): MockEdnaItem[] {
	return [
		{ sequence: 'ATCGATCGATCGATCGATCG', sequenceId: 'MN908947.3|COI|Gadus_morhua', species: 'Atlantic Cod (Gadus morhua)', confidence: 94, invasive: false },
		{ sequence: 'GCTAGCTAGCTAGCTAGCTA', sequenceId: 'NC_002614.1|16S|Phoca_vitulina', species: 'Harbor Seal (Phoca vitulina)', confidence: 89, invasive: false },
		{ sequence: 'TTAATTAATTAATTAATTAA', sequenceId: 'AY497292.1|COI|Mytilus_edulis', species: 'Blue Mussel (Mytilus edulis)', confidence: 76, invasive: false },
		{ sequence: 'CGCGCGCGCGCGCGCGCGCG', sequenceId: 'KF021605.1|COI|Oreochromis_niloticus', species: 'Nile Tilapia (Oreochromis niloticus)', confidence: 82, invasive: true },
		{ sequence: 'AAAATTTTAAAATTTTAAAA', sequenceId: 'EU497761.1|COI|Carcinus_maenas', species: 'European Green Crab (Carcinus maenas)', confidence: 71, invasive: false }
	];
}

let __mockClassificationCallCount = 0;
export function mockFishClassification(): { species: string; confidence: string } {
	const order = ['Neon Tetra', 'Zebra Danio', 'Clownfish'];
	const species = order[__mockClassificationCallCount % order.length];
	__mockClassificationCallCount += 1;
	const confidenceValue = Math.random() * (87 - 75) + 75; // 75 to 87
	const confidence = confidenceValue.toFixed(2) + '%';
	return { species, confidence };
}


