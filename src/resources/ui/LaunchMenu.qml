import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import RinUI
import "pages"
import "qrc:/resources/ui/components"

Window {
    id: window
    visible: true
    width: 700
    height: 400

    Component.onCompleted: Qt.callLater(function () {
        Theme.setTheme(Backend.isDark() ? Theme.mode.Dark : Theme.mode.Light); // note : impl for linux
    })

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
                source: "qrc:/logo"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Preview Text"
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 20
                font.bold: true
            }

            Button {
                text: qsTr("Cancel")

                width: 200
                height: 52

                anchors.horizontalCenter: parent.horizontalCenter

                font.pixelSize: 18

                onClicked : Backend.cancel()
            }

        }
    }

    ProgressBar {
        indeterminate: true
        state: ProgressBar.Running

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.bottomMargin: 12
    }

}
