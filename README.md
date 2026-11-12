# AI Video Application

## Overview

AI Video Application is a Python application that uses a LangGraph workflow to
help prepare short-form social videos. The workflow can select or reuse a video
niche, write a script, and turn it into a JSON storyboard. It also scans an
incoming-video folder; when it finds a clip, it generates a caption and can
publish the clip to a Facebook Page.

The project includes a web dashboard for watching workflow events as they run.
The current workflow creates scripts and storyboards, but does not automatically
render a video from them. Video clips to caption and publish must be supplied in
`videos/incoming/`.

## Requirements

- Python 3.11 or later
- Internet access for model calls and niche search
- A [Groq API key](https://console.groq.com/keys) for the active workflow
- Facebook Page credentials if you want the workflow to publish videos

The dependency list includes `pywin32`, so Windows is the supported setup
described below.

## Set up the environment

Run these commands from the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual-environment activation, allow scripts for the
current terminal session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Create a `.env` file in the repository root (next to `main.py`) and add your
Groq key:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

To enable Facebook publishing, add the Page ID and a Page access token as well:

```dotenv
FB_PAGE_ID=your_facebook_page_id
FB_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
```

Keep `.env` private; it is ignored by Git. Facebook credentials are only needed
when publishing clips. The application publishes videos found in the incoming
folder, so do not add clips there unless you intend to run them through the
captioning and publishing workflow.

## Prepare the ignored files and folders

The following paths are ignored by the repository's `.gitignore`. Unless noted,
all folders belong directly under the repository root:

| Ignored path | Purpose and setup |
| --- | --- |
| `.env` | Create this file at the repository root and add the credentials described above. |
| `.venv/` | Created by the virtual-environment setup commands. |
| `__pycache__/`, `*.pyc` | Python creates these when modules are imported or run; no manual setup is needed. |
| `videos/` | Create `videos/incoming/` at the repository root and put supported video files there (`.mp4`, `.mov`, `.mkv`, or `.webm`). The application creates `videos/processed/` after successful publication and moves published videos there. |
| `scripts/` | Created as needed when the workflow saves generated scripts. `scripts/selected_niche.json` is optional; create it to reuse a niche instead of selecting one. It must contain a JSON object with non-empty `topic` and string `short_description` properties. |
| `storyboards/` | Created when the workflow saves a storyboard. The publisher creates `storyboards/published/` when it moves a matching storyboard after publication. |
| `captions/` | Created when the workflow saves generated captions for incoming videos. |
| `output/` | Used and created by the separate video-generation agent in `app/agents/director_with_video_generation.py`; this agent is not connected to the active graph in `app/graph.py`. |
| `tests/` | Repository-root location for tests. This path is ignored, so new untracked tests placed here will not be included in Git unless the ignore rule is changed. It is not needed to run the application. |

For example, create the incoming-video directory with:

```powershell
New-Item -ItemType Directory -Force .\videos\incoming
```

Copy your input clips into that directory. The other runtime output folders are
created by the application when needed; you do not have to create them manually.

## Run the application

### Run the workflow in the terminal

With the virtual environment active and `.env` configured, run:

```powershell
python main.py
```

The workflow logs its progress in the terminal. When no videos are waiting in
`videos/incoming/`, it can still generate and save a script and storyboard. To
caption and publish a video, put the clip in `videos/incoming/` and configure
the Facebook credentials first. Successfully published clips are moved to
`videos/processed/` to prevent them from being published again.

### Run the web dashboard

Start the dashboard server from the repository root:

```powershell
python web_dashboard.py
```

The server listens on port 8000. Its `/` page loads `dashboard.html` from the
repository root; that file is not present in the current checkout, so restore
that page before opening the dashboard in a browser.

## Project layout

```text
app/
  agents/       LangGraph workflow steps for strategy, scripts, storyboards,
                video scanning, captions, and publishing
  MCP/          MCP server used by the Facebook publishing agent
  graph.py      Active workflow definition
videos/
  incoming/     Input clips to scan, caption, and publish (create this folder)
main.py         Command-line workflow entry point
web_dashboard.py
               FastAPI dashboard entry point (expects root-level dashboard.html)
requirements.txt
               Python dependencies
```

## Troubleshooting

- **Missing `GROQ_API_KEY`:** Confirm `.env` is in the repository root and the
  key is spelled exactly as shown. Restart the process after editing `.env`.
- **Missing Facebook credentials or publishing errors:** Set
  `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN` in `.env`, and confirm the token has
  permission to publish to that Page.
- **No videos detected:** Check that the clips are directly under
  `videos/incoming/` (nested folders are also scanned) and use a supported file
  extension.
