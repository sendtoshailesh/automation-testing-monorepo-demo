/**
 * String utility functions
 */

/**
 * Capitalizes the first letter of a string.
 * @param {string} str
 * @returns {string}
 */
function capitalize(str) {
  if (typeof str !== 'string') {
    throw new TypeError('Argument must be a string');
  }
  if (str.length === 0) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Reverses a string.
 * @param {string} str
 * @returns {string}
 */
function reverse(str) {
  if (typeof str !== 'string') {
    throw new TypeError('Argument must be a string');
  }
  return str.split('').reverse().join('');
}

/**
 * Checks if a string is a palindrome.
 * @param {string} str
 * @returns {boolean}
 */
function isPalindrome(str) {
  if (typeof str !== 'string') {
    throw new TypeError('Argument must be a string');
  }
  const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleaned === cleaned.split('').reverse().join('');
}

/**
 * Truncates a string to the given length, appending '...' if truncated.
 * @param {string} str
 * @param {number} maxLength
 * @returns {string}
 */
function truncate(str, maxLength) {
  if (typeof str !== 'string') {
    throw new TypeError('First argument must be a string');
  }
  if (typeof maxLength !== 'number' || maxLength < 0) {
    throw new TypeError('maxLength must be a non-negative number');
  }
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + '...';
}

module.exports = { capitalize, reverse, isPalindrome, truncate };
