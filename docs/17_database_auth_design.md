users Collection
{
  "_id": "uuid",
  "email": "leo@example.com",
  "password_hash": "bcrypt_hash",
  "role": "user",
  "is_active": true,
  "created_at": "2026-05-29T12:00:00Z"
}
scans Collection
{
  "scan_id": "uuid",
  "user_id": "uuid",
  "source_type": "file",
  "language": "c",
  "prediction": {
    "is_vulnerable": true,
    "confidence": 0.94
  },
  "created_at": "2026-05-29T12:00:00Z"
}
Recommended Indexes

users:

email
role

scans:

user_id
created_at
prediction.is_vulnerable
