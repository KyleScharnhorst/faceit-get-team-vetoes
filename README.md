# Summary

Must get an API key from faceit's developer site: https://docs.faceit.com/getting-started/intro/start-here

Must set an environment variable for your faceit api key, like: `export #FACEIT_API_KEY="YOUR_KEY_HERE"`

If calling from a script, could be something like: `. ./set_env_vars.sh`

Or clobber the line of code getting environment variable and 
just replace it with a raw string. I'm deving over here and don't 
want to push my API key to github so I'm doing an environment variable.

Update the `config.json` file with the team ID and matches. 
Can provide multiple sets of matches in the config. 
Can be useful if you want to include a previous season and the current season.

# Config Explained
`team_id`: The ID of the team on Faceit. 
Can be acquired from the URL of their team's page. 

Given: https://www.faceit.com/en/teams/73d28e6f-13a5-4d16-afef-4ba6572d5849/leagues

Their team ID is: 73d28e6f-13a5-4d16-afef-4ba6572d5849

`seasons`: Provide a list matches. Can provide many lists of matches.
Each list of matches can be acquired using the Firefox extension:
https://github.com/KyleScharnhorst/firefox-ext-faceit-team-match-copier

`time_between_requests`: If you're worried about being timed out by Faceit's API,
then you can adjust this value to be higher. Ultimately dictates the time between
requests to the faceit API. where 0.1 would be 1/10 of a second between requests.

`default_language`: There are scenarios where we may have to print the URL
to the user, Faceit's API returns us incomplete links and we have to put the
default language back into the URL. You can see what your default language
value is by viewing a faceit link. Given:
https://www.faceit.com/en/teams/73d28e6f-13a5-4d16-afef-4ba6572d5849/leagues

Your default langauge would be 'en'