import React from 'react';
import ReactDOM from 'react-dom/client';
import { SolarHero } from './SolarHero.jsx';
import './hero.css';

ReactDOM.createRoot(document.getElementById('app')).render(
  <React.StrictMode>
    <SolarHero />
  </React.StrictMode>
);
