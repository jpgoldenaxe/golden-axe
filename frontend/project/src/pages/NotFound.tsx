import { Component } from 'react';

class NotFound extends Component {
  render() {
    return (
      <div className="content-container">
        <div className="content-area">
          <h1 cds-text="heading">404</h1>
          <br></br>
          <h3>URL not found</h3>
        </div>
      </div>
    );
  }
}

export default NotFound;