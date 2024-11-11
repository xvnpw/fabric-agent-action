# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 Github action that utilize [fabric patterns](https://github.com/danielmiessler/fabric/tree/main/patterns) in agent fashion. Agents are implemented using [langgraph](https://www.langchain.com/langgraph).

## Usage

### Action inputs

| Name | Description | Default |
| --- | --- | --- |
| `input_file` | **Required** The path to input file that will be passed to fabric. | |
| `output_file` | **Required** The path to output file. Output from fabric will written to that file. | |
| `verbose` | Verbose messages (python logging set to INFO). | false |
| `debug` | Debug messages (python logging set to DEBUG). | false |
| `agent_type` | Type of agent, one of: single_command, react | single_command |
| `agent_provider` | Name of LLM provider for agent, one of: openai, openrouter, anthropic | openai |
| `agent_model` | Name model for agent | gpt-4o |
| `agent_temperature` | Sampling temperature for agent model | 0 |
| `fabric_provider` | Name of LLM provider for fabric, one of: openai, openrouter, anthropic | openai |
| `fabric_model` | Name model for fabric | gpt-4o |
| `fabric_temperature` | Sampling temperature for fabric model | 0 |

### Environment variables

| Name | Description | Default |
| --- | --- | --- |
| OPENAI_API_KEY | OpenAI API Key | |
| OPENROUTER_API_KEY | OpenRouter API Key | |
| ANTHROPIC_API_KEY | Anthropic API Key | |

One of api keys needs to be defined.

## Example usage

Action is not yet implementing getting issue body and comment(s) from GitHub. For that I'm using `actions/github-script`. For writing comment back to original issue I'm using `peter-evans/create-or-update-comment`. Condition `if: contains(github.event.comment.body, '/fabric')` is making sure that workflow is run only when referencing `/fabric`.

In following example I'm referencing action in GHCR docker registry. It's to avoid building docker container each time action is run. But you can also reference action using `uses: xvnpw/fabric-agent-action@vx.y.z`.

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
        uses:  docker://ghcr.io/xvnpw/fabric-agent-action:v0.0.13
        with:
          input_file: "fabric_input.md"
          output_file: "fabric_output.md"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      # create-or-update-comment is used to save output from agent back to original issue
      - name: Add comment
        uses: peter-evans/create-or-update-comment@v4
        with:
          issue-number: ${{ github.event.issue.number }}
          body-path: ${{ github.workspace }}/fabric_output.md
```

## LLM Providers

Currently supporting:
- [OpenAI](https://platform.openai.com/)
- [OpenRouter](https://openrouter.ai/)
- [Anthropic](https://anthropic.com/)