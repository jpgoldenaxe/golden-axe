import { Component } from 'react';
import { Link, NavLink } from "react-router-dom";

import { CdsIcon } from '@cds/react/icon';

class Header extends Component {
  render() {
    return (
      <header className="header header-6">
        <div className="branding">
          <Link to="/" className="title">
            Golden Axe
          </Link>
        </div>
        <div className="header-nav">
          <NavLink
            to="backup"
            className={
              ({ isActive }) => isActive ? "active nav-link" : "nav-link"
            }
          >
            Backup
          </NavLink>
        </div>
        <div className="settings">
          <Link to="settings" className="nav-link nav-icon">
            <CdsIcon shape="user"></CdsIcon>
          </Link>
        </div>
      </header >
    );
  }
}

export default Header;
