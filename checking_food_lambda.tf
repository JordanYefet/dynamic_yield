locals {
  lambda_zip_location_checking_food = "outputs/checking_food.zip"
}

data "archive_file" "checking_food" {
  type        = "zip"
  source_file = "checking_food.py"
  output_path = local.lambda_zip_location_checking_food
}

resource "aws_lambda_function" "checking_food" {
  filename         = local.lambda_zip_location_checking_food
  function_name    = "checking_food"
  role             = aws_iam_role.lambda_role.arn
  handler          = "checking_food.lambda_handler"
  source_code_hash = filebase64sha256(local.lambda_zip_location_checking_food) #need to turn on after a provision for code updates
  runtime          = "python3.6"
}

##Creating a S3bucket notification
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.checking_food.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = ".jpg"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

##Granting S3bucket permissions
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.checking_food.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
  depends_on    = [aws_s3_bucket.bucket]
}
