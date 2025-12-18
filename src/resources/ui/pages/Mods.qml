import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: root
    title: "Mods"

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Clip {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                backgroundColor: Theme.currentTheme.colors.controlColor
                radius: 5
                borderColor: Theme.currentTheme.colors.controlBorderColor
                borderWidth: 1

                onClicked: Backend.openModFolder()

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Icon {
                        name: "ic_fluent_folder_20_regular"
                        width: 50
                        height: 50
                    }

                    ColumnLayout {
                        spacing: 4
                        Layout.fillWidth: true

                        Text {
                            text: qsTr("Open Mods Folder")
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                        }

                        Text {
                            text: qsTr("Open the local folder where mods are stored")
                            font.pixelSize: 12
                            opacity: 0.7
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }


            Clip {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                backgroundColor: Theme.currentTheme.colors.controlColor
                radius: 5
                borderColor: Theme.currentTheme.colors.controlBorderColor
                borderWidth: 1

                onClicked: Backend.openInBroswer("https://bloxstraplabs.com/wiki/features/modding/")

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Icon {
                        name: "ic_fluent_book_information_20_regular"
                        width: 50
                        height: 50
                    }

                    ColumnLayout {
                        spacing: 4
                        Layout.fillWidth: true

                        Text {
                            text: qsTr("See how to use mods")
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                        }

                        Text {
                            text: qsTr("Open the bloxstrap's document.")
                            font.pixelSize: 12
                            opacity: 0.7
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }
}
