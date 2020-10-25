# Hennepin County Jail Bookings

The repository contains scripts used to get  jail bookings in Hennepin County, Minnesota.
The scripts are deployed using AWS. Note that the lambda functions are separated both from
the front-end script and from each other. This allows us to run long queries without
having to worry about exceeding the 60-second timeout window for server applications in AWS.

## Front end

The front end uses Dash, and the relevant front-end files are in the `front-end` folder.
The user selects the desired date range, and this script in turn calls two lambda functions
(as explained below) to write and retrieve booking data.

## Lambda functions

Two lambda functions are used and are in the `lambda-functions` folder:


* `writeBookingsToCsv`: This is called by the front-end script and is used to write all bookings from the supplied date range to S3. Note that relevant packages are also included in this folder. This is necessary mostly because Pandas is needed by this script but is not available natively on AWS.

* `checkIfFileExists`: This is called by the front-end script and is used to check if the bookings have been successfully written to S3. If they have, they are retrieved for the user to download.

Note that the following environment variables need to be defined within each lambda function in AWS for the functions to run successfully:

* `aws_bucket_name`: The name of the AWS bucket that is used to temporarily store data output from the `writeBookingsToCsv` lambda function.
* `aws_region_name`: The name of the region where the AWS bucket resides (e.g., `us-east-1`).
* `aws_access_key_id`: The AWS access key id of the access point used to write to/read from the bucket in S3.
* `aws_secret_access_key`: The AWS secret access key of the access point used to write to/read from the bucket in S3.
