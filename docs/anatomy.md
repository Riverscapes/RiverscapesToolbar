---
title: Plugin Anatomy
weight: 3
---

The riverscapes viewer is organized into 3 panels or tabs

## Repository Tab

**Buttons:** 

* **Local Only**: Only show local data. Do not call out to the repo. 
* **Show hidden projects**: This is useful if you want to create a directory structure to put a new project in. This option will show you where every possible project *could* go and give you right-click options to create a path to that folder. 
* **Reload**: Invalidate the cache and re-fetch all project status information from the repository

## Project Tab

**Buttons**:

* **Load**: Load a project from anywhere (even outside the riverscapes folder)
* **Upload: NOT WORKING YET**

## Transfers Tab

**Notes about uploading and downloading**:

* You must click start (for now) to kick off queue processing. 
* When you pause the queue it will complete whatever file it's working on before stopping. This is because I haven't figured out how to gracefully stop transfersin boto3