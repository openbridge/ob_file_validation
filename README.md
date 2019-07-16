# CSV Lint: File Validation and Schema Generation
The purpose of this API is to validate CSV files for compliance with established norms such as [RFC4180](https://tools.ietf.org/html/rfc4180). Think of it like an easy to use CSV linter.

# Why validate CSV files?
Comma-separated values (CSV) is commonly used for exchanging data between systems. While this format is common, it can present difficulties. Why? Different tools, or export processes, often generate outputs that are not CSV files or have variations that are not considered "valid" according to the RFC4180.

Invalid CSV files create challenges for those building data pipelines. Pipelines value consistency, predictability, and testability as they ensure uninterrupted operation from source to a target destination.

Imagine pouring a gallon of maple syrup into the gas tank of your car. That is what bad CSV files do to data pipelines. If an error can get trapped earlier in the process, it improves operations for all systems.

This API will assist users with determining the quality of CSV data prior to delivery to upstream data pipelines. It will also generate a schema for the tested file, which can further aid in validation workflows.

## What does a valid CSV look like?
Here is an example of a valid CSV file.

It has a header row with `foo`, `bar`, and `buzz` with a corresponding row of `aaa`, `bbb`, and `ccc`

|  foo | bar  |  buzz |
|---|---|---|
| aaa  |  bbb |  ccc |  

The CSV will look something like this;
```bash
foo,bar,buzz
aaa,bbb,ccc
```
However, what if one day something changed. The file now looks like this:

|  foo | bar  |  buzz | |
|---|---|---|---|
| aaa  |  zzzz | bbb |  ccc |  

```bash
foo,bar,buzz
aaa,zzz,bbb,ccc
```

So what is wrong with this? RFC 4180 says that;

*Within the header and each record, there may be one or more fields, separated by commas. Each line should contain the same number of fields throughout the file. Spaces are considered part of a field and should not be ignored. The last field in the record must not be followed by a comma.*  

Notice the additional `zzz` is now between `aaa` and `bbb`. This file would marked as invalid because this of this misalignment. Is `zzz` correct? What about `ccc`? Maybe there is a missing header value for `ccc`? Regardless, the file has some issues.

For other examples, please [take a look at the RFC document](https://tools.ietf.org/html/rfc4180) for guidance on proper formats used for files using Comma-Separated Values (CSV).

# Getting Started: API Usage
There are two steps to the validation process. The first step is to post the file(s) to the API. If the file was accepted, the API will return a polling endpoint that contains the results of the validation process.

In our example, we will assume you have a CSV file called `your.csv` that you want to test.

### Prerequisites
The API has a 10 MB limit per file posted. See our client code samples how on how to manage for this limit (hint: split large files). Also, a **header row is required** in your CSV for validation to work correctly.

## Step 1: Post `your.csv` to validation API
We will run a simple `curl` command that will send the data to the API. It will look like this:
```bash
curl -F 'file=@/path/to/your.csv' 'https://validation.openbridge.io/dryrun' -H 'Content-Type: multipart/form-data' -D -
```
For the sake of this example, we will assume that the file posted successfully. You will see a `HTTP/2 302` response like this:
```bash
HTTP/2 302
content-type: application/json
content-length: 2
location: https://validation.openbridge.io/dryrun/poll_async/99ax58f2020423v28c6e644cd143cdac
date: Fri, 15 Feb 2019 22:36:57 GMT
x-amzn-requestid: 33316acc-3172-11e9-b824-ddbb1dd27279
x-amz-apigw-id: VKbJWGPtIAMF5Wg=
x-amzn-trace-id: Root=1-5c673f07-252f6e91546d64f019526eb6;Sampled=0
x-cache: Miss from cloudfront
via: 1.1 ab6d050b627b51ed631842034b2e298b.cloudfront.net (CloudFront)
x-amz-cf-id: XLW--LDgeqe7xpLvuoKxaGvKfvNcB4BNkyvx62P99N3qfgeuAvT7EA==
```

## Step 2: Get Your Results
Note the `location` URL endpoint:
```bash
https://validation.openbridge.io/dryrun/poll_async/99ax58f2020423v28c6e644cd143cdac
```

This is the your polling endpoint. You use this to obtain the results from the validation process. You can use `curl` again:
```bash
curl -s -w "%{http_code}" "https://validation.openbridge.io/dryrun/poll_async/99ax58f2020423v28c6e644cd143cdac"
```
If the file was properly formatted, with no errors, you will get a `HTTP/2 200` response from your polling endpoint. This indicates success! As a bonus, it will also provide an inferred schema. In our `your.csv` file the schema looks like this:

```json
{"data": {"rules": {"configuration": {"load": {"prepend_headers": false, "schema": {"fields": [{"default": null, "include_in_checksum": true, "name": "ob_mws_seller_id", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "ob_mws_marketplace_id", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "item_name", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "item_description", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "listing_id", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "seller_sku", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "price", "type": "DOUBLE PRECISION"}, {"default": null, "include_in_checksum": true, "name": "quantity", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "open_date", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "image_url", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "item_is_marketplace", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "product_id_type", "type": "BIGINT"}, {"default": null, "include_in_checksum": true, "name": "zshop_shipping_fee", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "item_note", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "item_condition", "type": "BIGINT"}, {"default": null, "include_in_checksum": true, "name": "zshop_category1", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "zshop_browse_path", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "zshop_storefront_feature", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "asin1", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "asin2", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "asin3", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "will_ship_internationally", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "expedited_shipping", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "zshop_boldface", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "product_id", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "bid_for_featured_placement", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "add_delete", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "pending_quantity", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "fulfillment_channel", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": true, "name": "merchant_shipping_group", "type": "VARCHAR (1024)"}, {"default": null, "include_in_checksum": false, "name": "ob_transaction_id", "type": "varchar(256)"}, {"default": null, "include_in_checksum": false, "name": "ob_file_name", "type": "varchar(2048)"}, {"default": null, "include_in_checksum": false, "name": "ob_processed_at", "type": "varchar(256)"}, {"default": "getdate()", "include_in_checksum": false, "name": "ob_modified_date", "type": "datetime"}]}}}, "destination": {"tablename": "sample"}, "dialect": {"__doc__": null, "__module__": "csv", "_name": "sniffed", "delimiter": ",", "doublequote": true, "encoding": "UTF-8", "lineterminator": "\r\n", "quotechar": "\"", "quoting": 0, "skipinitialspace": false}, "meta": {"creation_date": null, "version": null}}}}
```
**Congratulations**, the file passed validation and generated a schema for you!

## Client Code: `Bash` and `Python`
We have provided a couple of client scripts for you to use as-is or modify as need.

The first is a `BASH` client. It will take a CSV as an argument, then split the file into chunks for processing. Each chunk is sent to the API for testing. This makes the process more atomic, rather than one large file it can test smaller chunks. If there is an error, it will fail on a chunk, allowing you to more easily isolate a problem.

```bash
bash -c './validation_client.sh path/to/your.csv'
```
The `PYTHON` client works the same way, pass it file via `-f` and it will split and send chunks, just like the `BASH` client.

```bash
python ./validation_client.py -f path/to/your.csv
```


# Troubleshooting Problem Files: Common Use Cases

## Use Case 1: Unquoted commas
If your file is comma delimited, confirm that there are no extra unquoted commas in your data. Unquoted commas in your data will be treated as a field delimiter and the result will be that your data is ‘shifted’ and an extra column(s) created.

In the example below, there is an unquoted comma (Openbridge, Inc.) in the second row of the file named `company_sales_20190207.csv` that is being loaded to a warehouse table named company_sales that has been defined with 3 fields: `comp_name (string)`, `comp_no (integer)` and `sales_amt (decimal)`

File: `company_sales_20190207.csv`

```bash
comp_name,comp_no,sales_amt
Acme Corp.,100,500.00
Openbridge,Inc., 101, 100.00
```

|  comp_name | comp_no  |  sales_amt |
|---|---|---|
| Acme Corp.  |  100 |  500.00 |  
| Openbridge,Inc.  | 101 |  100.00|


A typical error for this use case would be `Error: could not convert string to integer”`


As you can see, the unquoted comma in the `‘Openbridge, Inc.’` value is treated as a delimiter and text after the comma is ‘shifted’ into the next column (comp_no).  In this example, the file will fail because there will be a field type mismatch between the value ‘Inc.’ (string) and the table field type (integer).

### Resolution
The first step to resolving this failure is to determine which field value(s) have the unquoted comma.  Excel can help with this as is will place the field values in spreadsheet columns based on the comma delimiter.  Once opened in Excel, you can filter one of the columns to identify values that do not belong (e.g. if you see a value of ‘openbridge’ in a field named sales_amt that should have values with a decimal field type.

Once identified, there are a couple options for ‘fixing’ this data:

 1. Surround the field value in double quotes (e.g. `“Openbridge, Inc.”`). This will tell the system that the comma is part of the field value and not a delimiter.  As long as the field in question is defined properly (in this case as a string) the data for that row will be successfully loaded.
 2. You can also remove the comma in the field value (e.g. change the value `‘Openbridge,Inc.’` to `‘Openbridge Inc.`). While viable, the correct approach is to use the double quotes in (1).

Once this issue is resolved in your file, re-post the file to the API for testing.

## Use Case 2: Quotation Marks
As described in the previous use case, quotation marks can be used to surround values with commas to prevent them from being treated as delimiters.  However, the use of only one quotation mark can be problematic because the system will consider everything after that quotation mark until the end of the row as part of the field and the file will fail to load.


### Example
In the example below, there is a single quotation mark in the second row of the file named `company_sales_20190208.csv` that is being loaded to a warehouse table named `company_sales`.

File: `company_sales_20190208.csv`
Table: `company_sales`

```bash
comp_name,comp_no,sales_amt
Acme Corp.,100,500.00
Openbridge,Inc.,“101,100.00
```

|  comp_name (string) | comp_no (integer)  |  sales_amt (decimal) |
|---|---|---|
| Acme Corp.  |  100 |  500.00 |  
| Openbridge,Inc.  | 101,100.00| |


As you can see, the single quotation mark `“101` caused the system to treat the rest of the record as the value for the comp_no field and the record will once again fail to load because the data types do not align.

### Resolution:

There are a couple options to resolve this issue depending on whether the quotation marks were intended to surround a value or included in error…
 1. If quotation marks were intended, add the closing quotation mark at the end of the respective value
 2. If the single quotation mark was added in error, delete it

Once this issue is resolved in your file, re-post the file to the API.


## Use Case 3: Leading or trailing spaces in field values

Sometimes source systems have leading or trailing spaces in data fields. According to RFC410, ` Spaces are considered part of a field and should not be ignored.`  As a result, **we will not treat spaces as a failure** in our validation tests as it conforms to specifications.

However, there are potential issues with data containing leading or trailing spaces. Specifically, problems can arise if there are empty or null values included in a file.  If those null values include spaces, a system may treat those values as strings which may not be compatible with the field type defined in your destination table (i.e. integer).

Another potential issue is that spaces can cause issues with joins between tables in your warehouse.  If trimming spaces from your source data is not possible, you can typically remove those spaces by creating views in your warehouse using `TRIM` functions.

In many cases you will want to remove (trim) these spaces prior to posting.  

### Example
In the example below, there is an empty value that includes spaces for the field `sales_amt` in the second row of the file named `company_sales_20190209.csv` that is being loaded to a warehouse table named `company_sales`. That record will fail because the string field type associated with the spaces does not match the decimal field type for the table definition.

File: `company_sales_20190209.csv`
Table: `company_sales`
```bash
comp_name,comp_no,sales_amt
Acme Corp.,100,500.00
Openbridge Inc., 101,   ,
```

|  comp_name (string) | comp_no (integer)  |  sales_amt (decimal) |
|---|---|---|
| Acme Corp.  |  100 |  500.00 |  
| Openbridge Inc.  | 101 |‘   ‘ |

### Resolution:
There are a couple options to resolve this issue depending on whether the null value included in the file is a valid value or not.

1. If the value is valid, remove the spaces in the field value to indicate a true Null value. A field with spaces is not Null.
2. Replace the value with a valid field value that matches the field data type in the table (in our example a decimal)

## Use Case 4: Mismatch data types

It is possible that your data types will change over time. This means your old and new schemas do not have compatible field types defined in your destination table.


### Example
Lets say you attempt to process a file where all values for a column called `sales_amt` were an INT data type, yet historical data for `sales_amt` were a decimal data type. This will cause donwstream processing failures. A system will have a schema setting `sales_amt` as an INT and you are trying to process and load older data with a decimal data type. 

In the example below, there is a value that includes the field `sales_amt` of a file named `company_product_today.csv` that is being loaded to a warehouse table named `company_sales`. Here is an example of a file that is current that is sent every day: 
* File: `company_product_today.csv`
* Table: `company_product`

Notice the `sales_amt` is an INT:

```bash
comp_name,comp_no,sales_amt
Acme Corp.,100,500
Openbridge Inc.,101,300
```
|  comp_name (string) | comp_no (integer)  |  sales_amt (integer) |
|---|---|---|
| Acme Corp.  | 100 |  500 |  
| Openbridge Inc.  | 101 | 300 |


Now, lets say you have historical data from a few years ago you also want to load into the same destination. However, the `sales_amt` was not an INT back then, it was a decimal:

File: `company_product_history.csv`
Table: `company_product`
```bash
comp_name,comp_no,sales_amt
Acme Corp.,100,500.00
Openbridge Inc.,101,300.00
Wiley,103,1200.00
```
|  comp_name (string) | comp_no (integer)  |  sales_amt (decimal) |
|---|---|---|
| Acme Corp.  |  100 |  500.00 |  
| Openbridge Inc.  | 101 | 300.00 |
| Wiley | 103 | 1200.00 |

When you attempt to load `company_product_history.csv` it will fail as a result of this data type mismatch. That `sales_amt` will fail because the string field type associated with the spaces does not match the decimal field type for the table `company_product` definition.


### Resolution:
There are a couple options to resolve this issue:

1. Rather than send historical data to the same table, send it to an alternate table and then use a view to fuse them together. 
2. Use the API to check all of your current and hisotrical data. This will allows you to model the data so you can determine a common data type that would work across all variations. 


# Status Codes

## Validation Request Endpoint

* Status Code: `HTTP/2 302; Success - Processing has begun`
* Status Code:  `HTTP/2 404; Failure, no sample file was provided`
* Status Code: `HTTP/2 400; Failure, the rules API was unable to initialize the request for some reason`

## Results Polling Endpoint

* Status Code: `HTTP/2 302; Pending - still processing`
* Status Code: `HTTP/2 200; Success - processing completed, file validated successfully`
* Status Code: `HTTP/2 502; Failure - file determined to be invalid by rules API`
* Status Code: `HTTP/2 404; Failure - invalid request ID in polling URL (expired, etc.)`


# TODO


# Issues

If you have any problems with or questions about this image, please contact us through a GitHub issue.

# Contributing

You are invited to contribute new features, fixes, or updates, large or small; we are always thrilled to receive pull requests, and do our best to process them as fast as we can.

Before you start to code, we recommend discussing your plans through a GitHub issue, especially for more ambitious contributions. This gives other contributors a chance to point you in the right direction, give you feedback on your design, and help you find out if someone else is working on the same thing.
