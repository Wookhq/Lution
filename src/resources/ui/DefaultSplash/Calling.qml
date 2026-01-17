import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import RinUI
import ".."
import "qrc:/resources/QuickPromise/promise.js" as Q
import "qrc:/resources/ui/components"

Window {
    id: window
    visible: true
    width: 700
    height: 400
    property string currentProgress: ""

    Component.onCompleted: {
        Qt.callLater(function () {
            Theme.setTheme(Backend.isDark() ? Theme.mode.Dark : Theme.mode.Light);
        })
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

    Image {
        id: backgroundImage
        anchors.fill: parent
        source: "qrc:/imcalling" 
        fillMode: Image.PreserveAspectCrop

        Rectangle {
            anchors.fill: parent
            color: "#80000000"  
        }
    }

    Row {
        anchors.centerIn: parent
        spacing: 32
        z: 1 
        Column {
            width: 150
            spacing: 8
            anchors.verticalCenter: parent.verticalCenter

            Image {
                width: 150
                height: 150
                source: "qrc:/imcalling"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                id: progressTextItem
                text: currentProgress
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 20
                font.bold: true
                color: "white"  

                Behavior on text {
                    SequentialAnimation {
                        NumberAnimation {
                            target: progressTextItem
                            property: "opacity"
                            to: 0
                            duration: 150
                        }
                        PropertyAction { property: "text" }
                        NumberAnimation {
                            target: progressTextItem
                            property: "opacity"
                            to: 1
                            duration: 150
                        }
                    }
                }
            }

            Button {
                text: qsTr("Cancel")
                width: 200
                height: 52
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 18
                onClicked: Backend.cancel()
            }
        }
    }

    ProgressBar {
        indeterminate: true
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.bottomMargin: 12
        z: 1  
    }
}
