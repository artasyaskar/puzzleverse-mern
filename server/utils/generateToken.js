const crypto = require('crypto');

// Generate hashed token
const generateToken = () => {
  // Generate token
  const resetToken = crypto.randomBytes(20).toString('hex');

  // Hash token and set to resetPasswordToken field
  const resetPasswordToken = crypto
    .createHash('sha256')
    .update(resetToken)
    .digest('hex');

  // Set expire time (30 minutes from now)
  const resetPasswordExpire = Date.now() + 30 * 60 * 1000; // 30 minutes

  return { resetToken, resetPasswordToken, resetPasswordExpire };
};

module.exports = generateToken;
