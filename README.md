# Schwups

Schwups is a TUI based application used for downloading videos and music from as many common pages as i can care to implement

### Goals

- Schwups should be simple to use - paste link, download
- The download workflow should be as following:
    - Start schwups
    - Input link in already focused input field (just paste command)
    - Schwups fetches important information for download (available resolutions, subtitles...)
    - Options, Video title and all important information is shown with defaults selected
    - User can either change these settings or just press enter on the already focused download button for downloading the video with the set settings
- Schwups should be easily extanable to work for more websites
- Schwups should look minimalistic
- Following settings should be supported:
    - [x] Set download resolution
    - [x] Set different download dir
    - [-] Download default subtitles
    - [x] Set name for downloaded video
    - [ ] Optional: Download specific part of video


### Used technology

- Python main language
- Textual as TUI package
- Pyinstaller to compile to .exe
- ytdlp for downloading yt videos
- ffmpeg for merging video parts

### Default download scripts