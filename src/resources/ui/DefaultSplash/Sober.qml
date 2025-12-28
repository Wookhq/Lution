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

    property string currentProgress: ""

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#eeffff" }
            GradientStop { position: 1.0; color: "#98dfc2" }
        }
    }

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

    Row {
        anchors.centerIn: parent
        spacing: 32

        Column {
            width: 150
            spacing: 8
            anchors.verticalCenter: parent.verticalCenter

            Image {
                width: 150
                height: 150
                source: "qrc:/sober"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                id: progressTextItem
                text: currentProgress
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 20
                font.bold: true
                color: "#2c5f4f"

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

            Rectangle {
                width: 200
                height: 52
                radius: width * 0.15
                anchors.horizontalCenter: parent.horizontalCenter
                color: cancelButton.pressed ? "#7bc4ac" : (cancelButton.hovered ? "#88d4b8" : "#98dfc2")

                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

                Text {
                    text: qsTr("Cancel")
                    anchors.centerIn: parent
                    font.pixelSize: 18
                    font.bold: true
                    color: "#ffffff"
                }

                MouseArea {
                    id: cancelButton
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    property bool hovered: containsMouse

                    onClicked: Backend.cancel()
                }
            }
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.bottomMargin: 12
        height: 4
        radius: 2
        color: "#d0f0e8"

        Rectangle {
            id: progressIndicator
            height: parent.height
            width: parent.width * 0.3
            radius: parent.radius
            color: "#98dfc2"

            SequentialAnimation on x {
                loops: Animation.Infinite
                running: true
                NumberAnimation {
                    from: -progressIndicator.width
                    to: progressIndicator.parent.width
                    duration: 1500
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }
}
