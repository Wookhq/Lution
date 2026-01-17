import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Clip {
    id: root
    width: 520
    height: 200

    // Clip / Frame styling
    radius: 15
    borderWidth: 1
    borderColor: Theme.currentTheme.colors.controlBorderColor
    color: Theme.getTheme() === "Light" ? "#f6f6f6" : "#1e1e1e"
    highlighted: hovered

    // Data
    property string title: qsTr("Example Mod")
    property string desc: qsTr("Placeholder description text goes here.")
    property string creator: qsTr("Unknown")
    property string img: "qrc:/placeholder"
    property string modId: "Unknown"

    onClicked: {
        // Card click behavior
        console.log("Open mod:", modId)
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 14

        // ───────── LEFT (TEXT) ─────────
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 6

            Text {
                text: root.title
                font.pixelSize: 18
                font.weight: Font.Medium
                color: Theme.getTheme() === "Light" ? "black" : "white"
                elide: Text.ElideRight
                maximumLineCount: 1
                Layout.fillWidth: true
            }

            Text {
                text: root.desc
                font.pixelSize: 14
                wrapMode: Text.WordWrap
                color: Theme.getTheme() === "Light" ? "#444" : "#ccc"
                opacity: 0.85
                Layout.fillWidth: true
            }

            Item { Layout.fillHeight: true }
        }

        // ───────── RIGHT (IMAGE) ─────────
        Item {
            Layout.preferredWidth: 160
            Layout.fillHeight: true

            Rectangle {
                anchors.fill: parent
                radius: 10
                color: Theme.getTheme() === "Light" ? "#eaeaea" : "#2a2a2a"
                clip: true

                Image {
                    anchors.fill: parent
                    source: root.img
                    fillMode: Image.PreserveAspectCrop
                    smooth: true
                }
            }
        }
    }

    // Optional hover affordance
    HoverHandler {
        cursorShape: Qt.PointingHandCursor
    }
}
