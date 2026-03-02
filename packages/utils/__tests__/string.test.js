const { capitalize, reverse, isPalindrome, truncate } = require('../src/string');

describe('string utilities', () => {
  describe('capitalize()', () => {
    it('capitalizes the first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
    });

    it('returns an empty string unchanged', () => {
      expect(capitalize('')).toBe('');
    });

    it('leaves an already-capitalized string unchanged', () => {
      expect(capitalize('World')).toBe('World');
    });

    it('throws TypeError for non-string input', () => {
      expect(() => capitalize(123)).toThrow(TypeError);
    });
  });

  describe('reverse()', () => {
    it('reverses a string', () => {
      expect(reverse('hello')).toBe('olleh');
    });

    it('returns an empty string unchanged', () => {
      expect(reverse('')).toBe('');
    });

    it('throws TypeError for non-string input', () => {
      expect(() => reverse(null)).toThrow(TypeError);
    });
  });

  describe('isPalindrome()', () => {
    it('returns true for a simple palindrome', () => {
      expect(isPalindrome('racecar')).toBe(true);
    });

    it('returns true for a palindrome sentence ignoring punctuation and case', () => {
      expect(isPalindrome('A man, a plan, a canal: Panama')).toBe(true);
    });

    it('returns false for a non-palindrome', () => {
      expect(isPalindrome('hello')).toBe(false);
    });

    it('returns true for a single character', () => {
      expect(isPalindrome('a')).toBe(true);
    });

    it('throws TypeError for non-string input', () => {
      expect(() => isPalindrome(42)).toThrow(TypeError);
    });
  });

  describe('truncate()', () => {
    it('truncates a long string and appends ellipsis', () => {
      expect(truncate('Hello, world!', 5)).toBe('Hello...');
    });

    it('returns the string unchanged when within the limit', () => {
      expect(truncate('Hi', 10)).toBe('Hi');
    });

    it('returns the string unchanged when equal to the limit', () => {
      expect(truncate('Hello', 5)).toBe('Hello');
    });

    it('handles maxLength of 0', () => {
      expect(truncate('Hello', 0)).toBe('...');
    });

    it('throws TypeError for non-string first argument', () => {
      expect(() => truncate(123, 5)).toThrow(TypeError);
    });

    it('throws TypeError for invalid maxLength', () => {
      expect(() => truncate('hi', -1)).toThrow(TypeError);
      expect(() => truncate('hi', 'five')).toThrow(TypeError);
    });
  });
});
