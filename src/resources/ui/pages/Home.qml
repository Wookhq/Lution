import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

// the css nerds will love this

FluentPage {
    id: root
    title: "Home"

    property string name: Backend.getName()
    property var titles: [
        qsTr("%1").arg(name),
        qsTr("yo %1").arg(name),
        qsTr("never kill your self"),
        qsTr("%1, right?").arg(name), qsTr("is %1 your name").arg(name),
        qsTr("%1 returns!").arg(name),
        qsTr("must have been the wind"),
        "👋",
        "%1, 👋".arg(name)
        ]

    function getRandomTitles() {
        return titles[Math.floor(Math.random() * titles.length)]
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 40

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 80

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 8

                Text {
                    text: getRandomTitles()
                    font.pixelSize: 24
                    font.weight: Font.Light
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: qsTr("Let's get started!")
                    font.pixelSize: 36
                    font.weight: Font.Bold
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 320
            spacing: 24

            Clip {
                Layout.fillWidth: true
                Layout.preferredHeight: 320
                backgroundColor: Theme.currentTheme.colors.controlColor
                radius: 8
                borderColor: Theme.currentTheme.colors.controlBorderColor
                borderWidth: 1

                onClicked: window.navigationView.push(
                    Qt.resolvedUrl("Mods.qml")
                )


                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 16

                    Icon {
                        name: "ic_fluent_box_edit_20_regular"
                        width: 96
                        height: 96
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: qsTr("Mods")
                        font.pixelSize: 20
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        Layout.fillWidth: true
                    }

                    Text {
                        text: qsTr("Start modding stuff inside Sober/Roblox!")
                        font.pixelSize: 14
                        opacity: 0.75
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Clip {
                Layout.fillWidth: true
                Layout.preferredHeight: 320
                backgroundColor: Theme.currentTheme.colors.controlColor
                radius: 8
                borderColor: Theme.currentTheme.colors.controlBorderColor
                borderWidth: 1

                onClicked: window.navigationView.push(
                    Qt.resolvedUrl("MarketplaceTest.qml") // for now
                )

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 16

                    Icon {
                        name: "ic_fluent_building_shop_20_regular"
                        width: 96
                        height: 96
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: qsTr("Marketplace")
                        font.pixelSize: 20
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        Layout.fillWidth: true
                    }

                    Text {
                        text: qsTr("If you not want to find mods, Let's explore the marketplace!")
                        font.pixelSize: 14
                        opacity: 0.75
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Clip {
                Layout.fillWidth: true
                Layout.preferredHeight: 320
                backgroundColor: Theme.currentTheme.colors.controlColor
                radius: 8
                borderColor: Theme.currentTheme.colors.controlBorderColor
                borderWidth: 1

                onClicked: window.navigationView.push(
                    Qt.resolvedUrl("Settings.qml")
                )

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 16

                    Icon {
                        name: "ic_fluent_settings_cog_multiple_20_regular"
                        width: 96
                        height: 96
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: qsTr("Settings")
                        font.pixelSize: 20
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        Layout.fillWidth: true
                    }

                    Text {
                        text: qsTr("Customize Chroma and preferences")
                        font.pixelSize: 14
                        opacity: 0.75
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
