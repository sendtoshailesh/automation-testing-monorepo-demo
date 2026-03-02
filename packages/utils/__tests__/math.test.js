const { add, subtract, multiply, divide, factorial } = require('../src/math');

describe('math utilities', () => {
  describe('add()', () => {
    it('adds two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
    });

    it('adds a positive and a negative number', () => {
      expect(add(10, -4)).toBe(6);
    });

    it('adds two negative numbers', () => {
      expect(add(-1, -1)).toBe(-2);
    });

    it('adds zero to a number', () => {
      expect(add(5, 0)).toBe(5);
    });

    it('throws TypeError for non-number arguments', () => {
      expect(() => add('1', 2)).toThrow(TypeError);
      expect(() => add(1, null)).toThrow(TypeError);
    });
  });

  describe('subtract()', () => {
    it('subtracts two numbers', () => {
      expect(subtract(10, 4)).toBe(6);
    });

    it('returns negative when result is negative', () => {
      expect(subtract(2, 5)).toBe(-3);
    });

    it('throws TypeError for non-number arguments', () => {
      expect(() => subtract('a', 1)).toThrow(TypeError);
    });
  });

  describe('multiply()', () => {
    it('multiplies two positive numbers', () => {
      expect(multiply(3, 4)).toBe(12);
    });

    it('multiplies by zero', () => {
      expect(multiply(5, 0)).toBe(0);
    });

    it('multiplies two negative numbers', () => {
      expect(multiply(-2, -3)).toBe(6);
    });

    it('throws TypeError for non-number arguments', () => {
      expect(() => multiply(2, '3')).toThrow(TypeError);
    });
  });

  describe('divide()', () => {
    it('divides two numbers', () => {
      expect(divide(10, 2)).toBe(5);
    });

    it('returns a decimal result', () => {
      expect(divide(1, 4)).toBeCloseTo(0.25);
    });

    it('throws Error when dividing by zero', () => {
      expect(() => divide(5, 0)).toThrow('Division by zero is not allowed');
    });

    it('throws TypeError for non-number arguments', () => {
      expect(() => divide('10', 2)).toThrow(TypeError);
    });
  });

  describe('factorial()', () => {
    it('returns 1 for factorial of 0', () => {
      expect(factorial(0)).toBe(1);
    });

    it('returns 1 for factorial of 1', () => {
      expect(factorial(1)).toBe(1);
    });

    it('returns 120 for factorial of 5', () => {
      expect(factorial(5)).toBe(120);
    });

    it('throws Error for negative numbers', () => {
      expect(() => factorial(-1)).toThrow('Factorial is not defined for negative numbers');
    });

    it('throws TypeError for non-integer input', () => {
      expect(() => factorial(1.5)).toThrow(TypeError);
      expect(() => factorial('5')).toThrow(TypeError);
    });
  });
});
