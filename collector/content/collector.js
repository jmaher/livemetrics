/* -*- Mode: C++; tab-width: 20; indent-tabs-mode: nil; c-basic-offset: 2 -*- */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

try {
  if (Cc === undefined) {
    var Cc = Components.classes;
    var Ci = Components.interfaces;
  }
} catch (ex) {}

var collection = [];

function collectorInit(aWindow) {

  var win = aWindow.wrappedJSObject;

  if (!win) {
    return;
  } 

  if (win.location == '' || win.location == 'about:blank') {
    return;
  }

  win.collectorRecord = function () {
    // Start the recording, will issue a reset as well
    win.collectorReset();
    collection.push(new Date() + " Starting Collector: " + win.location);
  }


  win.collectorReset = function () {
    // Reset the recording module, issues a stop
    win.collectorStop();
    collection = [];

    try {
      var prefs = Components.classes['@mozilla.org/preferences-service;1']
        .getService(Components.interfaces.nsIPrefBranch2);
      var filename = prefs.getCharPref('mfl.logfile');
      MozillaFileLogger.init(filename);
    } catch (ex) {} //pref does not exist
  }

  win.collectorStop = function () {
    // Stop the recording module
    collection.push(new Date() + " Terminating Collector");
  }

  win.collectorDump = function () {
    // print out information
    for (var line in collection) {
      dumpLine(collection[line]);
    }
  }

  win.collectorGC = function () {
    // do a gc/cc
    aWindow.QueryInterface(Components.interfaces.nsIInterfaceRequestor)
          .getInterface(Components.interfaces.nsIDOMWindowUtils)
          .garbageCollect();
  }

  win.dumpLine = function(str) {
    if (MozillaFileLogger)
      MozillaFileLogger.log(str + "\n");
    dump(str);
    dump("\n");
  }
}

function dumpLine(str) {
  if (MozillaFileLogger)
    MozillaFileLogger.log(str + "\n");
  dump(str);
  dump("\n");
}



/** Init the file logger with the absolute path to the file.
    It will create and append if the file already exists **/

var MozillaFileLogger = {};
MozillaFileLogger.init = function(path) {
  var FOSTREAM_CID = "@mozilla.org/network/file-output-stream;1";
  var LF_CID = "@mozilla.org/file/local;1";
  var PR_WRITE_ONLY   = 0x02;
  var PR_CREATE_FILE  = 0x08;
  var PR_APPEND       = 0x10;

  MozillaFileLogger._file = Cc[LF_CID].createInstance(Ci.nsILocalFile);
  MozillaFileLogger._file.initWithPath(path);
  MozillaFileLogger._foStream = Cc[FOSTREAM_CID].createInstance(Ci.nsIFileOutputStream);
  MozillaFileLogger._foStream.init(this._file, PR_WRITE_ONLY | PR_CREATE_FILE | PR_APPEND,
                                   0664, 0);
}

MozillaFileLogger.getLogCallback = function() {

  return function (msg) {
    var data = msg.num + " " + msg.level + " " + msg.info.join(' ') + "\n";
    if (MozillaFileLogger._foStream)
      MozillaFileLogger._foStream.write(data, data.length);

    if (data.indexOf("SimpleTest FINISH") >= 0) {
      MozillaFileLogger.close();
    }
  }
}

// This is only used from chrome space by the reftest harness
MozillaFileLogger.log = function(msg) {
  if (MozillaFileLogger && MozillaFileLogger._foStream) {
    try {
      MozillaFileLogger._foStream.write(msg, msg.length);
    } catch(e) {}
  }
}

MozillaFileLogger.close = function() {
  if(MozillaFileLogger._foStream)
    MozillaFileLogger._foStream.close();
  
  MozillaFileLogger._foStream = null;
  MozillaFileLogger._file = null;
}

// Taken from special powers

// This is a frame script, so it may be running in a content process.
// In any event, it is targeted at a specific "tab", so we listen for
// the DOMWindowCreated event to be notified about content windows
// being created in this context.

function CollectorManager() {
  addEventListener("DOMWindowCreated", this, false);
}

CollectorManager.prototype = {
  handleEvent: function handleEvent(aEvent) {
    var window = aEvent.target.defaultView;
    collectorInit(window);
  }
};

var collectormanager = new CollectorManager();

