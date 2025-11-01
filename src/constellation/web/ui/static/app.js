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
  const CITY_LATITUDE = Number(DEFAULT_CITY.latitude_deg) || 35.6892;
  const CITY_LONGITUDE = Number(DEFAULT_CITY.longitude_deg) || 51.389;
  const constants = bootstrapData.constants || {};
  const EARTH_RADIUS_M = constants.earthRadiusM || 1;
  const MU_EARTH = constants.muEarth || 1;
  const DEVELOPMENT_TEXT = bootstrapData.developmentText || '';
  const MAP_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const MAP_TILE_OPTIONS = {
    maxZoom: 10,
    minZoom: 2,
    attribution: '© OpenStreetMap contributors',
  };
  const TRACK_COLOURS = ['#7fd0ff', '#ffb74d', '#ce93d8', '#80cbc4'];
  const RAD2DEG = 180 / Math.PI;

  const state = {
    view: 'home',
    running: false,
    selectedDuration: null,
    lastRun: null,
    city: DEFAULT_CITY,
    threeAnimation: null,
    threeRenderer: null,
    maps: {
      ground: createEmptyMapStore(),
      formation: createEmptyMapStore(),
    },
  };

  const navButtons = Array.from(document.querySelectorAll('.nav-item'));
  const durationSelect = document.getElementById('duration-select');
  const durationHint = document.getElementById('duration-hint');
  const statusMessage = document.getElementById('status-message');
  const summaryContainer = document.getElementById('run-summary');
  const orbitalTableBody = document.querySelector('#orbital-table tbody');
  const groundTrackMapContainer = document.getElementById('ground-track-map');
  const formationWindowMapContainer = document.getElementById('formation-window-map');
  const groundTrackPlaceholder = document.getElementById('ground-track-placeholder');
  const formationWindowPlaceholder = document.getElementById('formation-window-placeholder');
  const defaultGroundPlaceholderText = groundTrackPlaceholder ? groundTrackPlaceholder.textContent : '';
  const defaultFormationPlaceholderText = formationWindowPlaceholder
    ? formationWindowPlaceholder.textContent
    : '';
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
    resetFormationWindow();
    resetElementChart();
    resetThreeView();
  }

  function resetGroundTrack() {
    if (groundTrackPlaceholder) {
      groundTrackPlaceholder.textContent = defaultGroundPlaceholderText;
      togglePlaceholder(groundTrackPlaceholder, true);
    }
    clearMapOverlays('ground');
    const map = ensureLeafletMap('ground', groundTrackMapContainer);
    if (map) {
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 4);
      setTimeout(() => map.invalidateSize(), 0);
    }
  }

  function resetFormationWindow() {
    if (formationWindowPlaceholder) {
      formationWindowPlaceholder.textContent = defaultFormationPlaceholderText;
      togglePlaceholder(formationWindowPlaceholder, true);
    }
    clearMapOverlays('formation');
    const map = ensureLeafletMap('formation', formationWindowMapContainer);
    if (map) {
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 6);
      setTimeout(() => map.invalidateSize(), 0);
    }
  }

  function createEmptyMapStore() {
    return { map: null, overlays: [], baseLayer: null };
  }

  function ensureLeafletMap(key, container) {
    if (!container) {
      return null;
    }
    if (typeof window === 'undefined' || typeof window.L === 'undefined') {
      console.warn('Leaflet library is not available.');
      return null;
    }
    if (!state.maps[key]) {
      state.maps[key] = createEmptyMapStore();
    }
    const store = state.maps[key];
    if (store.map) {
      return store.map;
    }
    const map = L.map(container, {
      zoomControl: true,
      attributionControl: true,
      worldCopyJump: true,
    });
    store.map = map;
    store.baseLayer = L.tileLayer(MAP_TILE_URL, MAP_TILE_OPTIONS).addTo(map);
    return map;
  }

  function clearMapOverlays(key) {
    const store = state.maps[key];
    if (!store || !store.overlays) {
      return;
    }
    store.overlays.forEach((layer) => {
      if (!layer) {
        return;
      }
      if (typeof layer.remove === 'function') {
        layer.remove();
      } else if (store.map && typeof store.map.removeLayer === 'function') {
        store.map.removeLayer(layer);
      }
    });
    store.overlays = [];
  }

  function registerOverlay(key, layer) {
    const store = state.maps[key];
    if (!store) {
      return;
    }
    store.overlays = store.overlays || [];
    store.overlays.push(layer);
  }

  function togglePlaceholder(placeholder, visible) {
    if (!placeholder) {
      return;
    }
    placeholder.classList.toggle('hidden', !visible);
  }

  function createLegendControl(entries) {
    if (!entries.length || typeof window === 'undefined' || typeof window.L === 'undefined') {
      return null;
    }
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = () => {
      const container = L.DomUtil.create('div', 'map-legend');
      entries.forEach((entry) => {
        const item = L.DomUtil.create('div', 'map-legend-item', container);
        const swatch = L.DomUtil.create('span', 'map-legend-swatch', item);
        swatch.style.backgroundColor = entry.colour;
        const label = L.DomUtil.create('span', 'map-legend-label', item);
        label.textContent = entry.label;
      });
      return container;
    };
    return legend;
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
      renderFormationWindow(data.summary.geometry, data.summary.metrics);
      renderElementChart(data.summary.geometry);
      renderThreeView(data.summary.geometry, data.summary.metrics);
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
    if (!summary) {
      return;
    }
    const entries = buildOrbitalSnapshot(summary);
    if (!entries) {
      return;
    }
    const satelliteIds = Object.keys(entries).filter((key) => {
      const candidate = entries[key];
      return candidate && typeof candidate === 'object' && ('semi_major_axis_km' in candidate || 'semiMajorAxis' in candidate);
    });
    satelliteIds.sort();
    satelliteIds.forEach((satId) => {
      const row = document.createElement('tr');
      const parameters = entries[satId] || {};
      const values = [
        satId,
        formatNumber(parameters.semi_major_axis_km ?? parameters.semiMajorAxis),
        formatNumber(parameters.eccentricity, 6),
        formatNumber(parameters.inclination_deg ?? parameters.inclination),
        formatNumber(parameters.raan_deg ?? parameters.raan),
        formatNumber(parameters.argument_of_perigee_deg ?? parameters.argumentOfPerigee),
      ];
      values.forEach((value) => {
        const td = document.createElement('td');
        td.textContent = value;
        row.appendChild(td);
      });
      orbitalTableBody.appendChild(row);
    });
  }

  function buildOrbitalSnapshot(summary) {
    const metrics = summary.metrics || {};
    const orbital = metrics.orbital_elements || {};
    if (orbital && orbital.per_satellite && Object.keys(orbital.per_satellite).length) {
      return orbital.per_satellite;
    }
    const geometry = summary.geometry || {};
    const classical = geometry.classical_elements || {};
    const satelliteIds = geometry.satellite_ids || Object.keys(classical);
    if (!satelliteIds || !satelliteIds.length) {
      return null;
    }
    const times = geometry.times || [];
    const centreIndex = times.length ? Math.floor(times.length / 2) : 0;
    const snapshot = {};
    satelliteIds.forEach((satId) => {
      const elements = classical[satId];
      if (!elements) {
        return;
      }
      snapshot[satId] = {
        semi_major_axis_km: pickSeriesValue(elements.semi_major_axis_km, centreIndex),
        eccentricity: pickSeriesValue(elements.eccentricity, centreIndex),
        inclination_deg: pickSeriesValue(elements.inclination_deg, centreIndex),
        raan_deg: pickSeriesValue(elements.raan_deg, centreIndex),
        argument_of_perigee_deg: pickSeriesValue(elements.argument_of_perigee_deg, centreIndex),
      };
    });
    return Object.keys(snapshot).length ? snapshot : null;
  }

  function pickSeriesValue(series, index) {
    if (!Array.isArray(series) || !series.length) {
      return null;
    }
    const clamped = Math.min(Math.max(index, 0), series.length - 1);
    const value = Number(series[clamped]);
    return Number.isFinite(value) ? value : null;
  }

  function renderGroundTrack(geometry) {
    clearMapOverlays('ground');
    const map = ensureLeafletMap('ground', groundTrackMapContainer);
    if (!map) {
      if (groundTrackPlaceholder) {
        groundTrackPlaceholder.textContent = 'کتابخانهٔ نقشه در دسترس نیست.';
        togglePlaceholder(groundTrackPlaceholder, true);
      }
      return;
    }

    if (!geometry || !geometry.latitudes_rad || !(geometry.satellite_ids || []).length) {
      if (groundTrackPlaceholder) {
        groundTrackPlaceholder.textContent = 'داده‌اى براى گراوند ترک یافت نشد.';
        togglePlaceholder(groundTrackPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 4);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const boundsPoints = [];
    const legendEntries = [];

    (geometry.satellite_ids || []).forEach((satId, index) => {
      const lats = geometry.latitudes_rad[satId];
      const lons = geometry.longitudes_rad[satId];
      const segments = buildTrackSegments(lats, lons);
      if (!segments.length) {
        return;
      }
      segments.forEach((segment) => {
        const polyline = L.polyline(segment, {
          color: TRACK_COLOURS[index % TRACK_COLOURS.length],
          weight: 3,
          opacity: 0.85,
        }).addTo(map);
        registerOverlay('ground', polyline);
        segment.forEach((point) => boundsPoints.push([point[0], point[1]]));
      });
      legendEntries.push({ colour: TRACK_COLOURS[index % TRACK_COLOURS.length], label: satId });
    });

    if (!legendEntries.length) {
      if (groundTrackPlaceholder) {
        groundTrackPlaceholder.textContent = 'مسیرى براى نمایش موجود نیست.';
        togglePlaceholder(groundTrackPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 4);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const tehranMarker = L.circleMarker([CITY_LATITUDE, CITY_LONGITUDE], {
      radius: 6,
      color: '#ffd54f',
      weight: 2,
      fillColor: '#ffe082',
      fillOpacity: 1,
    }).addTo(map);
    tehranMarker.bindTooltip('تهران', { direction: 'top', permanent: true, className: 'map-tooltip' });
    registerOverlay('ground', tehranMarker);

    const legend = createLegendControl(legendEntries);
    if (legend) {
      legend.addTo(map);
      registerOverlay('ground', legend);
    }

    togglePlaceholder(groundTrackPlaceholder, false);

    if (boundsPoints.length) {
      const bounds = L.latLngBounds(boundsPoints);
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.18));
      }
    } else {
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 4);
    }
    setTimeout(() => map.invalidateSize(), 200);
  }

  function renderFormationWindow(geometry, metrics) {
    clearMapOverlays('formation');
    const map = ensureLeafletMap('formation', formationWindowMapContainer);
    if (!map) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'کتابخانهٔ نقشه در دسترس نیست.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      return;
    }

    if (!geometry || !geometry.latitudes_rad) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'داده‌اى براى بازهٔ فورمیشن یافت نشد.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const windowInfo = metrics && metrics.formation_window;
    if (!windowInfo || !windowInfo.start || !windowInfo.end) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'خروجى شامل بازهٔ فورمیشن معتبر نیست.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const startEpoch = Date.parse(windowInfo.start);
    const endEpoch = Date.parse(windowInfo.end);
    if (Number.isNaN(startEpoch) || Number.isNaN(endEpoch)) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'زمان‌بندى بازهٔ فورمیشن قابل تفسیر نیست.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const timeSeries = (geometry.times || []).map((value) => Date.parse(value));
    if (!timeSeries.length || timeSeries.every((value) => Number.isNaN(value))) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'نمونه‌هاى زمانى براى بازهٔ فورمیشن موجود نیست.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const boundsPoints = [];
    const legendEntries = [];

    (geometry.satellite_ids || []).forEach((satId, index) => {
      const lats = geometry.latitudes_rad[satId];
      const lons = geometry.longitudes_rad[satId];
      const maskedLatitudes = [];
      const maskedLongitudes = [];
      for (let i = 0; i < (lats || []).length; i += 1) {
        const epoch = timeSeries[i];
        if (Number.isFinite(epoch) && epoch >= startEpoch && epoch <= endEpoch) {
          maskedLatitudes.push(lats[i]);
          maskedLongitudes.push(lons[i]);
        } else {
          maskedLatitudes.push(Number.NaN);
          maskedLongitudes.push(Number.NaN);
        }
      }
      const segments = buildTrackSegments(maskedLatitudes, maskedLongitudes);
      if (!segments.length) {
        return;
      }
      segments.forEach((segment) => {
        const polyline = L.polyline(segment, {
          color: TRACK_COLOURS[index % TRACK_COLOURS.length],
          weight: 4,
          opacity: 0.95,
        }).addTo(map);
        registerOverlay('formation', polyline);
        segment.forEach((point) => boundsPoints.push([point[0], point[1]]));
      });
      const firstSegment = segments[0];
      const lastSegment = segments[segments.length - 1];
      const startPoint = firstSegment[0];
      const endPoint = lastSegment[lastSegment.length - 1];
      const startMarker = L.circleMarker(startPoint, {
        radius: 4,
        color: '#ffffff',
        weight: 1,
        fillColor: TRACK_COLOURS[index % TRACK_COLOURS.length],
        fillOpacity: 0.9,
      }).addTo(map);
      registerOverlay('formation', startMarker);
      const endMarker = L.circleMarker(endPoint, {
        radius: 4,
        color: '#121b2c',
        weight: 2,
        fillColor: TRACK_COLOURS[index % TRACK_COLOURS.length],
        fillOpacity: 1,
      }).addTo(map);
      registerOverlay('formation', endMarker);
      legendEntries.push({ colour: TRACK_COLOURS[index % TRACK_COLOURS.length], label: satId });
    });

    if (!legendEntries.length) {
      if (formationWindowPlaceholder) {
        formationWindowPlaceholder.textContent = 'رد زمینی براى بازهٔ فورمیشن موجود نیست.';
        togglePlaceholder(formationWindowPlaceholder, true);
      }
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
      setTimeout(() => map.invalidateSize(), 200);
      return;
    }

    const tehranMarker = L.circleMarker([CITY_LATITUDE, CITY_LONGITUDE], {
      radius: 6,
      color: '#ffd54f',
      weight: 2,
      fillColor: '#ffe082',
      fillOpacity: 1,
    }).addTo(map);
    tehranMarker.bindTooltip('تهران', { direction: 'top', permanent: true, className: 'map-tooltip' });
    registerOverlay('formation', tehranMarker);

    const legend = createLegendControl(legendEntries);
    if (legend) {
      legend.addTo(map);
      registerOverlay('formation', legend);
    }

    togglePlaceholder(formationWindowPlaceholder, false);

    if (boundsPoints.length) {
      const bounds = L.latLngBounds(boundsPoints);
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.22));
      }
    } else {
      map.setView([CITY_LATITUDE, CITY_LONGITUDE], 7);
    }
    setTimeout(() => map.invalidateSize(), 200);
  }

  function renderElementChart(geometry) {
    resetElementChart();
    if (!geometry || !geometry.times || !geometry.satellite_ids) return;
    const ctx = elementChartCanvas.getContext('2d');
    const width = elementChartCanvas.width;
    const height = elementChartCanvas.height;
    ctx.fillStyle = '#041327';
    ctx.fillRect(0, 0, width, height);
    const timeEpochs = (geometry.times || []).map((item) => Date.parse(item));
    if (timeEpochs.length < 2 || timeEpochs.some((value) => Number.isNaN(value))) {
      return;
    }
    const start = timeEpochs[0];
    const timeSeconds = timeEpochs.map((t) => (t - start) / 1000.0);
    const colours = TRACK_COLOURS;
    const metrics = [
      { key: 'semiMajorAxis', label: 'نیم‌محور بزرگ (km)' },
      { key: 'eccentricity', label: 'اگزا‌نتریسیته' },
      { key: 'inclination', label: 'میل مدار (°)' },
      { key: 'raan', label: 'گره صعودى راست (°)' },
    ];

    const perSatellite = buildOrbitalElementSeries(geometry, timeSeconds);
    const availableMetrics = metrics.filter((metric) => {
      return Object.values(perSatellite).some((series) => Array.isArray(series[metric.key]) && series[metric.key].length);
    });
    if (!availableMetrics.length) {
      return;
    }

    availableMetrics.forEach((metric, index) => {
      const top = index * (height / availableMetrics.length);
      const panelHeight = height / availableMetrics.length;
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
      series.forEach((value) => {
        if (typeof value === 'number' && Number.isFinite(value)) {
          values.push(value);
        }
      });
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
    const duration = Math.max(timeSeconds[timeSeconds.length - 1] - timeSeconds[0], 1e-6);
    Object.keys(perSatellite).forEach((satId, index) => {
      const series = perSatellite[satId][metric.key] || [];
      if (!series.length) return;
      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = colours[index % colours.length];
      series.forEach((value, i) => {
        if (!Number.isFinite(value)) {
          return;
        }
        const x = 40 + ((timeSeconds[i] - timeSeconds[0]) / duration) * (width - 80);
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
    if (!satelliteIds.length) return;
    ctx.save();
    const padding = 18;
    const entryWidth = 120;
    const startX = width - padding - entryWidth * Math.min(satelliteIds.length, 3);
    const baselineY = height - 24;
    ctx.font = '14px Vazirmatn, sans-serif';
    satelliteIds.forEach((satId, index) => {
      const column = index % 3;
      const row = Math.floor(index / 3);
      const x = startX + column * entryWidth;
      const y = baselineY - row * 22;
      ctx.fillStyle = colours[index % colours.length];
      ctx.fillRect(x, y - 12, 14, 14);
      ctx.fillStyle = '#d0e4ff';
    ctx.fillText(satId, x + 20, y);
    });
    ctx.restore();
  }

  function buildTrackSegments(latitudes, longitudes) {
    if (!Array.isArray(latitudes) || !Array.isArray(longitudes) || latitudes.length !== longitudes.length) {
      return [];
    }
    const segments = [];
    let current = [];
    let previousLongitude = null;
    for (let i = 0; i < latitudes.length; i += 1) {
      const lat = latitudes[i];
      const lon = longitudes[i];
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
        if (current.length) {
          segments.push(current);
        }
        current = [];
        previousLongitude = null;
        continue;
      }
      const latDeg = lat * RAD2DEG;
      const lonDeg = normaliseLongitude(lon * RAD2DEG);
      if (previousLongitude !== null && Math.abs(lonDeg - previousLongitude) > 180) {
        if (current.length) {
          segments.push(current);
        }
        current = [];
      }
      current.push([latDeg, lonDeg]);
      previousLongitude = lonDeg;
    }
    if (current.length) {
      segments.push(current);
    }
    return segments;
  }

  function buildOrbitalElementSeries(geometry, timeSeconds) {
    const perSatellite = {};
    const satIds = geometry.satellite_ids || [];
    const classical = geometry.classical_elements || {};
    const hasClassical = satIds.length > 0 && satIds.every((satId) => classical[satId]);
    if (hasClassical) {
      satIds.forEach((satId) => {
        const elements = classical[satId] || {};
        perSatellite[satId] = {
          semiMajorAxis: (elements.semi_major_axis_km || []).map(Number),
          eccentricity: (elements.eccentricity || []).map(Number),
          inclination: (elements.inclination_deg || []).map(Number),
          raan: (elements.raan_deg || []).map(Number),
        };
      });
      return perSatellite;
    }

    satIds.forEach((satId) => {
      const positions = geometry.positions_m[satId] || [];
      const velocities = estimateVelocities(positions, timeSeconds);
      perSatellite[satId] = computeOrbitalElementsSeries(positions, velocities);
    });
    return perSatellite;
  }


  function renderThreeView(geometry, metrics) {
    resetThreeView();
    if (!geometry || !geometry.positions_m || !window.THREE || !threeContainer) {
      return;
    }

    const satelliteIds = geometry.satellite_ids || [];
    if (!satelliteIds.length) {
      return;
    }

    const timeSeries = Array.isArray(geometry.times)
      ? geometry.times.map((value) => Date.parse(value))
      : [];
    const windowInfo = metrics && metrics.formation_window;
    let windowBounds = null;
    if (
      windowInfo &&
      windowInfo.start &&
      windowInfo.end &&
      timeSeries.length &&
      timeSeries.some((value) => Number.isFinite(value))
    ) {
      const startEpoch = Date.parse(windowInfo.start);
      const endEpoch = Date.parse(windowInfo.end);
      if (Number.isFinite(startEpoch) && Number.isFinite(endEpoch)) {
        const indices = [];
        timeSeries.forEach((epoch, index) => {
          if (Number.isFinite(epoch) && epoch >= startEpoch && epoch <= endEpoch) {
            indices.push(index);
          }
        });
        if (indices.length) {
          const minIndex = Math.min(...indices);
          const maxIndex = Math.max(...indices);
          const expandedMin = Math.max(minIndex - 1, 0);
          const expandedMax = Math.min(maxIndex + 1, timeSeries.length - 1);
          windowBounds = {
            minIndex: expandedMin,
            maxIndex: expandedMax,
            enforce: true,
          };
        } else {
          windowBounds = { minIndex: null, maxIndex: null, enforce: true };
        }
      }
    }

    const colours = [0x7fd0ff, 0xffb74d, 0xce93d8, 0x80cbc4];
    const tracks = [];
    satelliteIds.forEach((satId, index) => {
      const samples = geometry.positions_m[satId] || [];
      if (!Array.isArray(samples) || !samples.length) {
        return;
      }
      let startIndex = 0;
      let endIndex = samples.length;
      if (windowBounds) {
        if (
          windowBounds.minIndex !== null &&
          windowBounds.maxIndex !== null &&
          windowBounds.maxIndex >= windowBounds.minIndex
        ) {
          const boundedStart = Math.max(Math.min(windowBounds.minIndex, samples.length - 1), 0);
          const boundedEnd = Math.min(
            Math.max(windowBounds.maxIndex + 1, boundedStart + 1),
            samples.length
          );
          startIndex = boundedStart;
          endIndex = boundedEnd;
        } else if (windowBounds.enforce) {
          return;
        }
      }
      const subset = samples
        .slice(startIndex, endIndex)
        .filter(
          (point) =>
            Array.isArray(point) &&
            point.length >= 3 &&
            point.every((value) => Number.isFinite(value))
        );
      if (!subset.length) {
        return;
      }
      tracks.push({
        satId,
        colour: colours[index % colours.length],
        samples: subset,
      });
    });

    if (!tracks.length) {
      threeContainer.innerHTML =
        '<span class="placeholder">نمونه‌اى براى بازهٔ فورمیشن در دسترس نیست.</span>';
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

    tracks.forEach((track) => {
      const points = track.samples.map((point) => {
        return new THREE.Vector3(
          point[0] / EARTH_RADIUS_M,
          point[1] / EARTH_RADIUS_M,
          point[2] / EARTH_RADIUS_M
        );
      });
      if (!points.length) {
        return;
      }
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      const lineMaterial = new THREE.LineBasicMaterial({ color: track.colour, linewidth: 2 });
      const orbitLine = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(orbitLine);
      const satelliteMesh = new THREE.Mesh(
        new THREE.SphereGeometry(0.035, 16, 16),
        new THREE.MeshBasicMaterial({ color: track.colour })
      );
      satelliteMesh.position.copy(points[points.length - 1]);
      scene.add(satelliteMesh);
    });

    const lat = CITY_LATITUDE * (Math.PI / 180);
    const lon = CITY_LONGITUDE * (Math.PI / 180);
    const tehranMarker = new THREE.Mesh(
      new THREE.SphereGeometry(0.04, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xffd54f })
    );
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

  function normaliseLongitude(lonDeg) {
    if (!Number.isFinite(lonDeg)) {
      return Number.NaN;
    }
    let wrapped = ((lonDeg + 180) % 360 + 360) % 360 - 180;
    if (wrapped === -180) {
      wrapped = 180;
    }
    return wrapped;
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
  resetFormationWindow();
  resetElementChart();
  initialiseNavigation();
  populateDurations();
  populateCities();
  if (settingsStatus) {
    settingsStatus.textContent = DEVELOPMENT_TEXT;
  }
})();
