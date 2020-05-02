import React, { useState, CSSProperties } from "react";
import {
  Navbar,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  Button,
  Media,
  NavbarText,
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
} from "reactstrap";
import { SessionUserData } from "../App";

interface NavigationProps {
  userData: SessionUserData;
  onClickHelp: () => void;
  onClickAbout: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  userData,
  onClickHelp,
  onClickAbout,
}: NavigationProps) => {
  const linkStyle: CSSProperties = {
    color: "black",
    cursor: "pointer",
  };

  return (
    <>
      <Navbar color="light" light expand="md">
        <NavbarBrand href="/">Classic Course Manager</NavbarBrand>
        <Nav className="mr-auto">
          <NavItem>
            <NavLink style={linkStyle} onClick={onClickAbout}>
              {" "}
              About
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              style={linkStyle}
              href="https://github.com/oakypokey/class2calendar"
            >
              GitHub
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink style={linkStyle} onClick={onClickHelp}>
              {" "}
              Help{" "}
            </NavLink>
          </NavItem>
        </Nav>
        <UserBadge userData={userData} />
      </Navbar>
    </>
  );
};

interface UserBadgeProps {
  userData: SessionUserData;
}

const userStyle: React.CSSProperties = {
  borderRadius: "50%",
  maxWidth: "45px",
  float: "left",
  display: "inline-box",
};

const userBadgeStyle: React.CSSProperties = {
  float: "right",
  marginTop: "10px",
  marginLeft: "5px",
};

const UserBadge: React.FC<UserBadgeProps> = ({ userData }: UserBadgeProps) => {
  return (
    <>
      <UncontrolledDropdown inNavbar>
        <DropdownToggle color="light">
          <Media
            style={userStyle}
            right
            object
            src={userData.picture}
            alt="User Image"
          />
          <p style={userBadgeStyle}>
            <b>{userData.given_name}</b>
          </p>
        </DropdownToggle>
        <DropdownMenu right>
          <DropdownItem href="/logout"> Logout </DropdownItem>
        </DropdownMenu>
      </UncontrolledDropdown>
    </>
  );
};
