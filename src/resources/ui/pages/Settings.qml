import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    title: qsTr("Settings")

    Column {
        Layout.fillWidth: true
        spacing: 3
        Text {
            typography: Typography.BodyStrong
            text: qsTr("Appearance")
        }

        SettingCard {
            width: parent.width
            title: qsTr("App Theme")
            description: qsTr("Select which app theme to display")
            icon.name: "ic_fluent_paint_brush_20_regular"

            ComboBox {
                property var data: [Theme.mode.Light, Theme.mode.Dark, Theme.mode.Auto]
                model: ListModel {
                    ListElement { text: qsTr("Light") }
                    ListElement { text: qsTr("Dark") }
                }
                currentIndex: data.indexOf(Theme.getTheme())
                onCurrentIndexChanged: {
                    Theme.setTheme(data[currentIndex])
                }
            }
        }
    }

    Column {
        Layout.fillWidth: true
        spacing: 3

        Text {
            typography: Typography.BodyStrong
            text: qsTr("Sober")
        }

        SettingCard {
            width: parent.width
            title: qsTr("Sober Path")
            description: qsTr("Adjust the your sober path, leave blank to reset to default")
            icon.name: "ic_fluent_location_20_regular"

            TextArea {
                id: soberPathInput
                placeholderText: qsTr("~/.var/app/org.vinegarhq.Sober")
                width: 200
                Layout.fillWidth: true
                text: Backend.getSoberPath()
                onTextChanged: Backend.setSoberPath(soberPathInput.text)
            }

        }
    }

    Column {
        Layout.fillWidth: true
        spacing: 3
        Text {
            typography: Typography.BodyStrong
            text: qsTr("Language")
        }

        SettingCard {
            width: parent.width
            title: qsTr("Display Language")
            description: qsTr("Set your preferred language for Lution")
            icon.name: "ic_fluent_translate_20_regular"

            ComboBox {
                property var data: [Backend.getSystemLanguage(), "en_US", "vi_VN"]
                property bool initialized: false
                model: ListModel {
                    ListElement { text: qsTr("Use System Language") }
                    ListElement { text: "English (US)" }
                    ListElement { text: "Tiếng Việt" }
                }
                Component.onCompleted: {
                    currentIndex = data.indexOf(Backend.getLanguage())
                    initialized = true
                }

                onCurrentIndexChanged: {
                    if (initialized) {
                        Backend.setLanguage(data[currentIndex])
                    }
                }
            }
        }
    }

    Column {
        Layout.fillWidth: true
        spacing: 3
        Text {
            typography: Typography.BodyStrong
            text: qsTr("About")
        }

        SettingExpander {
            property string img: "qrc:/logo"

            icon.source: img
            width: parent.width
            title: qsTr("Lution Chroma")
            description: qsTr("Placeholder")
            icon.size: 28

            content: Text {
                color: Theme.currentTheme.colors.textSecondaryColor
                text: Backend.getVersion()
            }

            SettingItem {
                id: repo
                title: qsTr("Repo")

                TextInput {
                    id: repoUrl
                    readOnly: true
                    text: "https://github.com/wookhq/Lution"
                    wrapMode: TextInput.Wrap
                }
                ToolButton {
                    flat: true
                    icon.name: "ic_fluent_copy_20_regular"
                    onClicked: {
                        Backend.copyToClipboard(repoUrl.text)
                    }
                }
            }
            SettingItem {
                title: qsTr("License")
                description: qsTr("This project is licensed under the MIT license")

                Hyperlink {
                    text: qsTr("MIT License")
                    openUrl: "https://github.com/Wookhq/Lution/blob/main/LICENSE"
                }
            }
        }
    }

    Label {
        text: "notice : this page forked from RinUI's settings page."
        color: Theme.currentTheme.colors.textSecondaryColor
    }
}
