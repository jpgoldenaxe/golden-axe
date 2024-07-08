import { Component } from 'react';
import { NavLink } from "react-router-dom";

class Sidenav extends Component {
  render() {
    return (
      <nav className="sidenav">
        <section className="sidenav-content">
          <section className="nav-group">
            <input id="tabexample2" type="checkbox" />
            <label htmlFor="tabexample2">Target Appliance</label>
            <ul className="nav-list">
              <li><NavLink to="backup" className="nav-link active">
                vCenter</NavLink></li>
              <li><NavLink to="backup" className="nav-link">
                NSX-T</NavLink></li>
            </ul>
          </section>
        </section>
      </nav>
    );
  }
}

export default Sidenav;
