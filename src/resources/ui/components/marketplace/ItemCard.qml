import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import RinUI

Frame {
    id: root
    width: 500
    height: 200
    padding: 0

    property string title: qsTr("Example Mod")
    property string desc: qsTr("Placeholder text")
    property string creator: qsTr("Unknown")
    property string img: "qrc:/placeholder"
    
    function truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + "...";
    }

    background: Rectangle {
        radius: 15
        border.width: 1
        border.color: Theme.currentTheme.colors.controlBorderColor
        color: "transparent"
        clip: true
    }


    ColumnLayout {
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            margins: 14
        }

        Layout.bottomMargin: 52

        spacing: 6

        Text {
            text: root.truncateText(root.title, 50)
            font.pixelSize: 18
            font.weight: Font.Medium
            color: Theme.getTheme() === "Light" ? "black" : "white"

            maximumLineCount: 1
            wrapMode: Text.NoWrap

            Layout.fillWidth: true
            Layout.maximumHeight: font.pixelSize * 1.4
            clip: true
        }

        Text {
            text: root.truncateText(root.desc, 10)
            font.pixelSize: 14
            opacity: 0.75
            color: Theme.getTheme() === "Light" ? "#444" : "#ccc"

            wrapMode: Text.WordWrap 

            Layout.fillWidth: true
            Layout.preferredHeight: font.pixelSize * 2.6
            Layout.maximumHeight: Layout.preferredHeight
            clip: true
        }
    }


    Row {
        id: buttonBar
        spacing: 8

        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 14
        }

        Button {
            text: "Download"
            highlighted: true
        }

        Button {
            icon.name: "ic_fluent_line_horizontal_3_20_regular"
            highlighted: true
            onClicked: desc.open()
        }
    }


    Flyout {
        id: desc
        text: qsTr(
            "Description: %1\nCreator: %2"
        ).arg(root.desc).arg(root.creator)
    }
}