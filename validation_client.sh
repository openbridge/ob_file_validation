#!/usr/bin/env bash

# Set and test variables
args=("$@")
[[ -z ${args[0]} ]] && echo "ERROR: Was expecting the path and file to be passed" && exit 1
file="${args[0]}"
size=$(wc -c < "${file}")
base=$(echo ${file##*/})
name=$(echo ${base%.*})
runtime=$(date +%Y%m%d_%H%M%S)
workdir=${name}_${runtime}

# Check for curl, we require it for this script
if [[ ! -x "$(command -v curl)" ]]; then echo "Error: curl is not installed and is required for this script to function properly" >&2; exit 1; fi

# Setup the workspace
mkdir -p ./"${workdir}" && cp "$file" "$workdir" && cd "$workdir" || exit

if [[ ! -f ${file} ]]; then echo "ERROR: You supplied ${file} but the file can not be located by this script. Please check the path or filename." && exit 1; else echo "OK: The file being sent for validation is located here: ${file}"; fi

# Split the files so we can post in blocks.
if (( size > 999 )); then
  awk -v l=2000 '(NR==1){header=$0;next}
                 (NR%l==2) {
                    c=sprintf("%0.5d",c+1);
                    close(file); file=FILENAME; sub(/csv$/,c".csv",file)
                    print header > file
                 }
                 {print $0 > file}' "$file"
  # Remove orignal file prior to testing as we don't want this sent
  rm -f "$file"
 else
   echo "OK: The file being sent for validation does not exceed 10 MB"
fi

for i in ./*.csv; do
    # Submit file for validation
    location=$(curl -s -w "%{http_code}" -F file=@"$i" 'https://validation.openbridge.io/dryrun' -H 'Content-Type: multipart/form-data' -D -)
    body="${location:(-3)}"
    if [[ ${body} = '400' ]]; then
        echo "ERROR: The validator was unable to process the file" && exit 1
      elif [[ ${body} = '404' ]]; then
        echo "ERROR: No sample file was provided" && exit 1
      elif [[ ${body} = '302' ]]; then
        echo "PENDING: The file $i was submitted for testing. Processing..."
      else
        echo "ERROR: An unknown error occured" && exit 1
    fi
    # Check the polling URL for the results
    response=$(echo "${location}" | grep -Eo "(http|https)://[a-zA-Z0-9./?=_-]*" | sort | uniq)
    while [[ "$(curl -s -o /dev/null -w "%{http_code}" "${response}")" == "302" ]]; do echo "PENDING: Waiting for the validation if file $i to complete..." && sleep 5; done
    res=$(curl -s -w "%{http_code}" "${response}")
    loc=${res:(-3)}
    if [[ ${loc} = "200" ]]; then
       echo "SUCCESS: File $i passed validation tests"
     elif [[ ${loc} = "502" ]]; then
       echo "ERROR: File $i determined to be invalid." && exit 1
     elif [[ ${loc} = "404" ]]; then
       echo "ERROR: Invalid request ID in polling URL (expired, malformed...)" && exit 1
     else
       echo "ERROR: An unknown error occured" && exit 1
    fi
done

exit 0
