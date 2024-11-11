# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 GitHub action that utilizes [fabric patterns](https://github.com/danielmiessler/fabric/tree/main/patterns) in an agent fashion. Agents are implemented using [langgraph](https://www.langchain.com/langgraph).

## Usage

### Action inputs

| Name | Description | Default |
| --- | --- | --- |
| `input_file` | **Required** The path to input file containing e.g. issue body and request to agent. See [agent types](#agent-types) section below and [example](#example-usage) | |
| `output_file` | **Required** The path to output file. Output from running fabric pattern will be written to that file. | |
| `verbose` | Verbose messages (python logging set to INFO). | false |
| `debug` | Debug messages (python logging set to DEBUG). | false |
| `agent_type` | Type of agent, one of: single_command, react. See [agent types](#agent-types) section below. | single_command |
| `agent_provider` | Name of LLM provider for agent, one of: openai, openrouter, anthropic | openai |
| `agent_model` | Name of model for agent | gpt-4o |
| `agent_temperature` | Sampling temperature for agent model | 0 |
| `fabric_provider` | Name of LLM provider for fabric, one of: openai, openrouter, anthropic | openai |
| `fabric_model` | Name of model for fabric | gpt-4o |
| `fabric_temperature` | Sampling temperature for fabric model | 0 |
| `fabric-tools-included` | Comma-separated list of fabric patterns to include in agent. **Important**: you must use this argument (or `fabric-tools-excluded`) for `gpt-4o` model - it supports only 128 tools. Fabric has, as of Nov 2024, 175 patterns |
| `fabric-tools-excluded` | Comma-separated list of fabric patterns to exclude in agent |

`fabric-tools-included` / `fabric-tools-excluded` - must be used for models like `gpt-4o`. If you want to use all available patterns in fabric, consider `claude-3-5-sonnet-20240620` from Anthropic. Each fabric pattern is transformed into a tool and sent as part of the request to LLM.

### Environment variables

| Name | Description | Default |
| --- | --- | --- |
| OPENAI_API_KEY | OpenAI API Key | |
| OPENROUTER_API_KEY | OpenRouter API Key | |
| ANTHROPIC_API_KEY | Anthropic API Key | |

One of the API keys needs to be defined.

## Example usage

The action is not yet implementing getting issue body and comment(s) from GitHub. For that, I'm using `actions/github-script`. For writing comments back to the original issue, I'm using `peter-evans/create-or-update-comment`. The condition `if: contains(github.event.comment.body, '/fabric')` ensures that the workflow runs only when referencing `/fabric`.

In the following example, I'm referencing the action in the GHCR docker registry to avoid building the docker container each time the action runs. You can also reference the action using `uses: xvnpw/fabric-agent-action@vx.y.z`.

```yml
name: Run fabric-agent-action on issue comment
on:
  issue_comment:
    types:
      - created
      - edited

jobs:
  fabric_agent_action:
    name: Run fabric-agent-action on issue comment
    # only comments startsWith /fabric are triggering agent run
    if: startsWith(github.event.comment.body, '/fabric') && !github.event.issue.pull_request
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
      # github-script is used to:
      # 1. fetch issue body and comment body
      # 2. write comment body to fabric_input.md file
      # 3. write issue body to fabric_input.md file
      - uses: actions/github-script@v7
        id: read-issue-and-comment-script
        with:
          result-encoding: string
          retries: 3
          script: |
            const issue = await github.rest.issues.get({
              issue_number: ${{ github.event.issue.number }},
              owner: "${{ github.repository_owner }}",
              repo: "${{ github.event.repository.name }}",
            });
            const issueBody = issue.data.body;

            const comment = await github.rest.issues.getComment({
              comment_id: ${{ github.event.comment.id }},
              owner: "${{ github.repository_owner }}",
              repo: "${{ github.event.repository.name }}",
            });
            const commentBody = comment.data.body;

            const fabric_input = commentBody + "\n\n" + "GitHub issue:\n" + issueBody;

            const fs = require('fs');
            fs.writeFileSync('${{ github.workspace }}/fabric_input.md', fabric_input, (err) => {
                if (err) throw err;
                console.log('Data written to file');
            });
            return JSON.stringify(fabric_input);
      - name: Run fabric agent action
        uses: docker://ghcr.io/xvnpw/fabric-agent-action:v0.0.15
        with:
          input_file: "fabric_input.md"
          output_file: "fabric_output.md"
          agent_model: "gpt-4o" # default model, IMPORTANT - gpt-4o only supports 128 patterns - you need to use fabric_tools_included/fabric_tools_excluded 
          fabric_tools_included: "clean_text,create_stride_threat_model,create_design_document,review_design,refine_design_document,create_threat_scenarios,improve_writing"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      # create-or-update-comment is used to save output from agent back to original issue
      - name: Add comment
        uses: peter-evans/create-or-update-comment@v4
        with:
          issue-number: ${{ github.event.issue.number }}
          body-path: ${{ github.workspace }}/fabric_output.md
```

## Agent types

Agent decides what fabric pattern to pick. If there is not matching patterns it will return "no fabric pattern for this request" and finish.

### `single_command`

`single_command` is a simple agent that executes one tool and returns output.

**input_file** content. In [example](#example-usage) above input file has value: `commentBody + "\n\n" + "GitHub issue:\n" + issueBody;`.

Example:

```markdown
/fabric improve writing

I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I created AI Nutrition-Pro architecture and have been using it since then. What if it's already in LLMs' training data? Testing threat modeling capabilities could give me false results.

I developed several prompts to assist with the challenging task of creating design documents. I implemented these as Fabric patterns for everyone's benefit. If you're unfamiliar with Fabric - it's an excellent CLI tool created by Daniel Miessler.
```

### `react`

Not implemented

## LLM Providers

Currently supporting:
- [OpenAI](https://platform.openai.com/)
- [OpenRouter](https://openrouter.ai/)
- [Anthropic](https://www.anthropic.com/)
