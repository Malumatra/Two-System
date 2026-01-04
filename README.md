# Two-System

1. Core Architecture: The Two-Agent System

The system must support two distinct agent "modes" or "personas" with unique system prompts and responsibilities. It is being built for a locally run small 20B parameter LLM, so everything must be spoon-fed to it for it to run efficiently. The system prompts must be carefully crafted to accommodate the locally run LM Studio model. 

Initializer Agent Mode:

Trigger: Runs only on the very first session/context window.

Responsibility: Decomposes the high-level user prompt into a granular feature list.

Output Artifacts: Generates the initial file structure, init.sh, feature_list.json, and progress.txt.

Git Initialization: Performs the git init and the first commit.

Coding Agent Mode:

Trigger: Runs on all subsequent sessions.

Responsibility: Reads the state, picks one incomplete feature, implements it, tests it, and commits changes.

Context Strategy: Uses context compaction (summarization) to keep the window manageable, but relies primarily on external files (logs/specs) for memory.

2. State & Context Management (The "External Memory")

Since the context window resets, the harness must enforce the use of persistent files to bridge the gap between sessions.

Structured Feature Registry (feature_list.json):

JSON Schema Enforcement: Must use JSON (not Markdown) to prevent parsing errors.

Status Tracking: Fields for category, description, steps, and passes (boolean).

Default State: All features must default to passes: false upon initialization.

Write Protection: The harness should instruct the agent that it is unacceptable to remove tests, only update their status.

Persistent Progress Log (progress.txt):

Append-Only Log: A running diary where the agent summarizes what it did in natural language for the next iteration of itself.

Version Control Integration (Git):

Automated Commits: The harness must prompt/force a git commit after every session or successful feature implementation.

Revert Capability: The agent must have access to git log and git checkout to undo changes if it breaks the build.

3. The "Get Bearings" Routine (Session Bootstrap)

To prevent the agent from hallucinating the project state, the harness must inject a specific sequence of actions at the start of every new context window.

Auto-Injected Context: Before the agent starts "thinking," the harness should automatically run:

pwd (Confirm directory).

read feature_list.json (Find the next priority).

read claude-progress.txt (See what the previous agent did).

git log --oneline -20 (Review recent code changes).

Environment Wake-up (init.sh):

A standardized script created by the Initializer that starts development servers, databases, or build processes so the environment is "live" immediately.

4. Execution & Tooling

The agent needs specific tools to execute the "Incremental Progress" strategy.

Incremental Task Enforcement:

Prompt Engineering: The system prompt must explicitly forbid "one-shotting" (trying to do everything at once). It must force the agent to select only one failing feature from the JSON list per cycle.

Standardized Toolset:

Bash/Shell Tool: For file manipulation and running scripts.

File Read/Write: For editing code and updating the JSON/TXT state files.

Clean State Exit:

The harness must enforce a "cleanup" phase before the context window closes, ensuring code is linted/compilable and the progress log is updated.

5. Testing & Verification (The "Puppeteer" Layer)

To solve the issue of the agent falsely marking items as "done," the harness requires robust end-to-end testing capabilities.

Browser Automation Tool (MCP):

Integration with a tool like Puppeteer (via Model Context Protocol) to allow the agent to control a headless browser.

Capabilities: Click, type, navigate, and inspect DOM elements.

Visual Verification:

Screenshot Capability: The agent must be able to take screenshots of the web app to verify UI elements (essential for catching CSS bugs or missing components that code analysis misses).

Self-Verification Loop:

Pre-Test: Run the test before coding to confirm the feature fails (red).

Post-Test: Run the test after coding to confirm the feature passes (green).

User Simulation: The prompt must instruct the agent to test "as a human user would" (e.g., actually clicking the button, not just curling the API).

6. Safety & Guardrails

Directory Confinement: Ensure the agent can only read/write files within the specific project directory (sandbox).

Loop Limit: A mechanism to stop the agent if it fails to make progress on a specific feature after 
𝑋
X = 50
 attempts (to prevent infinite token burning).

Summary of User Flow (How it works)

User provides a high-level prompt (e.g., "Build a clone of Trello").

Harness spins up Initializer Agent.

Initializer creates feature_list.json (50+ items), init.sh, and git init.

Harness spins up Coding Agent (Session 1).

Coding Agent reads files, picks "Feature 1: Header Display," codes it, tests it via Puppeteer, updates JSON to true, commits to Git, writes to progress.txt.

Harness clears context.

Harness spins up Coding Agent (Session 2).

Coding Agent reads progress.txt (sees Header is done), picks "Feature 2: Login Button," and repeats.
