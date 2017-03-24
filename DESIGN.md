## Repository Explorer

### State:

* **app**
  * new
  * refreshing
  * refreshed
* **Tree Group**
* **Tree Container**
* **Project**
  * `LocalOnly` : Actions: View, Upload
  * `OnlineOnly`: Actions: View, Download
  * `BothSynced`: Actions: View
  * `BothLocalNewer`: Actions: View, Upload
  * `BothOnlineNewer`: Actions: View, Upload, Download

## Project Viewer

### State:

* **File**
  * Available
  * Local / Other Project
  * Missing
* **Folder / Group**
  * Expanded / Collapsed

## Downloader


### State:

* Queue state: `[empty/complete]` `running/paused/complete`
* ProjectState: ``






### Notes:

* We should store the queue in the system state. At least the project queue. File queue can be done on the fly