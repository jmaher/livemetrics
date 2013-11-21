/* -*- Mode: C++; tab-width: 2; indent-tabs-mode: nil; c-basic-offset: 2; -*- */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

try {
  if (Cc === undefined) {
    var Cc = Components.classes;
    var Ci = Components.interfaces;
    var Cu = Components.utils;
  }
}
catch (ex) {
  dump(ex);
}

Cu.import("resource://gre/modules/osfile.jsm");
Cu.import("resource://gre/modules/Task.jsm");
Cu.import("resource://gre/modules/Services.jsm");

var LogModule;
try {
  Cu.import("resource://gre/modules/Log.jsm");
  LogModule = Log;
}
catch(ex) {
  // In Firefox < 27, it is a service:
  // See https://bugzilla.mozilla.org/show_bug.cgi?id=451283.
  Cu.import("resource://services-common/log4moz.js");
  LogModule = Log4Moz;
}

var collection = [];
var events = {};
var logger = null;

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
    try {
      Cu.startMeasuring();
    } catch(ex) {
       dump("WARNING: unable to startMeasuring on the JS Engine, this build probably doesn't support it\n");
    }
    collection.push(new Date().getTime() + " Starting Collector: " + win.location);
  }


  win.collectorLog = function (msg) {
    collection.push(new Date().getTime() + " User Message: " + msg);
  }

  win.collectorReset = function () {
    // Reset the recording module, issues a stop
    win.collectorStop();
    collection = [];

    var filename = null;
    try {
      var prefs = Cc['@mozilla.org/preferences-service;1']
        .getService(Ci.nsIPrefBranch2);
      var filename = prefs.getCharPref('mfl.logfile');
    } catch (ex) {} //pref does not exist
    logger = initialize_logger(filename);
  }

  win.collectorStop = function () {
    // Stop the recording module
    try {
      let jsval = Cu.getCurrentMeasurements();
      collection.push("JS parsing time: " + jsval.parseTime);
    } catch(ex) {}
    for (event in events) {
      collection.push(events[event] + " " + event);
    }
    collection.push(new Date().getTime() + " Terminating Collector");
  }

  win.collectorDump = function () {
    // print out information
    for (var line in collection) {
      logger.info(collection[line]);
    }
  }

  win.collectorGC = function () {
    // do a gc/cc
    aWindow.QueryInterface(Ci.nsIInterfaceRequestor)
          .getInterface(Ci.nsIDOMWindowUtils)
          .garbageCollect();
  }
}


/** Init the file logger with the absolute path to the file.
    It will create and append if the file already exists **/

var formatter = {
 format: function format(message) {
    return message.loggerName + '\t' +
    message.levelDesc + '\t' +
    message.message + '\n';
  }
};


// XXX: bc - monkey patched to change open to not truncate.
LogModule.FileAppender.prototype._openFile = (function () {
  return Task.spawn(function _openFile() {
      try {
        this._file = yield OS.File.open(this._path,
                                        {truncate: false, write: true});
      } catch (err) {
        if (err instanceof OS.File.Error) {
          this._file = null;
        } else {
          throw err;
        }
      }
    }.bind(this));
  });

function initialize_logger(path) {
  var logger = LogModule.repository.getLogger('collector');
  var dumpAppender = new LogModule.DumpAppender(formatter);
  var consoleAppender = new LogModule.ConsoleAppender(formatter);
  logger.addAppender(dumpAppender);
  logger.addAppender(consoleAppender);
  if (path) {
    var fileAppender = new LogModule.FileAppender(path, formatter);
    logger.addAppender(fileAppender);
  }
  return logger;
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

Services.obs.addObserver(function observer(aSubject, aTopic) {
  Services.obs.removeObserver(observer, aTopic);
  events['browser-delayed-startup-finished'] = new Date().getTime()
}, "browser-delayed-startup-finished", false);

