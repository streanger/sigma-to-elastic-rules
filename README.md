# sigma_to_elastic_rules
wrapper for uncoder.io for sigma to elastic rules convertion

## related projects/websites

- https://github.com/SigmaHQ/sigma
- https://uncoder.io/

## requirements

`pip install requests termcolor`

## usage

- specify directory with sigma rules (with .yml extension) in rules_directory_name variable
- run script with `python sigma_to_elastic.py`
- converted rules are stored in {rules_directory_name}.json file
