import requests
from urllib.parse import urlparse

import markdown


def convert_readme_to_html_docs(
    text,
    remove_first_heading=True,
    convert_mermaid_diagrams=True,
    exclude_sections=None,
):
    """Take an application's README file and parse it for display in HTML documentation.

    Options:

    remove_first_heading: removes any first level headings ("#")
    convert_mermaid_diagrams: change ```mermaid``` blocks into HTML <div>s
    exclude_sections: Remove sections with headings in the list <exclude_sections>.
    """
    parsed_text_lines = []
    in_mermaid_diagram = False
    in_excluded_section = False
    in_excluded_section_level = None
    for line in text.split("\n"):
        if remove_first_heading:
            if line.startswith("# "):
                continue  # remove first heading
            elif line.startswith("##"):
                line = line[1:]  # reduce headings by 1
        if convert_mermaid_diagrams:
            if line.startswith("```mermaid"):  # convert mermaid diagrams to divs
                line = '<div class="mermaid">'
                in_mermaid_diagram = True
            elif line.startswith("```") and in_mermaid_diagram:
                line = "</div>"
                in_mermaid_diagram = False
        if exclude_sections:
            if line.startswith("#"):
                level = line.count("#")
                heading = line.lstrip("# ")
                if in_excluded_section:
                    if level <= in_excluded_section_level:
                        in_excluded_section = False
                        in_excluded_section_level = None
                if heading in exclude_sections:
                    in_excluded_section = True
                    in_excluded_section_level = level
            if in_excluded_section:
                continue
        parsed_text_lines.append(line)
    parsed_text = "\n".join(parsed_text_lines)
    return markdown.markdown(
        parsed_text, extensions=["codehilite", "fenced_code", "toc", "tables"]
    )


def get_api_server_url_from_request(request, scheme="http"):
    """Return the api server url given an instance of Request, <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Example returns:
     - http://localhost/v1/
     - https://service.srcdev.skao.int/api/v1

    Note:
      - request.scope.get('root_path') returns either e.g. /v1 or /api/v1 (if proxied)
      - request.base_url returns the full path up to and including the proxy base path (e.g. api)
      - request.app.url_path_for(function_name) returns the (sub)application path for a given function name
        (function_name)
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(
        scheme=scheme, path="{}".format(request.scope.get("root_path"))
    ).geturl()


def get_base_url_from_request(request, scheme="http"):
    """Return the base url given an instance of Request, <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Example returns:
     - http://localhost
     - https://service.srcdev.skao.int/api
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(scheme=scheme).geturl()


def get_url_for_app_from_request(function_name, request, scheme="http"):
    """Return an url for a particular (sub)application's function name, <function_name>, given an instance of Request,
    <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Examples:
     - on localhost, function_name="add_site": http://localhost/v1/www/sites/add
     - in production, function_name="add_site": https://service.srcdev.skao.int/api/v1/www/sites/add

    Note:
      - request.scope.get('root_path') returns either e.g. /v1 or /api/v1 (if proxied)
      - request.base_url returns the full path up to and including the proxy base path (e.g. api)
      - request.app.url_path_for(function_name) returns the (sub)application path for a given function name
        (function_name)
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(
        scheme=scheme,
        path="{}{}".format(
            request.scope.get("root_path"), request.app.url_path_for(function_name)
        ),
    ).geturl()
