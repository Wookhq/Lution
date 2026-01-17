import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

Clip {
    id: root

    property string title: ""
    property string description: ""
    property string iconName: ""

    signal activated

    Layout.fillWidth: true
    Layout.preferredHeight: 120

    backgroundColor: Theme.currentTheme.colors.controlColor
    radius: 8
    borderColor: Theme.currentTheme.colors.controlBorderColor
    borderWidth: 1

    onClicked: root.activated()

    RowLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        Icon {
            name: root.iconName
            width: 72
            height: 72
            Layout.alignment: Qt.AlignVCenter
        }

        ColumnLayout {
            spacing: 6
            Layout.fillWidth: true

            Text {
                text: root.title
                font.pixelSize: 16
                font.weight: Font.Medium
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            Text {
                text: root.description
                font.pixelSize: 13
                opacity: 0.75
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }
        }
    }
}
