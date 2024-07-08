import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import 'modern-normalize/modern-normalize.css';
import '@cds/core/global.css'; // pre-minified version breaks
import '@cds/city/css/bundles/default.min.css';
import './index.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals

//reportWebVitals();
