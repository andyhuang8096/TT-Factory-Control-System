using Microsoft.AspNetCore.Cryptography.KeyDerivation;
using System;
using System.Security.Cryptography;

namespace TT_PPID_CS.Application.Utils
{
    public static class PasswordHasher
    {
        public static string HashPassword(string password, out byte[] salt)
        {
            salt = new byte[128 / 8];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(salt);
            }

            string hashed = Convert.ToBase64String(KeyDerivation.Pbkdf2(
                password: password,
                salt: salt,
                prf: KeyDerivationPrf.HMACSHA256,
                iterationCount: 100000,
                numBytesRequested: 256 / 8));

            // Store salt and hash together as in Python version if needed
            // For now, let's keep it simple or match the exact Python format if DB is existing
            // Python: hashed_password = base64.b64encode(salt + key).decode('utf-8')
            
            byte[] key = KeyDerivation.Pbkdf2(
                password: password,
                salt: salt,
                prf: KeyDerivationPrf.HMACSHA256,
                iterationCount: 100000,
                numBytesRequested: 256 / 8);
            
            byte[] combined = new byte[salt.Length + key.Length];
            Buffer.BlockCopy(salt, 0, combined, 0, salt.Length);
            Buffer.BlockCopy(key, 0, combined, salt.Length, key.Length);
            
            return Convert.ToBase64String(combined);
        }

        public static bool VerifyPassword(string password, string storedHash)
        {
            try
            {
                byte[] combined = Convert.FromBase64String(storedHash);
                byte[] salt = new byte[16];
                byte[] storedKey = new byte[32];
                
                Buffer.BlockCopy(combined, 0, salt, 0, 16);
                Buffer.BlockCopy(combined, 16, storedKey, 0, 32);

                byte[] inputKey = KeyDerivation.Pbkdf2(
                    password: password,
                    salt: salt,
                    prf: KeyDerivationPrf.HMACSHA256,
                    iterationCount: 100000,
                    numBytesRequested: 32);

                return CryptographicOperations.FixedTimeEquals(storedKey, inputKey);
            }
            catch
            {
                return false;
            }
        }
    }
}
