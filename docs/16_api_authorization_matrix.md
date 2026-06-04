Public APIs
Endpoint	Method	Access
/api/v1/scan/code	POST	guest
/api/v1/scan/file	POST	guest
/api/v1/auth/login	POST	public
/api/v1/auth/register	POST	public
User APIs
Endpoint	Method	Access
/api/v1/history	GET	user
/api/v1/history/{id}	GET	user
/api/v1/report/export	POST	user
Admin APIs
Endpoint	Method	Access
/api/v1/admin/users	GET	admin
/api/v1/admin/scans	GET	admin
/api/v1/admin/stats	GET	admin
/api/v1/admin/model/reload	POST	admin
