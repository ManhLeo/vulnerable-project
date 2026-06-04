JWT Payload
{
  "sub": "user_id",
  "role": "user",
  "exp": 9999999999
}
Security Requirements
HS256 signing
Secret key from environment variable
Expiration time required
HTTPS only in production
Token Lifetime
Token	Duration
Access Token	24 hours
Refresh Token	7 days
Password Policy

Minimum:

8 characters
1 uppercase
1 lowercase
1 number