(function () {
  const bootstrapElement = document.getElementById('app-bootstrap');
  let bootstrapData = {};
  if (bootstrapElement) {
    try {
      bootstrapData = JSON.parse(bootstrapElement.textContent || '{}');
    } catch (error) {
      console.error('Failed to parse bootstrap data', error);
    }
  }

  const BASE_TRIANGLE_CONFIG = bootstrapData.baseConfig || {};
  const DURATION_OPTIONS = bootstrapData.durationOptions || [];
  const DEFAULT_CITY = bootstrapData.defaultCity || {};
  const constants = bootstrapData.constants || {};
  const EARTH_RADIUS_M = constants.earthRadiusM || 1;
  const MU_EARTH = constants.muEarth || 1;
  const DEVELOPMENT_TEXT = bootstrapData.developmentText || '';

  const state = {
    view: 'home',
    running: false,
    selectedDuration: null,
    lastRun: null,
    city: DEFAULT_CITY,
    threeAnimation: null,
    threeRenderer: null,
  };

  const navButtons = Array.from(document.querySelectorAll('.nav-item'));
  const durationSelect = document.getElementById('duration-select');
  const durationHint = document.getElementById('duration-hint');
  const statusMessage = document.getElementById('status-message');
  const summaryContainer = document.getElementById('run-summary');
  const orbitalTableBody = document.querySelector('#orbital-table tbody');
  const groundTrackCanvas = document.getElementById('ground-track');
  const elementChartCanvas = document.getElementById('element-chart');
  const threeContainer = document.getElementById('three-d-view');
  const homeControls = document.getElementById('home-controls');
  const homeVisual = document.getElementById('home-visual');
  const settingsView = document.getElementById('settings-view');
  const durationNotes = document.getElementById('duration-notes');
  const citySelect = document.getElementById('city-select');
  const settingsStatus = document.getElementById('settings-status');
  const scenarioForm = document.getElementById('scenario-form');
  const settingsForm = document.getElementById('settings-form');

  function initialiseNavigation() {
    navButtons.forEach((button) => {
      button.addEventListener('click', () => {
        setView(button.dataset.view || 'home');
      });
    });
  }

  function setView(view) {
    state.view = view;
    navButtons.forEach((button) => {
      button.classList.toggle('active', button.dataset.view === view);
    });
    if (view === 'home') {
      homeControls.classList.remove('hidden');
      homeVisual.classList.remove('hidden');
      settingsView.classList.add('hidden');
    } else {
      homeControls.classList.add('hidden');
      homeVisual.classList.add('hidden');
      settingsView.classList.remove('hidden');
    }
  }

  function populateDurations() {
    if (!durationSelect || !durationNotes) return;
    durationSelect.innerHTML = '';
    durationNotes.innerHTML = '';
    const seenNotes = new Set();
    DURATION_OPTIONS.forEach((option, index) => {
      const element = document.createElement('option');
      element.value = String(option.days);
      element.textContent = option.label;
      if (index === 0) {
        element.selected = true;
        state.selectedDuration = option;
        durationHint.textContent = option.explanation || '';
      }
      durationSelect.appendChild(element);
      if (option.explanation && !seenNotes.has(option.explanation)) {
        const noteItem = document.createElement('li');
        noteItem.textContent = option.explanation;
        durationNotes.appendChild(noteItem);
        seenNotes.add(option.explanation);
      }
    });
    durationSelect.addEventListener('change', () => {
      const selectedDays = parseFloat(durationSelect.value);
      const match = DURATION_OPTIONS.find((item) => Math.abs(item.days - selectedDays) < 1e-6);
      state.selectedDuration = match || null;
      durationHint.textContent = match ? match.explanation : '';
    });
  }

  function populateCities() {
    if (!citySelect) return;
    citySelect.innerHTML = '';
    const option = document.createElement('option');
    option.value = DEFAULT_CITY.id || '';
    option.textContent = DEFAULT_CITY.label || '';
    option.selected = true;
    citySelect.appendChild(option);
    citySelect.addEventListener('change', () => {
      state.city = DEFAULT_CITY;
    });
  }

  function updateStatus(message, isError = false) {
    if (!statusMessage) return;
    statusMessage.textContent = message;
    statusMessage.classList.toggle('error', Boolean(isError));
  }

  function resetSummaries() {
    summaryContainer.innerHTML = '';
    orbitalTableBody.innerHTML = '';
    resetGroundTrack();
    resetElementChart();
    resetThreeView();
  }

  function resetGroundTrack() {
    if (!groundTrackCanvas) return;
    const ctx = groundTrackCanvas.getContext('2d');
    ctx.clearRect(0, 0, groundTrackCanvas.width, groundTrackCanvas.height);
    ctx.fillStyle = '#061830';
    ctx.fillRect(0, 0, groundTrackCanvas.width, groundTrackCanvas.height);
    ctx.fillStyle = '#94b8ff';
    ctx.font = '16px Vazirmatn, sans-serif';
    ctx.fillText('پس از اجراى سناریو مسیر پوشش نمایش داده خواهد شد.', 30, groundTrackCanvas.height / 2);
  }

  function resetElementChart() {
    if (!elementChartCanvas) return;
    const ctx = elementChartCanvas.getContext('2d');
    ctx.clearRect(0, 0, elementChartCanvas.width, elementChartCanvas.height);
    ctx.fillStyle = '#061830';
    ctx.fillRect(0, 0, elementChartCanvas.width, elementChartCanvas.height);
    ctx.fillStyle = '#94b8ff';
    ctx.font = '16px Vazirmatn, sans-serif';
    ctx.fillText('نمودار المان‌ها پس از اجرا نمایش داده مى‌شود.', 40, elementChartCanvas.height / 2);
  }

  function resetThreeView() {
    if (state.threeAnimation) {
      cancelAnimationFrame(state.threeAnimation);
      state.threeAnimation = null;
    }
    if (state.threeRenderer) {
      state.threeRenderer.dispose();
      state.threeRenderer = null;
    }
    if (threeContainer) {
      threeContainer.innerHTML = '<span class="placeholder">پس از اجراى سناریو، مدل سه‌بعدى نمایش داده مى‌شود.</span>';
    }
  }

  async function runScenario(event) {
    event.preventDefault();
    if (state.running) return;
    if (!state.selectedDuration) {
      updateStatus('اتدا مدت سناریو را مشخص کنید.', true);
      return;
    }
    state.running = true;
    updateStatus('در حال ارسال تنظیمات به شبیه‌ساز...');
    resetSummaries();
    try {
      const payload = buildScenarioPayload();
      const response = await fetch('/runs/triangle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        let detail = 'اجرای سناریو با خطا مواجه شد.';
        try {
          const errorPayload = await response.json();
          if (errorPayload && errorPayload.detail) {
            detail = errorPayload.detail;
          }
        } catch (err) {
          detail = detail;
        }
        throw new Error(detail);
      }
      const data = await response.json();
      state.lastRun = data;
      renderRunSummary(data);
      renderOrbitalTable(data.summary);
      renderGroundTrack(data.summary.geometry);
      renderElementChart(data.summary.geometry);
      renderThreeView(data.summary.geometry);
      updateStatus('سناریو با موفقیت اجرا شد.');
    } catch (error) {
      updateStatus(error.message || 'خطاى ناشناخته رخ داده است.', true);
    } finally {
      state.running = false;
    }
  }

  function buildScenarioPayload() {
    const duration = state.selectedDuration ? state.selectedDuration.days : 1;
    const config = JSON.parse(JSON.stringify(BASE_TRIANGLE_CONFIG || {}));
    if (!config.formation) {
      config.formation = {};
    }
    const durationSeconds = duration * 86400.0;
    let step = config.formation.time_step_s || 1.0;
    if (durationSeconds > 6 * 3600) {
      step = 60.0;
    }
    if (durationSeconds > 3 * 86400) {
      step = 300.0;
    }
    config.formation.duration_s = durationSeconds;
    config.formation.time_step_s = step;
    config.metadata = config.metadata || {};
    config.metadata.notes = config.metadata.notes || [];
    config.metadata.notes.push(`Duration selected in UI: ${duration} days`);
    return {
      configuration: config,
      assumptions: [
        `duration_days=${duration.toFixed(3)}`,
        `time_step_s=${step.toFixed(3)}`,
        `city=${state.city.id}`,
      ],
    };
  }

  function renderRunSummary(data) {
    summaryContainer.innerHTML = '';
    if (!data) return;
    const { run_id: runId, timestamp } = data;
    const selected = state.selectedDuration ? state.selectedDuration.label : 'نامشخص';
    const cards = [
      {
        title: 'شناسه اجرا',
        value: runId,
      },
      {
        title: 'زمان ثبت',
        value: new Date(timestamp).toLocaleString('fa-IR'),
      },
      {
        title: 'مدت انتخاب‌شده',
        value: selected,
      },
    ];
    cards.forEach((card) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'summary-card';
      const label = document.createElement('span');
      label.textContent = card.title;
      const value = document.createElement('strong');
      value.textContent = card.value;
      wrapper.append(label, value);
      summaryContainer.appendChild(wrapper);
    });
  }

  function renderOrbitalTable(summary) {
    orbitalTableBody.innerHTML = '';
    if (!summary || !summary.metrics || !summary.metrics.orbital_elements) {
      return;
    }
    const entries = summary.metrics.orbital_elements;
    Object.keys(entries).forEach((satId) => {
      const row = document.createElement('tr');
      const parameters = entries[satId] || {};
      const values = [
        satId,
        formatNumber(parameters.semi_major_axis_km),
        formatNumber(parameters.eccentricity, 6),
        formatNumber(parameters.inclination_deg),
        formatNumber(parameters.raan_deg),
        formatNumber(parameters.argument_of_perigee_deg),
      ];
      values.forEach((value) => {
        const td = document.createElement('td');
        td.textContent = value;
        row.appendChild(td);
      });
      orbitalTableBody.appendChild(row);
    });
  }

  function renderGroundTrack(geometry) {
    resetGroundTrack();
    if (!geometry || !geometry.latitudes_rad) return;
    const ctx = groundTrackCanvas.getContext('2d');
    const width = groundTrackCanvas.width;
    const height = groundTrackCanvas.height;
    const latCentre = DEFAULT_CITY.latitude_deg;
    const lonCentre = DEFAULT_CITY.longitude_deg;
    const latRange = 18;
    const lonRange = 28;
    ctx.fillStyle = '#041327';
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(126, 185, 255, 0.25)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.stroke();
    const toCanvas = (latDeg, lonDeg) => {
      const x = ((lonDeg - (lonCentre - lonRange)) / (2 * lonRange)) * width;
      const y = height - ((latDeg - (latCentre - latRange)) / (2 * latRange)) * height;
      return [Math.max(0, Math.min(width, x)), Math.max(0, Math.min(height, y))];
    };
    const colours = ['#7fd0ff', '#ffb74d', '#ce93d8', '#80cbc4'];
    (geometry.satellite_ids || []).forEach((satId, index) => {
      const lats = geometry.latitudes_rad[satId] || [];
      const lons = geometry.longitudes_rad[satId] || [];
      if (!lats.length || !lons.length) return;
      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = colours[index % colours.length];
      lats.forEach((lat, i) => {
        const latDeg = lat * (180 / Math.PI);
        let lonDeg = lons[i] * (180 / Math.PI);
        if (lonDeg - lonCentre > 180) lonDeg -= 360;
        if (lonDeg - lonCentre < -180) lonDeg += 360;
        const [x, y] = toCanvas(latDeg, lonDeg);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
    });
    const [cx, cy] = toCanvas(latCentre, lonCentre);
    ctx.fillStyle = '#ffd54f';
    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.font = '15px Vazirmatn, sans-serif';
    ctx.fillStyle = '#ffe082';
    ctx.fillText('تهران', cx + 10, cy - 10);
  }

  function renderElementChart(geometry) {
    resetElementChart();
    if (!geometry || !geometry.positions_m) return;
    const ctx = elementChartCanvas.getContext('2d');
    const width = elementChartCanvas.width;
    const height = elementChartCanvas.height;
    ctx.fillStyle = '#041327';
    ctx.fillRect(0, 0, width, height);
    const times = (geometry.times || []).map((item) => Date.parse(item));
    if (times.length < 3) return;
    const start = times[0];
    const timeSeconds = times.map((t) => (t - start) / 1000.0);
    const colours = ['#7fd0ff', '#ffb74d', '#ce93d8', '#80cbc4'];
    const metrics = [
      { key: 'semiMajorAxis', label: 'نیم‌محور بزرگ (km)' },
      { key: 'inclination', label: 'میل مدار (°)' },
      { key: 'raan', label: 'گره صعودى راست (°)' },
    ];
    const perSatellite = {};
    (geometry.satellite_ids || []).forEach((satId) => {
      const positions = geometry.positions_m[satId] || [];
      const velocities = estimateVelocities(positions, timeSeconds);
      perSatellite[satId] = computeOrbitalElementsSeries(positions, velocities);
    });
    metrics.forEach((metric, index) => {
      const top = index * (height / metrics.length);
      const panelHeight = height / metrics.length;
      drawMetricPanel(ctx, {
        top,
        height: panelHeight,
        width,
        metric,
        timeSeconds,
        perSatellite,
        colours,
      });
    });
    drawLegend(ctx, {
      colours,
      satelliteIds: geometry.satellite_ids || [],
      width,
      height,
    });
  }

  function drawMetricPanel(ctx, config) {
    const { top, height, width, metric, timeSeconds, perSatellite, colours } = config;
    ctx.save();
    ctx.strokeStyle = 'rgba(126, 185, 255, 0.2)';
    ctx.beginPath();
    ctx.rect(40, top + 10, width - 80, height - 30);
    ctx.stroke();
    const values = [];
    Object.keys(perSatellite).forEach((satId) => {
      const series = perSatellite[satId][metric.key] || [];
      series.forEach((value) => values.push(value));
    });
    if (!values.length) {
      ctx.restore();
      return;
    }
    const min = Math.min(...values);
    const max = Math.max(...values);
    const margin = (max - min) * 0.1 || 1.0;
    const lower = min - margin;
    const upper = max + margin;
    Object.keys(perSatellite).forEach((satId, index) => {
      const series = perSatellite[satId][metric.key] || [];
      if (!series.length) return;
      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = colours[index % colours.length];
      series.forEach((value, i) => {
        const x = 40 + ((timeSeconds[i] - timeSeconds[0]) / (timeSeconds[timeSeconds.length - 1] - timeSeconds[0])) * (width - 80);
        const y = top + height - 30 - ((value - lower) / (upper - lower)) * (height - 40);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
    });
    ctx.fillStyle = '#d0e4ff';
    ctx.font = '15px Vazirmatn, sans-serif';
    ctx.fillText(metric.label, 50, top + 30);
    ctx.restore();
  }

  function drawLegend(ctx, config) {
    const { colours, satelliteIds, width, height } = config;
    ctx.save();
    const startX = width - 220;
    let currentY = height - 30;
    ctx.font = '14px Vazirmatn, sans-serif';
    satelliteIds.forEach((satId, index) => {
      ctx.fillStyle = colours[index % colours.length];
      ctx.fillRect(startX + index * 70, currentY - 12, 14, 14);
      ctx.fillStyle = '#d0e4ff';
      ctx.fillText(satId, startX + index * 70 + 20, currentY);
    });
    ctx.restore();
  }

  function renderThreeView(geometry) {
    resetThreeView();
    if (!geometry || !geometry.positions_m || !window.THREE) {
      return;
    }
    const width = threeContainer.clientWidth || 480;
    const height = threeContainer.clientHeight || 360;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020b1a);
    const camera = new THREE.PerspectiveCamera(45, width / Math.max(height, 1), 0.1, 1000);
    camera.position.set(0, -4.8, 2.6);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    threeContainer.innerHTML = '';
    threeContainer.appendChild(renderer.domElement);
    state.threeRenderer = renderer;
    const ambient = new THREE.AmbientLight(0xffffff, 0.65);
    const directional = new THREE.DirectionalLight(0xffffff, 0.55);
    directional.position.set(5, 3, 5);
    scene.add(ambient);
    scene.add(directional);
    const earthGeometry = new THREE.SphereGeometry(1, 48, 48);
    const earthMaterial = new THREE.MeshPhongMaterial({
      color: 0x0b2542,
      emissive: 0x061628,
      shininess: 18,
      transparent: true,
      opacity: 0.95,
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);
    const colours = [0x7fd0ff, 0xffb74d, 0xce93d8, 0x80cbc4];
    (geometry.satellite_ids || []).forEach((satId, index) => {
      const samples = geometry.positions_m[satId] || [];
      const points = samples.map((point) => {
        return new THREE.Vector3(point[0] / EARTH_RADIUS_M, point[1] / EARTH_RADIUS_M, point[2] / EARTH_RADIUS_M);
      });
      if (!points.length) return;
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      const lineMaterial = new THREE.LineBasicMaterial({ color: colours[index % colours.length], linewidth: 2 });
      const orbitLine = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(orbitLine);
      const satelliteMesh = new THREE.Mesh(new THREE.SphereGeometry(0.035, 16, 16), new THREE.MeshBasicMaterial({ color: colours[index % colours.length] }));
      satelliteMesh.position.copy(points[points.length - 1]);
      scene.add(satelliteMesh);
    });
    const lat = DEFAULT_CITY.latitude_deg * (Math.PI / 180);
    const lon = DEFAULT_CITY.longitude_deg * (Math.PI / 180);
    const tehranMarker = new THREE.Mesh(new THREE.SphereGeometry(0.04, 16, 16), new THREE.MeshBasicMaterial({ color: 0xffd54f }));
    tehranMarker.position.set(
      Math.cos(lat) * Math.cos(lon),
      Math.cos(lat) * Math.sin(lon),
      Math.sin(lat)
    );
    scene.add(tehranMarker);
    function animate() {
      state.threeAnimation = requestAnimationFrame(animate);
      earth.rotation.y += 0.0008;
      renderer.render(scene, camera);
    }
    animate();
  }

  function estimateVelocities(positions, timeSeconds) {
    const velocities = [];
    if (!positions || positions.length !== timeSeconds.length) {
      return velocities;
    }
    for (let i = 0; i < positions.length; i += 1) {
      let dt;
      let delta;
      if (i === 0) {
        dt = timeSeconds[i + 1] - timeSeconds[i];
        delta = subtractVectors(positions[i + 1], positions[i]);
      } else if (i === positions.length - 1) {
        dt = timeSeconds[i] - timeSeconds[i - 1];
        delta = subtractVectors(positions[i], positions[i - 1]);
      } else {
        dt = timeSeconds[i + 1] - timeSeconds[i - 1];
        delta = subtractVectors(positions[i + 1], positions[i - 1]);
      }
      const scale = dt !== 0 ? 1 / dt : 0;
      velocities.push(scaleVector(delta, scale));
    }
    return velocities;
  }

  function computeOrbitalElementsSeries(positions, velocities) {
    const semiMajorAxis = [];
    const inclination = [];
    const raan = [];
    const eccentricity = [];
    for (let i = 0; i < positions.length; i += 1) {
      const r = positions[i];
      const v = velocities[i] || [0, 0, 0];
      const rMag = vectorNorm(r);
      const vMag = vectorNorm(v);
      if (rMag === 0) {
        semiMajorAxis.push(0);
        inclination.push(0);
        raan.push(0);
        eccentricity.push(0);
        continue;
      }
      const h = crossProduct(r, v);
      const hMag = vectorNorm(h);
      const n = crossProduct([0, 0, 1], h);
      const nMag = vectorNorm(n);
      const eVector = subtractVectors(scaleVector(crossProduct(v, h), 1 / MU_EARTH), scaleVector(r, 1 / rMag));
      const eMag = vectorNorm(eVector);
      eccentricity.push(eMag);
      const energy = (vMag * vMag) / 2 - MU_EARTH / rMag;
      const a = Math.abs(energy) > 1e-9 ? -MU_EARTH / (2 * energy) : Infinity;
      semiMajorAxis.push(a / 1000.0);
      const inc = hMag > 0 ? Math.acos(clamp(h[2] / hMag, -1, 1)) : 0;
      inclination.push(inc * (180 / Math.PI));
      let raanValue = 0;
      if (nMag > 1e-10) {
        raanValue = Math.acos(clamp(n[0] / nMag, -1, 1));
        if (n[1] < 0) {
          raanValue = 2 * Math.PI - raanValue;
        }
      }
      raan.push(raanValue * (180 / Math.PI));
    }
    return {
      semiMajorAxis,
      inclination,
      raan,
      eccentricity,
    };
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function subtractVectors(a, b) {
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  }

  function scaleVector(vector, scalar) {
    return [vector[0] * scalar, vector[1] * scalar, vector[2] * scalar];
  }

  function crossProduct(a, b) {
    return [
      a[1] * b[2] - a[2] * b[1],
      a[2] * b[0] - a[0] * b[2],
      a[0] * b[1] - a[1] * b[0],
    ];
  }

  function vectorNorm(vector) {
    return Math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2]);
  }

  function formatNumber(value, digits = 3) {
    if (value === undefined || value === null || Number.isNaN(value)) {
      return '—';
    }
    return Number(value).toFixed(digits);
  }

  if (scenarioForm) {
    scenarioForm.addEventListener('submit', runScenario);
  }
  if (settingsForm) {
    settingsForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (settingsStatus) {
        settingsStatus.textContent = 'تنظیمات ذخیره شد (محلى). اتصال به سناریو برقرار است.';
      }
    });
  }

  resetGroundTrack();
  resetElementChart();
  initialiseNavigation();
  populateDurations();
  populateCities();
  if (settingsStatus) {
    settingsStatus.textContent = DEVELOPMENT_TEXT;
  }
})();
