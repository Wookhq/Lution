import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import RinUI

Frame {
    id: root
    width: 340
    height: 220
    padding: 0

    property string title: "Example Mod"
    property string desc: "Placeholder text"
    property string img: "qrc:/placeholder"

    background: Rectangle {
        id: bg
        radius: 15
        border.width: 1
        border.color: Theme.currentTheme.colors.controlBorderColor
        color: "transparent"
        clip: true

        Image {
            id: bgImage
            anchors.fill: parent
            source: root.img
            fillMode: Image.PreserveAspectCrop
            smooth: true
            visible: false
        }

        Rectangle {
            id: mask
            anchors.fill: parent
            radius: bg.radius
            color: "black"
            visible: false
        }

        OpacityMask {
            anchors.fill: parent
            source: bgImage
            maskSource: mask
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 110
            radius: bg.radius
            color: "transparent"

            gradient: Gradient {
                GradientStop { position: 0.0; color: "#00000000" }
                GradientStop { position: 0.4; color: "#80000000" } 
                GradientStop {
                    position: 1.0
                    color: "#cc000000" 
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 6

        Item { Layout.fillHeight: true } 

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            Label {
                text: root.title
                font.pixelSize: 16
                font.weight: Font.Medium
                color: Theme.getTheme() === "Light" ? "black" : "white"
                elide: Text.ElideRight
            }

            Label {
                text: root.desc
                font.pixelSize: 12
                opacity: 0.75
                color: Theme.getTheme() === "Light" ? "#444" : "#ccc"
                elide: Text.ElideRight
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Item { Layout.fillWidth: true }

            Button {
                text: "Download"
                highlighted: true
            }

            Button {
                id: descbutton
                icon.name: "ic_fluent_line_horizontal_3_20_regular"
                highlighted: true
                onClicked: desc.open()
            }
        }

        Flyout {
            id: desc
            parent: descbutton // Positions the flyout relative to myButton
            text: root.desc
        }
    }
}
