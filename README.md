# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 A GitHub action that leverages [fabric patterns](https://github.com/danielmiessler/fabric/tree/main/patterns) through an agent-based approach. Built with [langgraph](https://www.langchain.com/langgraph) for intelligent pattern selection and execution.

## Features

- Seamless integration with GitHub Actions workflow
- Support for multiple LLM providers (OpenAI, OpenRouter, Anthropic)
- Configurable agent types and behavior
- Flexible pattern inclusion/exclusion

## Configuration

### Action Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `input_file` | **Required** Source file containing input and agent instructions | |
| `output_file` | **Required** Destination file for pattern results | |
| `verbose` | Enable INFO level logging | `false` |
| `debug` | Enable DEBUG level logging | `false` |
| `agent_type` | Agent behavior model (`single_command`/`react`) | `single_command` |
| `agent_provider` | LLM provider for agent (`openai`/`openrouter`/`anthropic`) | `openai` |
| `agent_model` | Model name for agent | `gpt-4o` |
| `agent_temperature` | Model creativity (0-1) for agent | `0` |
| `fabric_provider` | Pattern execution LLM provider | `openai` |
| `fabric_model` | Pattern execution LLM model | `gpt-4o` |
| `fabric_temperature` | Pattern execution creativity (0-1) | `0` |
| `fabric-patterns-included` | Patterns to include (comma-separated). **Important**: Required for `gpt-4o` model which supports only 128 tools (Fabric has 175 patterns as of Nov 2024) | |
| `fabric-patterns-excluded` | Patterns to exclude (comma-separated) | |

> **Note**: For models with tool limits (e.g., `gpt-4o` - 128 tools), use pattern filtering options. Consider `claude-3-5-sonnet-20240620` for full pattern access.

### Required Environment Variables

Set one of the following API keys:
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ANTHROPIC_API_KEY`

## Usage Example

This action is flexible on workflow integration. Can be used on issues, push, etc. Use `actions/github-script` for fetching and `peter-evans/create-or-update-comment` for writing back to original issue. The condition `if: contains(github.event.comment.body, '/fabric')` ensures that the workflow runs only when referencing `/fabric`.

The example references the action from GHCR docker registry to avoid rebuilding the container. Alternatively, use `uses: xvnpw/fabric-agent-action@vx.y.z`.

```yaml
name: Fabric Pattern Processing
on:
  issue_comment:
    types: [created, edited]

jobs:
  process_fabric:
    # only comments startsWith /fabric are triggering agent run
    # checks user who commented to avoid abuse
    if: >
      github.event.comment.user.login == github.event.repository.owner.login &&
      startsWith(github.event.comment.body, '/fabric') &&
      !github.event.issue.pull_request
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # github-script is used to:
      # 1. fetch issue body and comment body
      # 2. write comment body to fabric_input.md file
      # 3. write issue body to fabric_input.md file
      - name: Prepare Input
        uses: actions/github-script@v7
        id: prepare-input
        with:
          script: |
            const issue = await github.rest.issues.get({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo
            });

            const comment = await github.rest.issues.getComment({
              comment_id: context.payload.comment.id,
              owner: context.repo.owner,
              repo: context.repo.repo
            });

            const input = `${comment.data.body}\n\nGitHub issue:\n${issue.data.body}`;
            require('fs').writeFileSync('fabric_input.md', input);

            return input;

      - name: Execute Fabric Patterns
        uses: docker://ghcr.io/xvnpw/fabric-agent-action:v0.0.18
        with:
          input_file: fabric_input.md
          output_file: fabric_output.md
          agent_model: gpt-4o # IMPORTANT - gpt-4o only supports 128 patterns - you need to use fabric_patterns_included/fabric_patterns_excluded
          fabric_patterns_included: clean_text,create_stride_threat_model,create_design_document,review_design,refine_design_document,create_threat_scenarios,improve_writing
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      # create-or-update-comment is used to save output from agent back to original issue
      - name: Post Results
        uses: peter-evans/create-or-update-comment@v4
        with:
          issue-number: ${{ github.event.issue.number }}
          body-path: fabric_output.md
```

## Agent Types

Agents select appropriate fabric patterns. If no matching patterns exist, they return "no fabric pattern for this request" and terminate.

### single_command

Executes single pattern selections with direct output:

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
        __start__([<p>__start__</p>]):::first
        assistant(assistant)
        tools(tools)
        __end__([<p>__end__</p>]):::last
        __start__ --> assistant;
        tools --> __end__;
        assistant -.-> tools;
        assistant -.-> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

Example Input:
```markdown
/fabric improve writing

I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I created AI Nutrition-Pro architecture and have been using it since then. What if it's already in LLMs' training data? Testing threat modeling capabilities could give me false results.
```

Example Output:
```markdown
##### (🤖 AI Generated, agent model: gpt-4o, fabric model: gpt-4o)

I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I developed the AI Nutrition-Pro architecture and have been using it since then. What if it's already included in the training data of LLMs? Testing threat modeling capabilities could yield false results.
```

### ReAct

*Coming soon*

## Supported LLM Providers

- [OpenAI](https://platform.openai.com/) - Industry standard
- [OpenRouter](https://openrouter.ai/) - Multi-model gateway
- [Anthropic](https://www.anthropic.com/) - Claude models

## Contributing

Issues and pull requests welcome! Please follow the existing code style and include tests for new features.

## License

MIT
