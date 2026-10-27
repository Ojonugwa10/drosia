/**
 * Tactical GIS Map Component using Leaflet
 * Displays Flown Tracks, Planned Routes, Geofences, and Geo-located Incidents with Evidence
 */

const tacticalMap = {
  map: null,
  layers: {
    track: null,
    planned: null,
    incidents: null,
  },

  init() {
    const mapContainer = document.getElementById('tactical-leaflet-map');
    if (!mapContainer || !window.L) return;

    if (!this.map) {
      // Default centered on Lekki Free Zone, Lagos Nigeria [6.4253, 3.8614]
      this.map = L.map('tactical-leaflet-map', {
        zoomControl: false,
        attributionControl: false,
      }).setView([6.4253, 3.8614], 14);

      L.control.zoom({ position: 'bottomright' }).addTo(this.map);

      // CartoDB Dark Matter tactical basemap tiles
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
      }).addTo(this.map);

      this.layers.track = L.layerGroup().addTo(this.map);
      this.layers.planned = L.layerGroup().addTo(this.map);
      this.layers.incidents = L.layerGroup().addTo(this.map);

      this.bindLayerControls();
    }

    this.loadLayers();
  },

  bindLayerControls() {
    const toggleTrack = document.getElementById('toggle-actual-track');
    const togglePlanned = document.getElementById('toggle-planned-route');
    const toggleIncidents = document.getElementById('toggle-incidents');

    if (toggleTrack) {
      toggleTrack.addEventListener('change', (e) => {
        if (e.target.checked) this.map.addLayer(this.layers.track);
        else this.map.removeLayer(this.layers.track);
      });
    }

    if (togglePlanned) {
      togglePlanned.addEventListener('change', (e) => {
        if (e.target.checked) this.map.addLayer(this.layers.planned);
        else this.map.removeLayer(this.layers.planned);
      });
    }

    if (toggleIncidents) {
      toggleIncidents.addEventListener('change', (e) => {
        if (e.target.checked) this.map.addLayer(this.layers.incidents);
        else this.map.removeLayer(this.layers.incidents);
      });
    }
  },

  async loadLayers() {
    if (!this.map) return;
    try {
      const data = await api.get('/analytics/gis-layers');

      this.layers.track.clearLayers();
      this.layers.planned.clearLayers();
      this.layers.incidents.clearLayers();

      // 1. Planned Route corridor
      if (data.planned_waypoints && data.planned_waypoints.length > 0) {
        const plannedLatLngs = data.planned_waypoints.map(wp => [wp.latitude, wp.longitude]);
        const plannedLine = L.polyline(plannedLatLngs, {
          color: '#f59e0b',
          weight: 2,
          dashArray: '6, 8',
          opacity: 0.8,
        }).addTo(this.layers.planned);

        data.planned_waypoints.forEach((wp, idx) => {
          const wpMarker = L.circleMarker([wp.latitude, wp.longitude], {
            radius: 4,
            fillColor: '#f59e0b',
            color: '#fff',
            weight: 1,
            fillOpacity: 1,
          }).bindPopup(`<b>${wp.name || 'Waypoint ' + (idx + 1)}</b><br/>Alt: ${wp.altitude_m}m AGL`);
          this.layers.planned.addLayer(wpMarker);
        });
      }

      // 2. Actual Flown GPS Track
      if (data.flight_track && data.flight_track.length > 0) {
        const trackLatLngs = data.flight_track.map(pt => [pt[1], pt[0]]); // [lat, lng]
        const trackPolyline = L.polyline(trackLatLngs, {
          color: '#00f0ff',
          weight: 3.5,
          opacity: 0.9,
          lineJoin: 'round',
        }).addTo(this.layers.track);

        // Center map on actual track bounds
        this.map.fitBounds(trackPolyline.getBounds(), { padding: [40, 40] });

        // Update floating telemetry HUD with latest point
        const latestPt = data.flight_track[data.flight_track.length - 1];
        this.updateTelemetryHUD(latestPt[1], latestPt[0], latestPt[2] || 120, 8.5, 94.0);
      }

      // 3. Incidents with Evidence Thumbnails
      if (data.incidents && data.incidents.length > 0) {
        data.incidents.forEach(inc => {
          const isCritical = inc.severity === 'Critical' || inc.severity === 'High';
          const iconHtml = `
            <div class="custom-incident-pin">
              ${isCritical ? '<div class="pin-pulse-beacon"></div>' : ''}
              <div class="${isCritical ? 'pin-core-critical' : 'pin-core-verified'}"></div>
            </div>
          `;

          const customIcon = L.divIcon({
            html: iconHtml,
            className: 'div-marker',
            iconSize: [24, 24],
            iconAnchor: [12, 12],
          });

          let mediaHtml = '';
          if (inc.media && inc.media.length > 0) {
            const m = inc.media[0];
            mediaHtml = `
              <img src="${m.thumbnail_path}" class="popup-media-thumb" alt="Evidence" onerror="this.style.display='none'"/>
              <div style="font-size:10px; color:#00f0ff; font-family:var(--font-mono); margin-top:2px;">
                Sensor: ${m.sensor_type}
              </div>
            `;
          }

          const popupContent = `
            <div class="incident-popup-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="badge-status ${isCritical ? 'badge-threat' : 'badge-verified'}">${inc.severity}</span>
                <span style="font-family:var(--font-mono); font-size:10px; color:#94a3b8;">${inc.observed_at ? inc.observed_at.slice(11, 19) : ''} UTC</span>
              </div>
              <div style="font-weight:600; font-size:13px; color:#fff;">${inc.category}</div>
              <div style="font-size:11.5px; color:#cbd5e1;">${inc.description}</div>
              ${mediaHtml}
              <div style="font-family:var(--font-mono); font-size:10.5px; color:#64748b; margin-top:4px;">
                GPS: ${inc.latitude.toFixed(4)} N, ${inc.longitude.toFixed(4)} E
              </div>
            </div>
          `;

          const marker = L.marker([inc.latitude, inc.longitude], { icon: customIcon })
            .bindPopup(popupContent);
          this.layers.incidents.addLayer(marker);
        });
      }
    } catch (e) {
      console.error('Error loading GIS layers:', e);
    }
  },

  updateTelemetryHUD(lat, lon, alt, speed, batt) {
    const latEl = document.getElementById('tel-hud-lat');
    const lonEl = document.getElementById('tel-hud-lon');
    const altEl = document.getElementById('tel-hud-alt');
    const spdEl = document.getElementById('tel-hud-spd');
    const batEl = document.getElementById('tel-hud-bat');

    if (latEl) latEl.textContent = `${lat.toFixed(5)}° N`;
    if (lonEl) lonEl.textContent = `${lon.toFixed(5)}° E`;
    if (altEl) altEl.textContent = `${alt.toFixed(1)} m AGL`;
    if (spdEl) spdEl.textContent = `${speed.toFixed(1)} m/s`;
    if (batEl) batEl.textContent = `${batt.toFixed(1)}%`;
  },

  invalidateSize() {
    if (this.map) {
      setTimeout(() => {
        this.map.invalidateSize();
        this.loadLayers();
      }, 200);
    }
  },
};
