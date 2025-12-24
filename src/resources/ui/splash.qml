import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import RinUI
import "pages"
import "qrc:/resources/ui/components"

Window {
    id: window
    visible: true
    title : "Chroma"
    width: 700
    height: 400

    Component.onCompleted: Qt.callLater(function () {
        Theme.setTheme(Backend.isDark() ? Theme.mode.Dark : Theme.mode.Light); // note : impl for linux
    })

    flags: Qt.Window | Qt.FramelessWindowHint

    Row {
        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.1
        anchors.verticalCenter: parent.verticalCenter
        spacing: 32
        width: parent.width * 0.8
        height: 220

        Column {
            spacing: 8
            width: 150

            Image {
                width: 150
                height: 150
                source: "qrc:/logo"
            }

            Text {
                text: "LChroma"
                horizontalAlignment: Text.AlignHCenter
                width: parent.width
                font.pixelSize: 20
                font.bold: true
            }

            Text {
                text: Backend.getVersion()
                horizontalAlignment: Text.AlignHCenter
                width: parent.width
                font.pixelSize: 14
            }
        }

        Column {
            spacing: 16
            width: parent.width - 150 - 32
            height: parent.height

            BigClip {
                title: qsTr("Launch Sober")
                description: qsTr("Play roblox via sober with Chroma running in the backround.")
                iconName: "ic_fluent_play_20_regular"
                width: parent.width
                height: parent.height / 2 - 8

                onActivated: Backend.launchMenu()
            }

            BigClip {
                title: qsTr("Launch Chroma")
                description: qsTr("Launch Chroma and start customize stuff!")
                iconName: "ic_fluent_wrench_20_regular"
                width: parent.width
                height: parent.height / 2 - 8

                onActivated: Backend.launchChroma()
            }
        }
    }
}
