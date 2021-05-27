# Message Automation for the smoking study
This project automates parts of generating hundreds of text messages (SMS) sent
to smoking study participants, receiving messages responding to interventions,
and deleting scheduled messages that are not needed any more.

## Endpoints
### /
Generate the text messages for a given participant.

Enter the participant ID, then press the "Generate messages"
button. If successful, CSV file with all the messages to be sent to this
participant is available to download.

The participant ID must be in the form `ASHnnn` where n is a number.
For example, ASH004 or ASH666 are valid participant IDs. 

Generating messages takes about 4 minutes because the site has to go to REDCap
to get the participant information, such as the participant's most important
values, their phone number, and the times it is appropriate to text.
Then it has to use Apptoto to generate 252 text messages for the intervention,
56 messages asking for number of cigarettes smoked each day of the
intervention, and 12 messages for the daily diary sessions 2, 3, and 4.

### /diary
Generate the daily diary messages and quit date boosters for a given participant.

Use this endpoint after Session 0, preferable the day after, but before Session 1.

Enter the participant ID, then press the "Create daily diary"
button. If successful, a success message is displayed.

The participant ID must be in the form `ASHnnn` where n is a number.
For example, ASH004 or ASH666 are valid participant IDs. 

Generating these messages takes only a few seconds.

### /task
Gets the input files for the values affirmation task, for a given participant.

Enter the participant ID, then press the "Generate value task input"
button. If successful, a ZIP file with all the input files for the value
affirmation task is available to download.

This endpoint goes to REDcap, gets the participants most-highly valued value
and least-highly rated value, and creates input files based on those values.

### /delete
Delete messages scheduled to be sent, for a given participant.

Enter the participant ID, then press the "Delete messages" button.

This endpoint deletes messages from the current day, going forward, so
participants who leave the study are not receiving unwanted texts.

### /count/\<participant_id\>
Get cigarette count responses from participants.

This endpoint is a REST API endpoint, responding to GET, where <participant_id>
is replaced with a valid participant ID. So, it would be accessed at 
https://message-automation.azurewebsites.net/count/ASH999, for example.

This endpoint returns all the text message responses from the participant, and
the time they responded. These responses are supposed to be the number of
cigarettes smoked that day.

This is a REST API endpoint to make it easier to script, and get the responses from multiple participants which can then be associated with other data from the study.