* removed 'or when new window opened'; it's just a plain every 5 seconds now
* removed clicks overlay
* added 1 minute screenshot sleep
* added disclaimer window at top of screen
* added comboboxes for context selection
* added textfield length limit
* added asynchronous thread "pool"
* added file counters to disclaimer UI
* added conditional shutdown button to finish remaining GPT responses
* made save button on primer window work for any combobox
* prompt strings now saved
* fixed keyboard event duplication
* added clipboard events
* added 'record only' mode for post-activity work
* added session name alongside timestamp
* added text sanitization to primer input fields
* added source RAG artifact correct type checking
* added context length limiter/compression
* added filename and context file whitelist regexes to remove bad stuff
* added empty context default strings
* added delete for empty session folders
* added exit yes/no window
* added minimum primer context length
* added clipboard events delimiting in file output
* added GPT file size limit for RAG upload
* added side-by-side and open-ended mode
* added side-by-side to prompt template
* filtered mouse events so it's only clicks and scrolls
* now only adds event context to prompt if they are not empty
* added file permission error checking when removing empty output folder
* added pause button to disclaimer window
* skipped initial screenshot at beginning of main loop to skip the first empty prompt
* added thread count slider
* added screenshot interval slider
* organized output folders
* made it so context entries in the context files can optionally have timestamps, to save token length
* lazy terminate can now be resumed
* fixed pausing button, now truly stops worker thread execution
* made UI scale "dynamically"
* added multi model selection to primer window
* keyboard events in the prompt are now concatenated to one single string, just like it was typed
* added delay to early primer window termination to account for permission/lock used in cloud folders (hit or miss, depends on Internet speed; not necessary, just makes folders cleaner)
* fixed side by side and open ended in prompt bodies
* added consent window prior to disclaimer
* added keyboard shortcut for pause, ctrl + shift + p
* pausing/resuming changes disclaimer message
* disclaimer window now movable but not outside screen
* disclaimer window changes title when waiting/terminating
* api key entry