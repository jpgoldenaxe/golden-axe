import { Component } from 'react';

class Subnav extends Component {
  render() {
    return (
      <nav className="subnav">
        <ul className="nav">
          <li className="nav-item">
            <a className="nav-link active" href="#">Subnav Link 1</a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">Subnav Link 2</a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">Subnav Link 3</a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">Subnav Link 4</a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">Subnav Link 5</a>
          </li>
        </ul>
      </nav>
    );
  }
}

export default Subnav;