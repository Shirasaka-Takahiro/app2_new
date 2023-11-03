##Bucket for ALB log
resource "aws_s3_bucket" "bucket_alb_access_log" {
  bucket = "${var.general_config["project"]}-${var.general_config["env"]}-alb-accesslog-bucket"

  tags = {
    Name = "${var.general_config["project"]}-${var.general_config["env"]}-alb-accessloh-bucket"
  }
}

##Public Access Block
resource "aws_s3_bucket_public_access_block" "bucket_public_access" {
  bucket                  = aws_s3_bucket.bucket_alb_access_log.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

##Versioning
resource "aws_s3_bucket_versioning" "bucket_versiong" {
  bucket = aws_s3_bucket.bucket_alb_access_log.id
  versioning_configuration {
    status = "Disabled"
  }
}

##Server Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_server_side_encryption" {
  bucket = aws_s3_bucket.bucket_alb_access_log.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

##Bucket ACL
resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket_alb_access_log.id
  acl    = "private"
}

##Bucket Policy
data "aws_elb_service_account" "main" {}

data "aws_iam_policy_document" "iam_policy_alb_access_log" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.bucket_alb_access_log.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = [data.aws_elb_service_account.main.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "bucket_policy_alb_access_log" {
  bucket = aws_s3_bucket.bucket_alb_access_log.id
  policy = data.aws_iam_policy_document.iam_policy_alb_access_log.json
}