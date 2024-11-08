# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 Github action that utilize [fabric](https://github.com/danielmiessler/fabric) as agent to perform action with LLMs

## Usage

### Inputs

### Action inputs

| Name | Description | Default |
| --- | --- | --- |
| `input_file` | **Required** The path to input file that will be passed to fabric. | |
| `output_file` | **Required** The path to output file. Output from fabric will written to that file. | |
| `verbose` | Verbose messages (python logging set to INFO). | false |
| `debug` | Debug messages (python logging set to DEBUG). | false |
| `agent_provider` | **NOT IMPLEMENTED** | |
| `agent_model` | **NOT IMPLEMENTED** | |
| `agent_temperature` | **NOT IMPLEMENTED** | |
| `fabric_model` | **NOT IMPLEMENTED** | |
| `fabric_temperature` | **NOT IMPLEMENTED** | |

## Example usage

```yml
- name: Run fabric agent
  uses: xvnpw/fabric-agent-action@v0.0.4
  with:
    input_file: "fabric_input.md"
    output_file: "fabric_output.md"
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```