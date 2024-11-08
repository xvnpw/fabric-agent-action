# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 Github action that utilize [fabric](https://github.com/danielmiessler/fabric) as agent to perform action with LLMs

## Inputs

### `input_file`

**Required** The path to input file that will be passed to fabric.

### `output_file`

**Required** The path to output file. Output from fabric will written to that file.

## Outputs

## Example usage

```yml
uses: xvnpw/fabric-agent-action@v0.0.1
with:
  input_file: '...'
  output_file: '...'

```