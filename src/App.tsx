import React from 'react';
import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import {Navigation} from './components/Navigation'

import { Container, Row, Col, Button, Navbar, NavbarBrand, NavbarText, NavbarToggler, Nav,  } from 'reactstrap'

function App() {
  return (
    <div className="App">
      <Navigation/>
      <Container>
        <Row>
          <Col></Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
