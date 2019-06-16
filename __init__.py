from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import * 
from . import rpc
import time

# Connect
client_id = '583084701510533126'
# Error prevent
connected = True
try:
    rpc_obj = rpc.DiscordIpcClient.for_platform(client_id)
except:
    connected = False
    pass

# Global vars
dueMessage = ""
skipEdit = 0
skipAnswer = 0

# Start time
start_time = round(time.time())

def update(state, details, pic):
    activity = {
            "state": state,
            "details": details,
            "timestamps": {
                "start": start_time
            },
            "assets": {
                "small_text": "Flashcards",
                "small_image": pic,
                "large_text": "Anki",
                "large_image": "anki"
            }
        }

    # send to server:
    rpc_obj.set_activity(activity)

def dueToday():
    # Reset
    global dueMessage
    dueCount = 0

    # Loop loop
    for i in mw.col.sched.deckDueTree():
        name, did, due, lrn, new, children = i
        dueCount += due + lrn + new

    # Correct cards
    if dueCount == 0:
        dueMessage = "No cards left"
    elif dueCount == 1:
        dueMessage = "(" + str(dueCount) + " card left)"
    else:
        dueMessage = "(" + str(dueCount) + " cards left)"        



# Status update

def onState(state, oldState):
    global skipEdit

    # Check if connected
    if connected:
        # Update numbe due
        dueToday()

        # debug for states
        #showInfo(state + ", " + oldState)

        # Check states:
        if state == "deckBrowser":
            update(dueMessage, "Chilling in the menus", "zzz")
        if state == "review":
            update(dueMessage, "Daily reviews", "tick-dark")
        if state == "browse":
            skipEdit = 1
            update(dueMessage, "Browsing decks", "search")
        if state == "edit":
            update(dueMessage, "Adding cards", "ellipsis-dark")



##### Simulated states
## onBrowse --> when loading browser menu
#
def onBrowse(x):
    onState("browse", "dummy")
#
#
## onEdit --> when loading editor
#
def onEditor(x, y):
    global skipEdit

    # if skipEdit 1, opening browse
    if skipEdit == 0:
        onState("edit", "dummy")

    # reset
    skipEdit = 0
#
#
## onAnswer --> new answer (update cards left)
#
def onAnswer():
    global skipAnswer
    
    # Skip every 3 cards, unneccesary load
    if skipAnswer >= 2:
        onState("review", "review")
        skipAnswer = 0
    skipAnswer += 1



##### Adding Hooks
# afterStateChange --> base states
# browser.setupMenus --> loading browser
# setupEditorShortcuts --> editor (in browser and add)
# showAnswer --> new answer
# AddCards.onHistory --> opening browser via Add Cards
# (Note: Decided to remove last one since obsolete)
#
addHook("afterStateChange", onState)
addHook("browser.setupMenus", onBrowse)
addHook("setupEditorShortcuts", onEditor)
addHook("showAnswer", onAnswer)
#addHook("AddCards.onHistory", onEditor)
