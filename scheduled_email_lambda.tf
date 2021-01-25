locals {
  lambda_zip_location_scheduled_email = "outputs/scheduled_email.zip"
}

data "archive_file" "scheduled_email" {
  type        = "zip"
  source_file = "scheduled_email.py"
  output_path = local.lambda_zip_location_scheduled_email
}

resource "aws_lambda_function" "scheduled_email" {
  filename         = local.lambda_zip_location_scheduled_email
  function_name    = "scheduled_email"
  role             = aws_iam_role.lambda_role.arn
  handler          = "scheduled_email.lambda_handler"
  source_code_hash = filebase64sha256(local.lambda_zip_location_scheduled_email)
  runtime          = "python3.6"

  /* Doesn't seem to work :( */
  /*   environment {
    variables = {
      S3Bucket  = "${aws_s3_bucket.bucket.bucket}"
      sender    = "Jordan.Yefet90@gmail.com"
      recipient = "Jordan.Yefet90@gmail.com"
    }
  } */
}


##Creating an EventBridge trigger for every 1 minute
resource "aws_cloudwatch_event_rule" "scheduled_email" {
  name                = "scheduled_email"
  description         = "Notify about the hunger of my cat."
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "scheduled_email" {
  rule      = aws_cloudwatch_event_rule.scheduled_email.name
  target_id = "EmailNotifier"
  arn       = aws_lambda_function.scheduled_email.arn
}
##Granting EventBridge permissions
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduled_email.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_email.arn
}
