Must get an API key from faceit's developer site: https://docs.faceit.com/getting-started/intro/start-here

Must set an environment variable for your faceit api key, like: `export #FACEIT_API_KEY="YOUR_KEY_HERE"`

If calling from a script, could be something like: `. ./set_env_vars.sh`

Or clobber the line of code getting environment variable and just replace it with a raw string. I'm deving over here and don't want to push my API key to github so I'm doing an environment variable.

Get your set of match IDs and the team's ID and update `get_vetoes.py` update section.

Can acquire your set of match ID's by using this tool: https://github.com/KyleScharnhorst/firefox-ext-faceit-team-match-copier
