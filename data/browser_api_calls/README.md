# Network Traffic Directory

This directory contains files and scripts related to capturing, analyzing, and processing network traffic for LinkedIn scraping purposes.

## Contents

- **\*.har Files**
    Exported via chrome dev tools, describe the network activity from a website during the exported session. Helpful in finding out what parameters are allowed
    by an undocumented api

- **\*.sh Files **
    Example code used to extract data from the har files.

- **\*.json Files**
    Contain full urls or extracted parameters from those urls. The data there-in are pulled from .har files using the code in the .sh files.

- *Honorable mention*: Some of the parsing and analysis of these files is performed using utility functions in `pipeline/analytics/gql_utils`. These functions help decode, normalize, and analyze the url GraphQL queries  and responses found in the captured network traffic.
