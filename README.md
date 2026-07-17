# Yoinks

Yoinks is a TUI based application used for downloading videos from common pages such as youtube, instagram, twitter and as many more as i can care to implement

### Goals

- Yoinks should be simple to use - paste link, download
- The download workflow should be as following:
    - Start yoinks
    - Input link in already focused input field (just paste command)
    - Yoinks fetches important information for download (available resolutions, subtitles...)
    - Options, Video title and all important information is shown with defaults selected
    - User can either change these settings or just press enter on the already focused download button for downloading the video with the set settings
- Yoinks should be easily extanable to work for more websites
- Yoinks should look minimalistic
- Following settings should be supported:
    - [ ] Set download resolution
    - [ ] Set different download dir
    - [ ] Download default subtitles
    - [ ] Set name for downloaded video
    - [ ] Optional: Download specific part of video


### Used technology

- Python main language
- Textual as TUI package
- Pyinstaller to compile to .exe