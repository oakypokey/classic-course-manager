import React, { useState } from "react";
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
import { prependOnceListener } from "cluster";

export const Navigation: React.FC = () => {
  const [loggedin, setLoggedin] = useState(false);
  const toggle = () => setLoggedin(!loggedin);
  return (
    <>
      <Navbar pills color="light" light expand="md">
        <NavbarBrand href="/">Classic Course Manager</NavbarBrand>
        <Nav className="mr-auto">
          <NavItem>
            <NavLink> About</NavLink>
          </NavItem>
          <NavItem>
            <NavLink> GitHub</NavLink>
          </NavItem>
          <NavItem>
            <NavLink> Help </NavLink>
          </NavItem>
        </Nav>
        {loggedin ? (
          <UserBadge
            url="https://picsum.photos/35"
            toggle={toggle}
          />
        ) : (
          <Button onClick={toggle} color="primary">
            {" "}
            Login{" "}
          </Button>
        )}
      </Navbar>
    </>
  );
};

interface UserBadgeProps {
  url: string;
  toggle: any;
}

const userStyle: React.CSSProperties = {
  borderRadius: "50%"
}

const UserBadge: React.FC<UserBadgeProps> = ({
  url,
  toggle,
}: UserBadgeProps) => {
  return (
    <>
      <UncontrolledDropdown inNavbar>
        <DropdownToggle color="light">
          <Media  style={userStyle} right object src={url} alt="Generic placeholder image" />
        </DropdownToggle>
        <DropdownMenu right>
          <DropdownItem onClick={toggle}>Logout</DropdownItem>
        </DropdownMenu>
      </UncontrolledDropdown>
    </>
  );
};
