import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

Clip {
    id: root

    property string title: ""
    property string description: ""
    property string iconName: ""

    signal activated()

    Layout.fillWidth: true
    Layout.preferredHeight: 100

    backgroundColor: Theme.currentTheme.colors.controlColor
    radius: 5
    borderColor: Theme.currentTheme.colors.controlBorderColor
    borderWidth: 1

    onClicked: root.activated()

    RowLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Icon {
            name: root.iconName
            width: 50
            height: 50
        }

        ColumnLayout {
            spacing: 4
            Layout.fillWidth: true

            Text {
                text: root.title
                font.pixelSize: 16
                font.weight: Font.Medium
                elide: Text.ElideRight
            }

            Text {
                text: root.description
                font.pixelSize: 12
                opacity: 0.7
                wrapMode: Text.WordWrap
            }
        }
    }
}
