##Creating S3 bucket
resource "aws_s3_bucket" "bucket" {
  bucket = "drorassignment"
  acl    = "private"
}

##Uploading a timestamp.json to S3
resource "aws_s3_bucket_object" "object" {
  bucket = aws_s3_bucket.bucket.bucket
  key    = "timestamp.json"
  source = "timestamp.json"

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  etag = filemd5("timestamp.json")
}
