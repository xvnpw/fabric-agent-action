# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 Github action that utilize [fabric](https://github.com/danielmiessler/fabric) as agent to perform action with LLMs

## Usage

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
    if: contains(github.event.comment.body, '/fabric') && ${{ !github.event.issue.pull_request }}
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
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
      - name: Generate user story security acceptance criteria
        uses:  docker://ghcr.io/xvnpw/fabric-agent-action:v0.0.11
        with:
          input_file: "fabric_input.md"
          output_file: "fabric_output.md"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Add comment
        uses: peter-evans/create-or-update-comment@v4
        with:
          issue-number: ${{ github.event.issue.number }}
          body-path: ${{ github.workspace }}/fabric_output.md
```