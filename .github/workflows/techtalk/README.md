# REG tech talk notifications

The contents of this directory allow custom tech talk notifications to be posted in Slack.

An overview of the steps is as follows:

 - The `techtalk.yaml` file specifies a GitHub Action which runs the Python code in this directory.
    - The action is run every Tuesday morning (so that the page title can be updated to read `Today's Tech Talk`), as well as every Wednesday morning (to update it to point to next week's talk), and every time the repository wiki is updated (i.e. whenever the schedule is changed).

 - The Python code (`techtalk.py`):
    - reads the `Lunchtime-Tech-Talks.md` wiki page (checked out into `wiki/` at the repo root by the action)
    - parses the tech talk Markdown file to obtain the dates, speakers, and titles of each talk
    - gets the next upcoming talk and generates a HTML file at `web/index.html`.

 - This HTML file is never committed to the main branch, but is instead placed on [the `gh-pages` branch](https://github.com/alan-turing-institute/REG-knowledge-sharing/tree/gh-pages).
    - The HTML file contains `meta` tags which are parsed by Slack into a nice format.
    - It does not otherwise contain any actual content; instead, it is configured to redirect to the schedule (in the wiki).

 - In the repository settings, GitHub Pages is set up to publish from the `gh-pages` branch.
    - This means that the HTML file above can be accessed at https://alan-turing-institute.github.io/REG-knowledge-sharing.

 - A Slack workflow is set up to post a message every Tuesday morning, pointing to this link.

## To test locally

- Clone the repo:

      git clone git@github.com:alan-turing-institute/REG-knowledge-sharing.git

- Clone the wiki:

      cd REG-knowledge-sharing
      git clone git@github.com:alan-turing-institute/REG-knowledge-sharing.wiki.git wiki

- Run the script (Python 3 required, no extra dependencies):

      python .github/workflows/techtalk/techtalk.py wiki/Lunchtime-Tech-Talks.md web/index.html

  To test a specific date (e.g. pretend it's the 17th of March):

      python .github/workflows/techtalk/techtalk.py wiki/Lunchtime-Tech-Talks.md web/index.html --date 3 17

## I want to...

**...stop the Slack notifications / edit the message**:

- Edit the workflow on Slack.
  Open the list of members in any channel, then click on 'Integrations' > 'Add a workflow'.

**...change the physical meeting room that will be displayed**:

- Edit the wiki page. The changes will be automatically picked up by the GitHub Action.

**...change the speaker or topic that will be displayed**:

- Edit the wiki page. The changes will be automatically picked up by the GitHub Action.

**...do something else not listed here**:

- If anything about this is unclear (or if the displayed results are not correct), please feel free to drop Penny a message.
