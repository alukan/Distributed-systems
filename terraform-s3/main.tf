provider "aws" {
  region = "eu-west-3"
}

resource "aws_s3_bucket" "static_site" {
  bucket = "nikolai.terraform"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "aws_s3_bucket_object" "index" {
  bucket = aws_s3_bucket.static_site.bucket
  key    = "index.html"
  source = "~/M12-DSystems/terraform-s3/index.html"
}

resource "aws_s3_bucket_object" "error" {
  bucket = aws_s3_bucket.static_site.bucket
  key    = "error.html"
  source = "~/M12-DSystems/terraform-s3/error.html"
}

resource "aws_s3_bucket_policy" "static_site_policy" {
  bucket = aws_s3_bucket.static_site.bucket

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Principal = "*",
        Action: "s3:GetObject",
        Resource: "arn:aws:s3:::${aws_s3_bucket.static_site.bucket}/*"
      }
    ]
  })
}

output "website_url" {
  value = aws_s3_bucket.static_site.website_endpoint
}
