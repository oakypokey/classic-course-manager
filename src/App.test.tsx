import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import App from './App';

test('renders title', () => {
  const { getByText } = render(<App />);
  const linkElement = getByText(/Classic Course Manager/i);
  expect(linkElement).toBeInTheDocument();
});