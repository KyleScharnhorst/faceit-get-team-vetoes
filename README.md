must set an environment variable for your faceit api key

`export #FACEIT_API_KEY="YOUR_KEY_HERE"`
if calling from a script, must be like:
`. ./name_of_script.file_extension`

or clobber the line of code getting environment variable and just replace it with a raw string. I'm deving over here and don't want to push my API key to git so I'm doing an environment variable.
