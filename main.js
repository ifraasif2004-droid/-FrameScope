import './style.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import VectorLayer from 'ol/layer/Vector.js';
import OSM from 'ol/source/OSM.js';
import VectorSource from 'ol/source/Vector.js';
import Feature from 'ol/Feature.js';
import Point from 'ol/geom/Point.js';
import { fromLonLat } from 'ol/proj.js';
import Overlay from 'ol/Overlay.js';
import { Icon, Style } from 'ol/style.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import { Fill, Stroke, Circle as CircleStyle, Text } from 'ol/style.js';
import { getVectorContext } from 'ol/render.js';
import { easeOut } from 'ol/easing.js';

function pulseFeature(feature, layerForAnimation) {
  const duration = 800;
  const start = Date.now();
  const geom = feature.getGeometry().clone();

  const onPostRender = (event) => {
    const frameState = event.frameState;
    const elapsed = frameState.time - start;
    const elapsedRatio = elapsed / duration;

    if (elapsed > duration) {
      layerForAnimation.un('postrender', onPostRender);
      return;
    }
    const radius = easeOut(elapsedRatio) * 25 + 5;
const opacity = easeOut(1 - elapsedRatio);

// Get category from feature
const category = feature.get('category');

// Decide pulse color based on category
const pulseColor =
  category === 'Type 1'
    ? `rgba(255, 0, 0, ${opacity})`
    : `rgba(0, 0, 255, ${opacity})`;

const pulseFillColor =
  category === 'Type 1'
    ? `rgba(255, 0, 0, ${opacity * 0.2})`
    : `rgba(0, 0, 255, ${opacity * 0.2})`;

const style = new Style({
  image: new CircleStyle({
    radius: radius,
    stroke: new Stroke({
      color: pulseColor,
      width: 3,
    }),
    fill: new Fill({
      color: pulseFillColor,
    }),
  }),
});
    const vectorContext = getVectorContext(event);
    vectorContext.setStyle(style);
    vectorContext.drawGeometry(geom);
    map.render();
  };

  layerForAnimation.on('postrender', onPostRender);
  map.render();
}

/* GeoJSON vector layer */
const geojsonLayer = new VectorLayer({
  source: new VectorSource({
    url: './data/points.geojson',
    format: new GeoJSON(),
  }),
  style: (feature) =>
    new Style({
      image: new CircleStyle({
        radius: map.getView().getZoom() > 13 ? 12 : 7,
        fill: new Fill({ color: '#1976d2' }),
        stroke: new Stroke({ color: '#ffffff', width: 2 }),
      }),
      text: new Text({
        text: feature.get('name') ?? '',
        offsetY: -16,
        fill: new Fill({ color: '#111' }),
        stroke: new Stroke({ color: '#fff', width: 3 }),
      }),
    }),
});



/* Basemap */
const baseLayer = new TileLayer({
  source: new OSM(),
});

/* Marker feature */
const markerFeature = new Feature({
  geometry: new Point(fromLonLat([73.0479, 33.6844])),
  name: 'Faisal Mosque',
  info: 'This is a marker with attributes.',
});

markerFeature.setStyle(
  new Style({
    image: new Icon({
      src: 'https://openlayers.org/en/latest/examples/data/icon.png',
      anchor: [0.5, 1],
    }),
  })
);

/* Marker layer */
const markerLayer = new VectorLayer({
  source: new VectorSource({
    features: [markerFeature],
  }),
});

/* Map */
const map = new Map({
  target: 'map',
  layers: [baseLayer, geojsonLayer, markerLayer],
  view: new View({
    center: fromLonLat([73.0479, 33.6844]),
    zoom: 11,
  }),
});
const btnReset = document.getElementById('btn-reset');

btnReset.addEventListener('click', () => {
  const view = map.getView();

  view.animate({
    center: fromLonLat([73.0479, 33.6844]),
    zoom: 11,
    duration: 1500,
  });
});

const btnFly = document.getElementById('btn-fly');

function flyTo(locationLonLat) {
  const view = map.getView();
  const zoom = view.getZoom();
  const center = fromLonLat(locationLonLat);

  view.animate(
    { center, duration: 2000 },
    { zoom: zoom + 3, duration: 1000 },
    { zoom, duration: 1000 }
  );
}

btnFly.addEventListener('click', () => {
  flyTo([73.0479, 33.6844]);
});

const btnFlyLahore = document.getElementById('btn-fly-lahore');

btnFlyLahore.addEventListener('click', () => {
  flyTo([74.3587, 31.5204]); // Lahore
});

const btnRotate = document.getElementById('btn-rotate');

btnRotate.addEventListener('click', () => {
  const view = map.getView();
  const rotation = view.getRotation();

  view.animate({
    rotation: rotation + Math.PI,
    duration: 2000,
  });
});

/* Popup */
const popupEl = document.getElementById('popup');
const popupContentEl = document.getElementById('popup-content');
const popupCloserEl = document.getElementById('popup-closer');

const popupOverlay = new Overlay({
  element: popupEl,
  autoPan: true,
  autoPanAnimation: { duration: 250 },
});

map.addOverlay(popupOverlay);

popupCloserEl.onclick = () => {
  popupEl.classList.remove('is-open');
  popupOverlay.setPosition(undefined);
  popupCloserEl.blur();
  return false;
};

/* CLICK INTERACTION */
map.on('singleclick', (evt) => {
  const feature = map.forEachFeatureAtPixel(evt.pixel, (f) => f);

  if (!feature) {
    popupEl.classList.remove('is-open');
    popupOverlay.setPosition(undefined);
    return;
  }

  pulseFeature(feature, geojsonLayer);

  const name = feature.get('name') ?? 'Unknown';
  const info = feature.get('info') ?? 'No info';
  const category = feature.get('category') ?? 'No category';

  popupContentEl.innerHTML = `
    <strong>${name}</strong>
    <p>${info}</p>
    <p><b>Category:</b> ${category}</p>
  `;

  popupEl.classList.add('is-open');
  popupOverlay.setPosition(evt.coordinate);
});

export default map;





