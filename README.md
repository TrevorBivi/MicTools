# About
Control playlists, soundboards, voice morphing, live recording/spicing (TODO) and volume levels for an artificial input device. The program is controlled using a serial USB audio mixing controller that can play TTS narrations of actions to the user's headphones for use when VR gaming.
![alt text](https://github.com/TrevorBivi/MicTools/raw/master/images/audio_mixer.jpg)
*An image of the controller.*


NOTE:WIP Recording / splicing is only partially complete. The rest of the modes described may not be mapped the buttons stated yet

#Button Functions
The serial controller has __ different button functions.

`╔══╦══╗╔══╗╔══╦══╗`

`║_1║_2║║M1║║_7║_8║`

`╠══╬══╣╠══╣╠══╬══╣`

`║_3║_4║║M2║║_9║10║`

`╠══╬══╣╠══╣╠══╬══╣`

`║_5║_6║║M3║║11║12║`

`╚╦═╩╦═╝╚══╝╚═╦╩═╦╝`

`-║S1║--------║S2║`

`-╚══╝--------╚══╝`
 
`------[DIAL]`

## Special Buttons
The special buttons never change what they do

**Special Button 1:** Creates a recording that starts 5 seconds before the button was pressed and ends when the button is released. Note: The program stops sending informational audio to the user while the button is pressed (tts narration, output listening, etc...) The 5 seconds before the button is pressed will also record the audio that is being sent to the player.

**Special Button 2:** Make tts narration repeat old actions that were created - to replace with undo?

## Mode Button
Mode buttons select one of 8 modes depending on the buttons pressed. Buttons must be pressed in the order listed to unless otherwise stated. Pressing all the buttons restarts the device.

### Raw editor
_press M1,M2_
This mode is used to perform actions on raw recordings that have been created with the recording button.

**Buttons 1 & 2:** Select the next/previous recording. Pressing both will cause dial to dictate the selected recording.

**Buttons 3:** Toggles dial selecting beginning/ending of where to retrieve audio for a cut recording.

**Button 4:** Plays cut recording to the user

**Button 5:** Sends cut recording to sound board

**Button 6:** Sends cut recording to remix maker

**Button 7:** Normal volume

**Button 8:** Dial selects volume

**Button 9:** Sets cut recording to normal pitch

**Button 10:** Dial selects cut recording pitch

**Button 11:** Sets cut recording to normal speed

**Button 12:** Dial selects cut recording speed

### Recording manager
_press M2, M1_
**Button 1:** Add new soundboard

**Button 2:** Remove selected soundboard

**Button 3 & 4:** Select next/prev soundboard. Pressing both will cause dial to dictate selected soundboard.

**Button 5 & 6:** Preview next/prev cut recording in board. Pressing both will stop playing a preview.

**Button 7:** Add new remix group to board

**Button 8:** Remove selected remix group

**Button 9 & 10:** Next/prev remix group. Pressing both will cause dial to dictate selected remix group.

**Button 11 & 12:** Preview next/prev cut recording in remix group. Pressing both will stop playing a preview.

### Remix Maker
_press M2, M3_
**button 1 & 2:** Next/prev song. Pressing both will cause dial to dictate selected song

**button 3 & 4:** Next/prev cut recording. pressing both will cause dial to select cut recording

**button 5:** Preview cut in song

**button 6:** Add cut to song sources

**button 7:** Normal volume

**button 8:** Dial dictates volume

**button 9:** Normal pitch

**button 10:** Dial dictates pitch

**button 11:** Normal speed

**button 12:** Dial dictates speed

### 
_press M3, M2_