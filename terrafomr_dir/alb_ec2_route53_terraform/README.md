■Set-Up
1. Create S3 for tfstate
ex)example-dev-alb-accesslog-bucket

■Resources
<br />
EC2(web, db) x 2
ALb x 1(HTTP Listener only)

■Deploy
1. Move dev directory
2. terraform init
3. terraform plan
4. terraform apply