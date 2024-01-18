#!/bin/bash
# Initialise the template API with a new API name.

shopt -s dotglob    # include hidden dot files e.g. .gitlab-ci.yml

# -------
# Functions to convert the inputted API name to the required different string formats.
#
api_name_to_capitalised() {
    local input="$1"
    echo "$input" | awk -F'-' '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1' OFS='-'
}

api_name_to_hyphenated_package_name() {
    local input="$1"
    echo "ska-src-$input-api"
}

api_name_to_hyphenated_service_name() {
  local input="$1"
  echo "$input-api"
}

api_name_to_snakecase_package_name() {
    local input="$1"
    echo "ska-src-$input-api" | sed 's/-/_/g'
}

api_name_to_snakecase() {
  local input="$1"
  echo "$input" | sed 's/-/_/g'
}

api_name_to_upper_camel_case() {
    local input="$1"
    local result=""

    IFS='-' read -ra words <<< "$input"
    for word in "${words[@]}"; do
        result+=$(echo "$word" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}' | sed 's/-//g')
    done

    echo "$result"
}

# Function to render all j2 templates in a directory recursively.
render_templates_in_directory() {
    local directory="$1"
    local template_suffix=".j2"
    local api_name="$2"  # New argument for API name
    for file in "$directory"/*; do
        if [[ -d "$file" ]]; then
            # If directory, recursively call the function with the API name
            render_templates_in_directory "$file" "$api_name"
        elif [[ -f "$file" && "$file" == *"$template_suffix" ]]; then
            # If file has a specific suffix perform templating operations
            render_template "$file" "$api_name"
        fi
    done
}

# Function to render a j2 template substituting variables from the environment.
render_template() {
    local file="$1"
    local api_name="$2"

    filename_without_j2_suffix="${file%.*}"
    echo "Rendering file $(basename $file) as $(basename $filename_without_j2_suffix) (in $(dirname $file))"
    j2 "$file" --undefined --import-env= -o "$filename_without_j2_suffix"

    echo "Removing template file $file"
    rm $file
}

# -------
# Entrypoint
#
# Expects the lowercase, hyphenated api name as the first argument.
#
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <lowercase-hyphenated-api-name>"
    exit 1
fi

root_path=$(realpath "../..")   # this should evaluate to the repository base assuming script location is etc/scripts
parent_path=$(realpath "../../..")   # this should evaluate to the repository parent dir

# Check j2 command is available
command -v j2 >/dev/null 2>&1 || { echo >&2 "Error: j2 is not installed. Exiting."; exit 1; }

# Use the inputted API name to construct required strings to render in templates.
export api_name_hyphenated="$1"                                                                     # some-service

# Export required variables into environment for j2 substitution.
export python_package_name=$(api_name_to_snakecase_package_name "$api_name_hyphenated")             # ska_src_some_service_api
export python_client_module_name=$(api_name_to_snakecase "$api_name_hyphenated")                    # some_service
export python_client_class_name=$(api_name_to_upper_camel_case "$api_name_hyphenated")"Client"      # SomeServiceClient
export helm_chart_name=$(api_name_to_hyphenated_package_name "$api_name_hyphenated")                # ska-src-some-service-api
export chart_core_deployment_prefix=$(api_name_to_hyphenated_package_name "$api_name_hyphenated")   # ska-src-some-service-api
export image_repository_name=$(api_name_to_hyphenated_package_name "$api_name_hyphenated")          # ska-src-some-service-api
export api_image_tag_prefix=$api_name_hyphenated                                                    # some-service
export api_ingress_host_prefix=$api_name_hyphenated                                                 # some-service
export iam_client_name=$(api_name_to_hyphenated_package_name "$api_name_hyphenated")                # ska-src-some-service-api
export iam_client_audience=$(api_name_to_hyphenated_service_name "$api_name_hyphenated")            # some-service-api
export permissions_service_name=$(api_name_to_hyphenated_service_name "$api_name_hyphenated")       # some-service-api
export repository_name=$(api_name_to_hyphenated_package_name "$api_name_hyphenated")                # ska-src-some-service-api
export api_name_hyphenated_and_capitalised=$(api_name_to_capitalised "$api_name_hyphenated")        # Some-Service

export package_path="${parent_path}/$(api_name_to_hyphenated_package_name "$api_name_hyphenated")"
echo "Initialising new API from the template at: $package_path"

# Create new top level directory for new API project
if [ -d "$package_path" ]; then
  echo "Error: Directory already exists: $package_path"
  exit 1
else
  echo "Creating directory: $package_path" 
  cp -r $root_path $package_path
fi

# Remove the placeholder README.md
rm $package_path"/"README.md

# Render all templates in $root_path.
render_templates_in_directory $package_path "$api_name"

# Rename files and directories that have references to the template.
mv $package_path"/bin/ska-src-template" $package_path"/bin/ska-src-"$api_name_hyphenated                                                                              # binary
mv $package_path"/src/ska_src_template_api/client/template.py" $package_path"/src/ska_src_template_api/client/"$(api_name_to_snakecase "$api_name_hyphenated")".py"   # module name of client in source package
mv $package_path"/src/ska_src_template_api" $package_path"/src/"$(api_name_to_snakecase_package_name "$api_name_hyphenated")                                          # source package name
