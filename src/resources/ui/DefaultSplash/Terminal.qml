import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import ".."
import "qrc:/resources/QuickPromise/promise.js" as Q
import "qrc:/resources/ui/components"

Window {
    id: window
    visible: true
    width: 700
    height: 400
    color: "#0a0a0a"

    property string currentProgress: ""

    Component.onCompleted: {
        Qt.callLater(runStartupChecks)
    }

    function runStartupChecks() {
        Q.promise(function(resolve, reject) {
            var onError = function(error) {
                Backend.checksComplete.disconnect(onSuccess)
                Backend.checksError.disconnect(onError)
                reject(error)
            }
            var onSuccess = function(success) {
                Backend.checksComplete.disconnect(onSuccess)
                Backend.checksError.disconnect(onError)
                resolve(success)
            }
            Backend.checksComplete.connect(onSuccess)
            Backend.checksError.connect(onError)
            Backend.startChecks()
        }).then(function(success) {
            if (success) {
                console.log("Startup checks completed successfully")
                currentProgress = "Ready!"
                launchTimer.start()
            } else {
                console.log("Startup checks completed with warnings")
                currentProgress = "Completed with warnings"
            }
        }, function(error) {
            console.error("Startup checks failed:", error)
            currentProgress = "Error: " + error
        })
    }

    Timer {
        id: launchTimer
        interval: 500
        repeat: false
        onTriggered: {
            console.log("Launching main application...")
            Backend.cancel()
        }
    }

    Connections {
        target: Backend
        function onProgressText() {
            currentProgress = Backend.progress
        }
    }

    flags: Qt.Window | Qt.FramelessWindowHint

    // Terminal border
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.color: "#00ff00"
        border.width: 2
    }

    Column {
        anchors.centerIn: parent
        spacing: 20
        width: parent.width - 100

        // ASCII Art Logo
        Text {
            text: "╔═══════════════════════════╗\n" +
                  "║    SYSTEM INITIALIZING    ║\n" +
                  "╚═══════════════════════════╝"
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: "Courier"
            font.pixelSize: 14
            color: "#00ff00"
        }

        // Progress text with terminal styling
        Rectangle {
            width: parent.width
            height: 60
            color: "#1a1a1a"
            border.color: "#00ff00"
            border.width: 1
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                id: progressTextItem
                text: "> " + currentProgress + "_"
                anchors.centerIn: parent
                font.family: "Courier"
                font.pixelSize: 16
                color: "#00ff00"

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    running: true
                    NumberAnimation { to: 1; duration: 500 }
                    NumberAnimation { to: 0.5; duration: 500 }
                }
            }
        }

        // Cancel button with terminal style
        Rectangle {
            width: 200
            height: 40
            color: mouseArea.pressed ? "#003300" : (mouseArea.containsMouse ? "#001a00" : "transparent")
            border.color: "#00ff00"
            border.width: 2
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                text: "[CANCEL]"
                anchors.centerIn: parent
                font.family: "Courier"
                font.pixelSize: 16
                font.bold: true
                color: "#00ff00"
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: Backend.cancel()
            }
        }
    }

    // Terminal-style progress bar
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.bottomMargin: 12
        height: 30
        color: "#1a1a1a"
        border.color: "#00ff00"
        border.width: 1

        Row {
            anchors.centerIn: parent
            spacing: 2
            Repeater {
                model: 40
                Rectangle {
                    width: 12
                    height: 20
                    color: "transparent"

                    Text {
                        anchors.centerIn: parent
                        text: "█"
                        font.family: "Courier"
                        font.pixelSize: 14
                        color: "#00ff00"

                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            NumberAnimation {
                                to: 1
                                duration: 50
                            }
                            PauseAnimation {
                                duration: index * 30
                            }
                            NumberAnimation {
                                to: 0.3
                                duration: 50
                            }
                            PauseAnimation {
                                duration: (40 - index) * 30
                            }
                        }
                    }
                }
            }
        }
    }
}
