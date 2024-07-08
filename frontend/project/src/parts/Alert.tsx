import { Component } from 'react';

import { CdsIcon } from '@cds/react/icon';

class Alert extends Component {
  render() {
    return (
      <div className="alert alert-app-level alert-info">
        <div className="alert-items">
          <div className="alert-item static">
            <div className="alert-icon-wrapper">
              <CdsIcon className="alert-icon" shape="info-circle"></CdsIcon>
            </div>
            <div className="alert-text">
              App Level Alert
            </div>
            <div className="alert-actions">
              <button className="btn btn-sm alert-action">Action</button>
            </div>
          </div>
        </div>
        <button type="button" className="close" aria-label="Close">
          <CdsIcon aria-hidden="true" shape="close"></CdsIcon>
        </button>
      </div>
    );
  }
}

export default Alert;