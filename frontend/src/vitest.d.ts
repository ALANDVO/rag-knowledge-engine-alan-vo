import '@testing-library/jest-dom';
import { expect } from 'vitest';

declare module 'vitest' {
  interface Assertion<T = any> {
    toBeInTheDocument(): T;
    toHaveAttribute(name: string, value?: string): T;
    toBeDisabled(): T;
    // Add other jest-dom matchers as needed
  }
  interface AsymmetricMatchersContaining {
    toBeInTheDocument(): any;
    toHaveAttribute(name: string, value?: string): any;
    toBeDisabled(): any;
  }
}
