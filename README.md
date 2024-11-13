# Fabric Agent Action

[![CI](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/xvnpw/fabric-agent-action/actions/workflows/ci.yaml)

🤖 A GitHub Action that utilizes [Fabric Patterns](https://github.com/danielmiessler/fabric/tree/main/patterns) to automate complex workflows through an agent-based approach. Built with [LangGraph](https://www.langchain.com/langgraph), it enables intelligent pattern selection and execution using Large Language Models (LLMs).

## Features

- **Seamless GitHub Actions Integration:** Easily incorporate the action into your existing workflows without additional setup.
- **Multiple LLM Provider Support:** Choose between OpenAI, OpenRouter, or Anthropic based on your preference or availability.
- **Configurable Agent Behavior:** Select agent types (`single_command` or `react`) and customize their behavior to suit your workflow needs.
- **Flexible Pattern Management:** Include or exclude specific Fabric Patterns to optimize performance and adhere to model limitations.

## Setup

You can add the Fabric Agent Action to your workflow by referencing it in your `.yaml` file:

```yaml
- name: Execute Fabric Agent Action
  uses: xvnpw/fabric-agent-action@v0.0.18
  with:
    input_file: path/to/input.md
    output_file: path/to/output.md
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

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
| `agent_preamble` | Preamble that is added to the beginning of output | `##### (🤖 AI Generated)` |
| `fabric_provider` | Pattern execution LLM provider | `openai` |
| `fabric_model` | Pattern execution LLM model | `gpt-4o` |
| `fabric_temperature` | Pattern execution creativity (0-1) | `0` |
| `fabric-patterns-included` | Patterns to include (comma-separated). **Required for models with pattern limits (e.g., `gpt-4o`).** | |
| `fabric-patterns-excluded` | Patterns to exclude (comma-separated) | |

> **Note:** Models like `gpt-4o` have a limit on the number of tools (128), whereas Fabric currently includes 175 patterns (as of November 2024). Use the `fabric_patterns_included` or `fabric_patterns_excluded` inputs to tailor the patterns used. For access to all patterns without tool limits, consider using `claude-3-5-sonnet-20240620`.

You can find the list of available Fabric Patterns [here](https://github.com/danielmiessler/fabric/tree/main/patterns).

### Required Environment Variables

Set one of the following API keys:
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ANTHROPIC_API_KEY`

## Usage Example

This action is flexible on workflow integration. Can be used on issues, push, etc.

### Issue Comments - created, edited

The following is an example of how to integrate the Fabric Agent Action into a GitHub Actions workflow that reacts to issue comments:

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

In this workflow:

- The job runs only when:
  - The comment starts with `/fabric`.
  - The comment author is the repository owner.
  - The issue is not a pull request.
- This prevents unauthorized users from triggering the action, which could lead to excessive API usage or costs.

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

Agent is taking input from user, deciding on pattern selection and again reason about output from pattern:

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
        __start__([<p>__start__</p>]):::first
        assistant(assistant)
        tools(tools)
        __end__([<p>__end__</p>]):::last
        __start__ --> assistant;
        tools --> assistant;
        assistant -.-> tools;
        assistant -.-> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

This is the intuition behind [ReAct](https://react-lm.github.io/):

* `act` - let the model call specific tools (in our case patterns)
* `observe` - pass the tool output back to the model
* `reason` - let the model reason about the tool output to decide what to do next (e.g., call another tool or just respond directly)

Example Input:
```markdown
/fabric clean text and improve writing

I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I created AI Nutrition-Pro architecture and have been using it since then. What if it's already in LLMs' training data? Testing threat modeling capabilities could give me false results.
```

Example Output:
```markdown
##### (🤖 AI Generated, agent model: gpt-4o, fabric model: gpt-4o)

Here is the cleaned and improved version of your text:

Cleaned Text:
"I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I created AI Nutrition-Pro architecture and have been using it since then. What if it's already in LLMs' training data? Testing threat modeling capabilities could give me false results."

Improved Writing:
"I encountered a challenge in creating high-quality design documents for my threat modeling research. About a year and a half ago, I developed the AI Nutrition-Pro architecture and have been using it since then. What if it's already included in the training data of LLMs? Testing threat modeling capabilities could yield false results."
```

## Supported LLM Providers

- [OpenAI](https://platform.openai.com/) - Industry standard
- [OpenRouter](https://openrouter.ai/) - Multi-model gateway
- [Anthropic](https://www.anthropic.com/) - Claude models

## Contributing

Issues and pull requests welcome! Please follow the existing code style and include tests for new features.

## License

This project is licensed under the [MIT License](LICENSE).
