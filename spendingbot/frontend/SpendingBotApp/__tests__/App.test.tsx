/**
 * @format
 */

import React from 'react';
import { render } from '@testing-library/react-native';
import App from '../App';

jest.mock('react-native-plaid-link-sdk', () => ({
  PlaidLink: () => null,
}));

test('renders SpendingBot header', () => {
  const { getByText } = render(<App />);
  expect(getByText('SpendingBot')).toBeTruthy();
});
